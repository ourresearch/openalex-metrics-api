import aiohttp
import asyncio
import os
import time
import random
from datetime import datetime
from math import ceil
from contextlib import contextmanager
from email.utils import parsedate_to_datetime
from collections import defaultdict, deque

from models import Sample, MetricSet, Response
from app import db
from schema import tests_schema, entities, is_set_test, get_test_keys

OPENALEX_API_KEY = os.getenv("OPENALEX_API_KEY")

api_endpoint = "https://api.openalex.org/"

samples = defaultdict(dict)
prod_results = defaultdict(dict)
walden_results = defaultdict(dict)
matches = defaultdict(dict)
match_rates = defaultdict(dict)
coverage = defaultdict(dict)

MAX_REQUESTS_PER_SECOND = 50
rate_limiter = None
headers = {'Authorization': f'Bearer {OPENALEX_API_KEY}'}


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
        
        try:
            # Extract the part after the last "/" if present, otherwise use the full id
            clean_ids = [id.split("/")[-1] if "/" in id else id for id in ids]
            api_url = f"{api_endpoint}{entity}?filter={id_filter_field(entity)}:{'|'.join(clean_ids)}&per_page=100{'&data-version=2' if is_v2 else ''}"
            
            #if entity == "institutions":
            #    print("GET", api_url)

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
            print(f"Error fetching {entity} from {api_url}: {e}")
            break  # Don't retry for other exceptions
            
        finally:
            # Always release the semaphore, regardless of success or failure
            rate_limiter.release()


def extract_id(input_str):
    org_index = input_str.find('.org/')
    return input_str[org_index + 5:] if org_index != -1 else input_str


def id_filter_field(entity):
    uses_id = ["keywords", "domains", "fields", "subfields", "continents", "countries", "languages", "licenses", "sdgs", "work-types", "source-types"]
    return "id" if entity in uses_id else "ids.openalex"


def get_field_value(obj, field):
    """Get nested field value from object using dot notation"""
    if obj is None:
        return None
    
    if "*" in field:
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
    Extract strings from nested structures using JSONPath format.
    Handles patterns like:
    - "authorships[*].id"
    - "authorships[*].institutions[*].id"
    - "authorships[*].countries"
    """
    import re
    
    def _parse_jsonpath(path):
        """Parse JSONPath into tokens, handling [*] syntax"""
        # Split on dots but preserve [*] markers
        tokens = []
        parts = path.split('.')
        
        for part in parts:
            if '[*]' in part:
                # Split field[*] into field and [*]
                field_name = part.replace('[*]', '')
                tokens.append(field_name)
                tokens.append('[*]')
            else:
                tokens.append(part)
        
        return tokens
    
    def _extract_strings(current_obj, remaining_tokens):
        """Recursive helper to extract strings from nested structure using JSONPath tokens"""
        if not remaining_tokens:
            # No more tokens - collect strings from current value
            if isinstance(current_obj, str):
                return [current_obj]
            elif isinstance(current_obj, list):
                # Array of strings
                return [item for item in current_obj if isinstance(item, str)]
            else:
                return []
        
        # More tokens to process
        next_token = remaining_tokens[0]
        rest_tokens = remaining_tokens[1:]
        
        if next_token == '[*]':
            # Array wildcard - iterate through all items
            if isinstance(current_obj, list):
                strings = []
                for item in current_obj:
                    strings.extend(_extract_strings(item, rest_tokens))
                return strings
            else:
                return []
                
        else:
            # Regular field access
            if isinstance(current_obj, dict) and next_token in current_obj:
                return _extract_strings(current_obj[next_token], rest_tokens)
            else:
                # Invalid structure or missing key
                return []
    
    if obj is None:
        return []
    
    tokens = _parse_jsonpath(field)
    return _extract_strings(obj, tokens)


def calc_match(prod, walden, entity):
    """Calculate matches between a prod and a walden result"""
    
    match = {"_test_values": {}}
    
    # Iterate through all tests in the schema for this entity type
    for test in tests_schema[entity]:
        
        test_key = test["display_name"].replace(" ", "_").lower()
        prod_value = get_field_value(prod, test["field"])
        walden_value = get_field_value(walden, test["field"])
        
        # Store comparison values if they differ from raw values
        if "*" in test["field"]:
            if is_set_test(test["test_func"]):
                match["_test_values"][test_key] = {
                    "prod": len(set(prod_value)) if isinstance(prod_value, list) else prod_value,
                    "walden": len(set(walden_value)) if isinstance(walden_value, list) else walden_value
                }
            else:
                match["_test_values"][test_key] = {
                    "prod": len(prod_value) if isinstance(prod_value, list) else prod_value,
                    "walden": len(walden_value) if isinstance(walden_value, list) else walden_value
                }
            
        match[test_key] = test["test_func"](prod_value, walden_value)
        
    return match


def calc_matches():
    for entity in entities:
      if not "both" in samples[entity]:
        continue
      for id in samples[entity]["both"]["ids"]:
        matches[entity][id] = calc_match(prod_results[entity][id], walden_results[entity][id], entity)


def calc_match_rates():
    for entity in entities:
      if not "both" in samples[entity]:
        continue
      test_keys = get_test_keys(entity)
      count = defaultdict(int)
      hits = defaultdict(int)
      for id in samples[entity]["both"]["ids"]:
        for test_key in test_keys:
          if matches[entity][id][test_key]:
            hits[test_key] += 1
          count[test_key] += 1
            
      for test_key in test_keys:
        match_rates[entity][test_key] = round(100 * hits[test_key] / count[test_key])

      # Calculate average match rates for bug and feature tests
      for type_ in ["bug", "feature"]:
        test_keys = get_test_keys(entity, type_=type_)
        average_sum = 0
        for test_key in test_keys:
          average_sum += match_rates[entity][test_key]
        match_rates[entity][f"_average_{type_}"] = round(average_sum / len(test_keys))

    print(match_rates)


def calc_all_coverage():
    calc_coverage("prod")
    calc_coverage("walden")


def calc_coverage(type_):
    test_store = walden_results if type_ == "prod" else prod_results
    for entity in samples.keys():
        count = 0
        hits = 0
        if not coverage[entity]:
            coverage[entity] = {}
        if type_ in samples[entity]:
            for id in samples[entity][type_]["ids"]:
                if test_store[entity].get(id, None):
                    hits += 1
                count += 1
        coverage[entity][type_] = {
            "coverage": round(100 * hits / count) if count > 0 else "-",
            "sampleSize": count
        }


async def get_entity_counts():
    async def get_entity_count(session, url, entity, type_):
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                coverage[entity][type_]["count"] = data["meta"]["count"]

    async with aiohttp.ClientSession(headers=headers) as session:
        tasks = []
        for entity in samples.keys():
            tasks.append(get_entity_count(session, api_endpoint + entity, entity, "prod"))
            tasks.append(get_entity_count(session, api_endpoint + entity + "?data-version=2", entity, "walden"))       
        await asyncio.gather(*tasks)


@contextmanager
def db_session():
    """Context manager for database sessions with proper cleanup and timeout"""
    session = db.session
    try:
        # Set statement timeout to prevent hanging queries
        # session.execute("SET statement_timeout = '180s'")
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Database error: {e}")
        raise
    finally:
        session.close()


def save_data():
    print("Saving data to database...")
    start_time = time.time()
    with db_session() as session:
        coverage_data = dict(coverage)
        coverage_metric_set = MetricSet(
            type="coverage",
            entity="all",
            date=datetime.now(),
            data=coverage_data
        )

        match_rates_data = dict(match_rates)
        match_rates_metric_set = MetricSet(
            type="match_rates",
            entity="all",
            date=datetime.now(),
            data=match_rates_data
        )

        # Bulk upsert optimization for large datasets
        from sqlalchemy.dialects.postgresql import insert
        
        # Prepare bulk data
        current_time = datetime.now()
        bulk_data = []
        for id in samples["works"]["both"]["ids"]:
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
        session.execute(stmt)

        # Save to database
        session.add(coverage_metric_set)
        session.add(match_rates_metric_set)
    
    elapsed_time = time.time() - start_time
    print(f"Saved metrics and responses to database in {elapsed_time:.2f} seconds")


def get_latest_samples(type_):
    """
    Return a list of samples, one for each value of "entity" and the most recent only
    if there is more than one sample for each entity value, only considering samples
    whose type is "prod".
    """
    from sqlalchemy import func

    with db_session() as session:
        # Subquery to get latest date for each entity
        latest_dates = (
            session.query(
                Sample.entity,
                func.max(Sample.date).label("max_date")
            )
            .filter(Sample.type == type_)
            .group_by(Sample.entity)
            .subquery()
        )

        # Select only the columns we need; returns plain tuples
        latest_samples = (
            session.query(Sample.entity, Sample.ids, Sample.type, Sample.name)
            .join(
                latest_dates,
                (Sample.entity == latest_dates.c.entity) &
                (Sample.date == latest_dates.c.max_date)
            )
            .filter(Sample.type == type_)
            .all()
        )

        # latest_samples is now a list of tuples: [(entity, ids), ...]
        return [{'entity': entity, 'ids': ids, 'type': type_, 'name': name} for entity, ids, type_, name in latest_samples]


async def run_metrics(test=False):
    latest_samples = get_latest_samples(type_="prod")
    latest_samples += get_latest_samples(type_="walden")
    latest_samples += get_latest_samples(type_="both")

    for sample in latest_samples:
        print(f"Using sample {sample['name']} ({sample['type']}) with {len(sample['ids'])} IDs")
        samples[sample["entity"]][sample["type"]] = sample

    # Create tasks for all samples to run in parallel
    tasks = []
    for sample in latest_samples:
        ids = sample["ids"]
        entity = sample["entity"]
        tasks.append(fetch_all_ids(ids, entity))
    
    # Execute all sample fetching in parallel
    await asyncio.gather(*tasks)
    
    # Calculate recall after all data is fetched
    calc_matches()
    calc_match_rates()
    calc_all_coverage()
    await get_entity_counts()

    print("Coverage:", coverage)

    # Save data to database
    if not test:
        save_data()