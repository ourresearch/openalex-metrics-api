import aiohttp
import asyncio
import os
import time
import random
from datetime import datetime
from math import ceil
from models import Sample, MetricSet, Response
from collections import defaultdict, deque
from app import db
from email.utils import parsedate_to_datetime

from schema import schema, canonical_ids, test_fields, sum_fields

OPENALEX_API_KEY = os.getenv("OPENALEX_API_KEY")

api_endpoint = "https://api.openalex.org/"

prod_results = defaultdict(dict)
walden_results = defaultdict(dict)
matches = defaultdict(dict)
match_rates = defaultdict(dict)
recall = defaultdict(dict)
sum_fields_store = defaultdict(dict)

MAX_REQUESTS_PER_SECOND = 100
rate_limiter = None

class RateLimiter:
    def __init__(self, max_requests_per_second):
        self.max_requests = max_requests_per_second
        self.requests = deque()
        self.semaphore = asyncio.Semaphore(max_requests_per_second)
    
    async def acquire(self):
        """Acquire permission to make a request, respecting rate limits"""
        await self.semaphore.acquire()
        
        current_time = time.time()
        
        # Remove requests older than 1 second
        while self.requests and current_time - self.requests[0] > 1.0:
            self.requests.popleft()
        
        # If we're at the limit, wait until we can make another request
        if len(self.requests) >= self.max_requests:
            sleep_time = 1.0 - (current_time - self.requests[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
                # Clean up old requests again after sleeping
                current_time = time.time()
                while self.requests and current_time - self.requests[0] > 1.0:
                    self.requests.popleft()
        
        # Record this request
        self.requests.append(current_time)
    
    def release(self):
        """Release the semaphore"""
        self.semaphore.release()


async def fetch_all_ids(ids, entity):
    """Fetch IDs from both prod and walden APIs in parallel"""
    global rate_limiter
    if rate_limiter is None:
        rate_limiter = RateLimiter(MAX_REQUESTS_PER_SECOND)
    
    n_groups = ceil(len(ids) / 100)
    
    headers = {'Authorization': f'Bearer {OPENALEX_API_KEY}'}
    
    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for i in range(n_groups):
            id_group = ids[i*100:(i+1)*100]
            tasks.append(fetch_ids(session, id_group, entity, prod_results, is_v2=False))
            tasks.append(fetch_ids(session, id_group, entity, walden_results, is_v2=True))
        
        await asyncio.gather(*tasks)


async def fetch_ids(session, ids, entity, store, is_v2):
    """Fetch IDs from a specific URL using the provided session with rate limiting and retry logic"""
    global rate_limiter
    
    max_retries = 5
    base_delay = 1  # Start with 1 second
    max_delay = 60  # Cap at 60 seconds
    
    for attempt in range(max_retries + 1):
        # Acquire rate limit permission
        await rate_limiter.acquire()
        
        # Extract the part after the last "/" if present, otherwise use the full id
        clean_ids = [id.split("/")[-1] if "/" in id else id for id in ids]
        api_url = f"{api_endpoint}{entity}?filter={id_filter_field(entity)}:{'|'.join(clean_ids)}&per_page=100{'&data-version=2' if is_v2 else ''}"
        try:
            async with session.get(api_url) as response:
                if response.status == 200:
                    data = await response.json()
                    for result in data["results"]:
                        store[entity][extract_id(result["id"])] = result
                    returned_ids = [extract_id(result["id"]) for result in data["results"]]
                    missing_ids = list(set(ids) - set(returned_ids))
                    for id in missing_ids:
                        store[entity][id] = None
                    return  # Success - exit retry loop
                
                elif response.status == 429:
                    # Rate limited - implement exponential backoff with jitter
                    if attempt < max_retries:
                        # Check for Retry-After header
                        retry_after = response.headers.get('Retry-After')
                        if retry_after:
                            try:
                                # Try parsing as integer seconds first
                                delay = min(int(retry_after), max_delay)
                            except ValueError:
                                try:
                                    # Parse as HTTP date format
                                    retry_time = parsedate_to_datetime(retry_after)
                                    delay = min((retry_time - datetime.now()).total_seconds(), max_delay)
                                    delay = max(delay, 1)  # Ensure at least 1 second delay
                                except (ValueError, TypeError):
                                    # Fall back to exponential backoff if parsing fails
                                    delay = min(base_delay * (2 ** attempt), max_delay)
                        else:
                            # Exponential backoff: 1s, 2s, 4s, 8s, 16s
                            delay = min(base_delay * (2 ** attempt), max_delay)
                        
                        # Add jitter (±25% randomness) to avoid thundering herd
                        jitter = delay * 0.25 * (2 * random.random() - 1)
                        final_delay = delay + jitter
                        
                        print(f"Rate limited (429) - retrying in {final_delay:.1f}s (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(final_delay)
                        continue
                    else:
                        print(f"Rate limited (429) - max retries exceeded for {entity}")
                        break
                
                elif response.status in [500, 502, 503, 504]:
                    # Server errors - retry with shorter backoff
                    if attempt < max_retries:
                        delay = min(base_delay * (1.5 ** attempt), 10)  # Shorter backoff for server errors
                        jitter = delay * 0.1 * (2 * random.random() - 1)
                        final_delay = delay + jitter
                        
                        print(f"Server error ({response.status}) - retrying in {final_delay:.1f}s (attempt {attempt + 1}/{max_retries}) from {api_url}")
                        await asyncio.sleep(final_delay)
                        continue
                    else:
                        print(f"Server error ({response.status}) - max retries exceeded for {entity} from {api_url}")
                        break
                
                else:
                    print(f"HTTP {response.status} error fetching {entity} from {api_url}")
                    break  # Don't retry for other HTTP errors (400, 401, 403, etc.)
                    
        except asyncio.TimeoutError:
            if attempt < max_retries:
                delay = min(base_delay * (1.5 ** attempt), 10)
                print(f"Timeout - retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})")
                await asyncio.sleep(delay)
                continue
            else:
                print(f"Timeout - max retries exceeded for {entity}")
                break
                
        except Exception as e:
            print(f"Error fetching {entity} from {url}: {e}")
            break  # Don't retry for other exceptions
        finally:
            # Always release the rate limiter
            rate_limiter.release()
    
    # If we get here, all retries failed - mark all IDs as missing
    for id in ids:
        store[entity][id] = None


def extract_id(input_str):
    org_index = input_str.find('.org/')
    return input_str[org_index + 5:] if org_index != -1 else input_str


def id_filter_field(entity):
    uses_id = ["keywords", "domains", "fields", "subfields", "continents", "countries", "languages", "licenses", "sdgs", "work-types", "source-types"]
    return "id" if entity in uses_id else "ids.openalex"


def is_test_count_field(field):
    return field in ["authorships.id", "authorships.institutions.id", "authorships.countries", "concepts.id", "topics.id"]


def get_field_value(obj, field):
    """Get nested field value from object using dot notation"""
    if obj is None:
        return None
    
    if is_test_count_field(field):
        return get_nested_strings(obj, field)
    
    keys = field.split('.')
    value = obj
    
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    
    return value


def get_nested_strings(obj, field):
    """
    Extract strings from nested structures with auto-detection.
    Handles patterns like:
    - array.object.string: "authorships.id"
    - array.object.array.string: "authorships.countries" 
    - array.object.array.object.string: "authorships.institutions.id"
    """
    def _extract_strings(current_obj, remaining_keys):
        """Recursive helper to extract strings from nested structure"""
        if not remaining_keys:
            # No more keys - collect strings from current value
            if isinstance(current_obj, str):
                return [current_obj]
            elif isinstance(current_obj, list):
                # Array of strings
                return [item for item in current_obj if isinstance(item, str)]
            else:
                return []
        
        # More keys to process
        next_key = remaining_keys[0]
        rest_keys = remaining_keys[1:]
        
        if isinstance(current_obj, list):
            # Current level is an array - iterate through items
            strings = []
            for item in current_obj:
                if isinstance(item, dict) and next_key in item:
                    strings.extend(_extract_strings(item[next_key], rest_keys))
            return strings
            
        elif isinstance(current_obj, dict) and next_key in current_obj:
            # Current level is an object - access the next key
            return _extract_strings(current_obj[next_key], rest_keys)
            
        else:
            # Invalid structure or missing key
            return []
    
    if obj is None:
        return []
    
    keys = field.split('.')
    return _extract_strings(obj, keys)


def deep_equal(obj1, obj2):
    """Deep equality comparison similar to lodash _.isEqual"""
    if obj1 is obj2:
        return True
    
    if type(obj1) != type(obj2):
        return False
    
    if isinstance(obj1, dict):
        if len(obj1) != len(obj2):
            return False
        for key in obj1:
            if key not in obj2 or not deep_equal(obj1[key], obj2[key]):
                return False
        return True
    
    if isinstance(obj1, list):
        if len(obj1) != len(obj2):
            return False
        for i in range(len(obj1)):
            if not deep_equal(obj1[i], obj2[i]):
                return False
        return True
    
    return obj1 == obj2


def calc_match(prod, walden, entity):
    """Calculate matches between a prod and a walden result"""
    
    def passes_5_percent(prod_value, walden_value):
        """Check if values are within 5% of each other"""
        if type(prod_value) != type(walden_value):
            return False
        
        if prod_value == 0 and walden_value == 0:
            return True

        if prod_value == 0:
            return False

        return abs((walden_value - prod_value) / prod_value * 100) <= 5

    def passes_5_percent_or_more(prod_value, walden_value):
        """Check if values are within 5% of each other or more"""
        if type(prod_value) != type(walden_value):
            return False
        
        if walden_value >= prod_value:
            return True

        return passes_5_percent(prod_value, walden_value)

    match = {"_test_values": {}}
    
    # Iterate through all fields in the schema for this entity type
    for field in schema[entity]:
        field_type_and_test = schema[entity][field]
        parts = field_type_and_test.split('|')
        field_type = parts[0]
        test = parts[1] if len(parts) > 1 else None
        
        passed = False
        
        prod_value = get_field_value(prod, field)
        walden_value = get_field_value(walden, field)
        
        if is_test_count_field(field):
            if test == "set =":
                match["_test_values"][field] = {
                    "prod": len(set(prod_value)) if isinstance(prod_value, list) else prod_value,
                    "walden": len(set(walden_value)) if isinstance(walden_value, list) else walden_value
                }
            else:
                match["_test_values"][field] = {
                    "prod": len(prod_value) if isinstance(prod_value, list) else prod_value,
                    "walden": len(walden_value) if isinstance(walden_value, list) else walden_value
                }

        if prod and not walden:
            passed = False

        elif prod_value is None and walden_value is None:
            passed = True

        elif field_type == "number":
            if type(prod_value) != type(walden_value):
                passed = False
            elif test == "≥":
                passed = prod_value <= walden_value
            elif test == "<5%":
                passed = passes_5_percent(prod_value, walden_value)
            elif test == "-5%+":
                passed = passes_5_percent_or_more(prod_value, walden_value)
            else:
                passed = prod_value == walden_value

        elif field_type == "array":
            if test == "fill-in":
                passed = (prod_value is None and isinstance(walden_value, list)) \
                            or deep_equal(prod_value, walden_value)
            elif test == "exists-fill-in":
                passed = (prod_value is None and walden_value is None) \
                            or (isinstance(prod_value, list)) and isinstance(walden_value, list)
            elif not (isinstance(prod_value, list) and isinstance(walden_value, list)):
                passed = False
            elif test == "≥":
                passed = len(prod_value) <= len(walden_value)
            elif test == "<5%":
                passed = passes_5_percent(len(prod_value), len(walden_value))
            elif test == "-5%+":
                passed = passes_5_percent_or_more(len(prod_value), len(walden_value))
            elif test == "count =":
                passed = len(prod_value) == len(walden_value)
            elif test == "set =":
                passed = set(prod_value) == set(walden_value)
            else:
                passed = deep_equal(prod_value, walden_value)

        elif field_type == "string":
            if test == "fill-in":
                passed = (prod_value is None and isinstance(walden_value, str)) \
                            or prod_value == walden_value
            elif test == "exists-fill-in":
                passed = (prod_value is None and walden_value is None) \
                            or (isinstance(prod_value, str)) and isinstance(walden_value, str)
            elif not (isinstance(prod_value, str) and isinstance(walden_value, str)):
                passed = False
            elif test == "len <5%":
                passed = passes_5_percent(len(prod_value), len(walden_value))
            else:
                passed = prod_value == walden_value

        elif field_type == "object":
            if test == "fill-in":
                passed = (prod_value is None and isinstance(walden_value, dict)) \
                            or deep_equal(prod_value, walden_value)
            elif test == "exists-fill-in":
                passed = (prod_value is None and walden_value is None) \
                            or (isinstance(prod_value, dict)) and isinstance(walden_value, dict) 
            else:
                passed = deep_equal(prod_value, walden_value)

        
        match[field] = passed
        
    _test_fields = test_fields.get(entity, []);
    match["testsPassed"] = all(match[field] for field in _test_fields) if len(_test_fields) > 0 else False

    return match


def calc_matches():
    entities = ["works", "authors", "sources", "institutions", "publishers"]
    for entity in entities:
      for id in prod_results[entity]:
        matches[entity][id] = calc_match(prod_results[entity][id], walden_results[entity][id], entity)


def calc_match_rates():
    entities = ["works"]
    for entity in entities:
      fields = list(schema[entity].keys()) + ["testsPassed"]
      count = defaultdict(int)
      hits = defaultdict(int)
      for id in prod_results[entity]:
        for field in fields:
          if matches[entity][id][field]:
            hits[field] += 1
          count[field] += 1
            
      for field in fields:
        match_rates[entity][field] = round(100 * hits[field] / count[field])

    print(match_rates)


def calc_sum_fields():
  entities = ["works"]
  def sum_field(field, store):
    sum = 0
    for id in store:
      if store[id] and isinstance(store[id][field], list):
        sum += len(store[id][field])
    return sum

  for entity in entities:
    sum_fields_store[entity] = {}
    for field in sum_fields[entity]:
      sum_fields_store[entity][field] = {
        "prod": sum_field(field, prod_results[entity]),
        "walden": sum_field(field, walden_results[entity])
      }
    
  
def calc_recall():
    for entity in prod_results:
        count = 0
        hits = 0
        id_hits = 0
        recall[entity] = {}
        for id in prod_results[entity]:
            if walden_results[entity][id]:
                hits += 1
            count += 1
            if entity in canonical_ids:
              if matches[entity][id][canonical_ids[entity]]:
                id_hits += 1
        recall[entity]["recall"] = round(100 * hits / count)
        recall[entity]["canonicalId"] = round(100 * id_hits / count) if entity in canonical_ids else "-"
        recall[entity]["sampleSize"] = count
        print(f"Recall for {entity}: {recall[entity]}")


def save_data():
    recall_data = dict(recall)
    recall_metric_set = MetricSet(
        type="recall",
        entity="all",
        date=datetime.now(),
        data=recall_data
    )

    match_rates_data = {
      "rates": dict(match_rates["works"]),
      "sums": dict(sum_fields_store["works"]),
    }
    match_rates_metric_set = MetricSet(
        type="field_match_rates",
        entity="works",
        date=datetime.now(),
        data=match_rates_data
    )

    # Bulk upsert optimization for large datasets
    from sqlalchemy.dialects.postgresql import insert
    
    # Prepare bulk data
    current_time = datetime.now()
    bulk_data = []
    for id in prod_results["works"]:
        bulk_data.append({
            'id': id,
            'entity': 'works',
            'date': current_time,
            'prod': prod_results["works"][id],
            'walden': walden_results["works"][id],
            'match': matches["works"][id]
        })
    
    # PostgreSQL UPSERT - much faster for bulk operations
    stmt = insert(Response).values(bulk_data)
    stmt = stmt.on_conflict_do_update(
        index_elements=['id'],
        set_={
            'entity': stmt.excluded.entity,
            'date': stmt.excluded.date,
            'prod': stmt.excluded.prod,
            'walden': stmt.excluded.walden,
            'match': stmt.excluded.match
        }
    )
    db.session.execute(stmt)

    # Save to database
    db.session.add(recall_metric_set)
    db.session.add(match_rates_metric_set)
    db.session.commit()
    
    print(f"Saved recall data and match rates to database")


async def run_metrics(test=False):
    samples = get_latest_prod_samples()
    
    # Create tasks for all samples to run in parallel
    tasks = []
    for sample in samples:
        ids = sample.ids
        tasks.append(fetch_all_ids(ids, sample.entity))
    
    # Execute all sample fetching in parallel
    await asyncio.gather(*tasks)
    
    # Calculate recall after all data is fetched
    calc_matches()
    calc_match_rates()
    calc_sum_fields()
    calc_recall()

    # Save data to database
    if not test:
        save_data()


def get_latest_prod_samples():
    """
    Return a list of samples, one for each value of "entity" and the most recent only
    if there is more than one sample for each entity value, only considering samples
    whose type is "prod".
    """
    from sqlalchemy import func
    
    # Subquery to find the latest date for each entity with type "prod"
    latest_dates = (
        Sample.query
        .filter(Sample.type == 'prod')
        .with_entities(
            Sample.entity,
            func.max(Sample.date).label('max_date')
        )
        .group_by(Sample.entity)
        .subquery()
    )
    
    # Join with the original table to get the full sample records
    # for the latest date of each entity
    latest_samples = (
        Sample.query
        .join(
            latest_dates,
            (Sample.entity == latest_dates.c.entity) &
            (Sample.date == latest_dates.c.max_date)
        )
        .filter(Sample.type == 'prod')
        .all()
    )
    
    return latest_samples


def get_latest_sample(entity):
    return Sample.query.filter_by(entity=entity, type="prod").order_by(Sample.date.desc()).first()