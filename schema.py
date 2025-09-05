
from functools import wraps
from numbers import Number


"""
Test Helpers
"""
def expects_numbers(func):
  @wraps(func)
  def wrapper(prod_value, walden_value):
    if not isinstance(prod_value, Number) or not isinstance(walden_value, Number):
      return False
        
    return func(prod_value, walden_value)
    
  return wrapper


def expects_strings(func):
  @wraps(func)
  def wrapper(prod_value, walden_value):
    if not isinstance(prod_value, str) or not isinstance(walden_value, str):
      return False
        
    return func(prod_value, walden_value)
    
  return wrapper


def expects_lists(func):
  @wraps(func)
  def wrapper(prod_value, walden_value):
    if not isinstance(prod_value, list) or not isinstance(walden_value, list):
      return False
        
    return func(prod_value, walden_value)
    
  return wrapper


def is_set_test(func):
  return func in [set_does_not_equal, set_count_does_not_equal, set_count_increased, set_count_decreased]


def get_test_keys(entity, type_="all"):
  if type_ == "all":
    tests = tests_schema[entity]
  elif type_ == "bug":
    tests = [test for test in tests_schema[entity] if test["test_type"] == "bug"]
  elif type_ == "feature":
    tests = [test for test in tests_schema[entity] if test["test_type"] == "feature"]

  return [test["display_name"].replace(" ", "_").lower() for test in tests]


"""
Test Functions
"""
def not_exact_match(prod_value, walden_value):
  return prod_value != walden_value


@expects_numbers
def greater_than(prod_value, walden_value):
  return walden_value > prod_value


@expects_numbers
def greater_than_or_equal(prod_value, walden_value):
  return walden_value >= prod_value


@expects_numbers
def less_than(prod_value, walden_value):
  return walden_value < prod_value


@expects_numbers
def within_5_percent(prod_value, walden_value):  
  if prod_value == 0 and walden_value == 0:
      return True

  if prod_value == 0:
      return False

  return abs((walden_value - prod_value) / prod_value * 100) <= 5


@expects_numbers
def below_5_percent(prod_value, walden_value):
  return prod_value > walden_value and not within_5_percent(prod_value, walden_value)


@expects_numbers
def within_5_percent_or_more(prod_value, walden_value):
  return walden_value > prod_value or within_5_percent(prod_value, walden_value)


@expects_strings
def length_not_within_5_percent(prod_value, walden_value):
  return not within_5_percent(len(prod_value), len(walden_value))


@expects_lists
def count_does_not_equal(prod_value, walden_value):
  return len(prod_value) != len(walden_value)


@expects_lists
def set_does_not_equal(prod_value, walden_value):
  return set(prod_value) != set(walden_value)


@expects_lists
def set_count_does_not_equal(prod_value, walden_value):
  return len(set(prod_value)) != len(set(walden_value))


@expects_lists
def set_count_increased(prod_value, walden_value):
  return len(set(prod_value)) < len(set(walden_value))


@expects_lists
def set_count_decreased(prod_value, walden_value):
  return len(set(prod_value)) > len(set(walden_value))


def status_changed_except_gold(prod_value, walden_value):
  return walden_value != "gold" and prod_value != walden_value


def status_became_gold(prod_value, walden_value):
  return prod_value != "gold" and walden_value == "gold"


def became_false(prod_value, walden_value):
  return walden_value is False and prod_value is not False


def became_null(prod_value, walden_value):
  return walden_value is None and prod_value is not None


def became_true(prod_value, walden_value):
  return walden_value is True and prod_value is not True


def value_lost(prod_value, walden_value):
  return prod_value is not None and walden_value is None


def value_added(prod_value, walden_value):
  return prod_value is None and walden_value is not None


def existing_value_changed(prod_value, walden_value):
  """ True if prod had a value that changed, but False if walden adds a value where prod had none"""
  return prod_value is not None and prod_value != walden_value


def language_changed_to_non_english(prod_value, walden_value):
  return prod_value == "en" and walden_value != "en"


def language_changed_to_english(prod_value, walden_value):
  return prod_value != "en" and walden_value == "en"


def type_changed_to_repository(prod_value, walden_value):
  return prod_value != "repository" and walden_value == "repository"


def type_changed_from_funder(prod_value, walden_value):
  return prod_value == "funder" and walden_value != "funder"

"""
TEST DEFINITIONS
"""

tests_schema_base = {
  "works": [
    # Sources
    {
      "display_name": "Primary Source Lost",
      "field": "primary_location.source.id",
      "field_type": "string",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "sources",
      "icon": "mdi-map-marker-account",
      "description": "The <code>primary_location.source.id</code> field had a value but now is null or missing",
    },
    {
      "display_name": "Primary Source Added",
      "field": "primary_location.source.id",
      "field_type": "string",
      "test_func": value_added,
      "test_type": "feature",
      "category": "sources",
      "icon": "mdi-map-marker-account",
      "description": "The <code>primary_location.source.id</code> field was missing but now has a value",
    },
    {
      "display_name": "Primary Source Changed",
      "field": "primary_location.source.id",
      "field_type": "string",
      "test_func": existing_value_changed,
      "test_type": "bug",
      "category": "sources",
      "icon": "mdi-map-marker-account",
      "description": "The <code>primary_location.source.id</code> field had a value and changed",
    },
    {
      "display_name": "Primary Source Changed to Core",
      "field": "primary_location.source.is_core",
      "field_type": "boolean",
      "test_func": became_true,
      "test_type": "feature",
      "category": "sources",
      "icon": "mdi-map-marker-check",
      "description": "The <code>primary_location.source.is_core</code> field became <code>true</code>",
    },
    {
      "display_name": "Primary Source Changed to Non-Core",
      "field": "primary_location.source.is_core",
      "field_type": "boolean",
      "test_func": became_false,
      "test_type": "bug",
      "category": "sources",
      "icon": "mdi-map-marker-check",
      "description": "The <code>primary_location.source.is_core</code> field became <code>false</code>",
    },
    {
      "display_name": "Best OA Source Added",
      "field": "best_oa_location.source.id",
      "field_type": "string",
      "test_func": value_added,
      "test_type": "feature",
      "category": "sources",
      "icon": "mdi-map-marker-account-outline",
      "description": "The <code>best_oa_location.source.id</code> field was missing but now has a value",  
    },
    {
      "display_name": "Best OA is_published Changed",
      "field": "best_oa_location.source.is_published",
      "field_type": "boolean",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "sources",
      "icon": "mdi-map-marker-check-outline",
      "description": "The <code>best_oa_location.source.is_published</code> fields are not equal",
    },
    # Open Access
    {
      "display_name": "is_oa Changed",
      "field": "open_access.is_oa",
      "field_type": "boolean",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "open access",
      "icon": "mdi-lock-open-outline",
      "description": "The <code>open_access.is_oa</code> fields are not equal",
    },
    {
      "display_name": "is_oa Lost",
      "field": "open_access.is_oa",
      "field_type": "boolean",
      "test_func": became_false,
      "test_type": "bug",
      "category": "open access",
      "icon": "mdi-lock-open-outline",
      "description": "The <code>open_access.is_oa</code> field became <code>false</code>",
    },
    {
      "display_name": "OA Status Changed",
      "field": "open_access.oa_status",
      "field_type": "string",
      "test_func": status_changed_except_gold,
      "test_type": "bug",
      "category": "open access",
      "icon": "mdi-lock-percent-open-outline",
      "description": "The <code>open_access.oa_status</code> field changed to a value other than <code>gold</code>",
    },
    {
      "display_name": "OA Status Changed to Gold",
      "field": "open_access.oa_status",
      "field_type": "string",
      "test_func": status_became_gold,
      "test_type": "feature",
      "category": "open access",
      "icon": "mdi-lock-percent-open-outline",
      "description": "The <code>open_access.oa_status</code> field changed to <code>gold</code>",
    },
    {
      "display_name": "PDF URL Lost",
      "field": "best_oa_location.source.pdf_url",
      "field_type": "string",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "open access",
      "icon": "mdi-file-pdf-box",
      "description": "The <code>best_oa_location.source.pdf_url</code> field was not null but now is null or missing",
    },
    {
      "display_name": "PDF URL Added",
      "field": "best_oa_location.source.pdf_url",
      "field_type": "string",
      "test_func": value_added,
      "test_type": "feature",
      "category": "open access",
      "icon": "mdi-file-pdf-box",
      "description": "The <code>best_oa_location.source.pdf_url</code> field was missing but now has a value",
    },
    {
      "display_name": "Best OA License Changed",
      "field": "best_oa_location.source.license",
      "field_type": "string",
      "test_func": existing_value_changed,
      "test_type": "bug",
      "category": "open access",
      "icon": "mdi-license",
      "description": "The <code>best_oa_location.source.license</code> field had a value and the value changed",
    },
    {
      "display_name": "Best OA License Lost",
      "field": "best_oa_location.source.license",
      "field_type": "string",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "open access",
      "icon": "mdi-license",
      "description": "The <code>best_oa_location.source.license</code> field was not null but now is null or missing",
    },
    {
      "display_name": "Best OA License Added",
      "field": "best_oa_location.source.license",
      "field_type": "string",
      "test_func": value_added,
      "test_type": "feature",
      "category": "open access",
      "icon": "mdi-license",
      "description": "The <code>best_oa_location.source.license</code> field was missing but now has a value",
    },
    # Language
    {
      "display_name": "Language Changed to Non-English",
      "field": "language",
      "field_type": "string",
      "test_func": language_changed_to_non_english,
      "test_type": "feature",
      "category": "language",
      "icon": "mdi-translate",
      "description": "The <code>language</code> field changed to a non-English value",
    },
    {
      "display_name": "Language Added",
      "field": "language",
      "field_type": "string",
      "test_func": value_added,
      "test_type": "feature",
      "category": "language",
      "icon": "mdi-translate",
      "description": "The <code>language</code> field was missing but now has a value",
    },
    {
      "display_name": "Language Changed to English",
      "field": "language",
      "field_type": "string",
      "test_func": language_changed_to_english,
      "test_type": "bug",
      "category": "language",
      "icon": "mdi-translate",
      "description": "The <code>language</code> field changed to English",
    },
    {
      "display_name": "Language Lost",
      "field": "language",
      "field_type": "string",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "language",
      "icon": "mdi-translate",
      "description": "The <code>language</code> field was not null but now is null or missing",
    },
    # Locations
    {
      "display_name": "Locations Count Increased",
      "field": "locations_count",
      "field_type": "number",
      "test_func": greater_than,
      "test_type": "feature",
      "category": "locations",
      "icon": "mdi-map-marker-multiple-outline",
      "description": "The <code>locations_count</code> field increased",
    },
        {
      "display_name": "Locations Count Decreased",
      "field": "locations_count",
      "field_type": "number",
      "test_func": less_than,
      "test_type": "bug",
      "category": "locations",
      "icon": "mdi-map-marker-multiple-outline",
      "description": "The <code>locations_count</code> field decreased",
    },
    # Citations
    {
      "display_name": "Referenced Works Count Decreased",
      "field": "referenced_works_count",
      "field_type": "number",
      "test_func": below_5_percent,
      "test_type": "bug",
      "category": "citations",
      "icon": "mdi-book-arrow-down-outline",
      "description": "The <code>referenced_works_count</code> field decreased by 5% or more",
    },
    {
      "display_name": "Referenced Works Count Increased",
      "field": "referenced_works_count",
      "field_type": "number",
      "test_func": greater_than,
      "test_type": "feature",
      "category": "citations",
      "icon": "mdi-book-arrow-down-outline",
      "description": "The <code>referenced_works_count</code> field increased",
    },
    {
      "display_name": "Citations Count Decreased",
      "field": "cited_by_count",
      "field_type": "number",
      "test_func": less_than,
      "test_type": "bug",
      "category": "citations",
      "icon": "mdi-book-arrow-down-outline",
      "description": "The <code>cited_by_count</code> field decreased",
    },
    {
      "display_name": "Citations Count Increased",
      "field": "cited_by_count",
      "field_type": "number",
      "test_func": greater_than,
      "test_type": "feature",
      "category": "citations",
      "icon": "mdi-book-arrow-down-outline",
      "description": "The <code>cited_by_count</code> field increased",
    },
    # Authors
    {
      "display_name": "Authorships Count Changed",
      "field": "authorships[*].id",
      "field_type": "array",
      "test_func": set_count_does_not_equal,
      "test_type": "bug",
      "category": "authors",
      "icon": "mdi-account-multiple-outline",
      "description": "The size of the set of items in <code>authorships</code> is not equal",
    },
    {
      "display_name": "Authorships Changed",
      "field": "authorships[*].id",
      "field_type": "array",
      "test_func": set_does_not_equal,
      "test_type": "bug",
      "category": "authors",
      "icon": "mdi-account-multiple-check-outline",
      "description": "The set of items in the <code>authorships[*].id</code> fields are not equal",
    },
    {
      "display_name": "Corresponding Author Changed",
      "field": "corresponding_author_ids",
      "field_type": "array",
      "test_func": set_does_not_equal,
      "test_type": "bug",
      "category": "authors",
      "icon": "mdi-account-check-outline",
      "description": "The set of items in the <code>corresponding_author_ids</code> fields are not equal",
    },
    # Institutions
    {
      "display_name": "Institutions Changed",
      "field": "authorships[*].institutions[*].id",
      "field_type": "array",
      "test_func": set_does_not_equal,
      "test_type": "bug",
      "category": "institutions",
      "icon": "mdi-town-hall",
      "description": "The set of items in the <code>authorships[*].institutions[*].id</code> fields are not equal",
    },
    {
      "display_name": "Country Count Increased",
      "field": "authorships[*].countries",
      "field_type": "array",
      "test_func": set_count_increased,
      "test_type": "feature",
      "category": "institutions",
      "icon": "mdi-earth",
      "description": "The count of the set of items in the <code>authorships[*].countries</code> fields increased",
    },
    {
      "display_name": "Country Count Decreased",
      "field": "authorships[*].countries",
      "field_type": "array",
      "test_func": set_count_decreased,
      "test_type": "bug",
      "category": "institutions",
      "icon": "mdi-earth",
      "description": "The count of the set of items in the <code>authorships[*].countries</code> fields decreased",
    },
    # Other
    {
      "display_name": "Title Changed",
      "field": "title",
      "field_type": "string",
      "test_func": length_not_within_5_percent,
      "test_type": "bug",
      "category": "other",
      "icon": "mdi-format-title",
      "description": "The <code>title</code> changed more than 5% in length",
    },
    {
      "display_name": "Publication Year Changed",
      "field": "publication_year",
      "field_type": "number",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "icon": "mdi-calendar-month",
      "description": "The <code>publication_year</code> fileds are not equal",
    },
    {
      "display_name": "Type Changed",
      "field": "type",
      "field_type": "string",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "icon": "mdi-shape-outline",
      "description": "The <code>type</code> fields are not equal",
    },
    {
      "display_name": "Indexed In Changed",
      "field": "indexed_in",
      "field_type": "array",
      "test_func": set_does_not_equal,
      "test_type": "bug",
      "category": "other",
      "icon": "mdi-database-outline",
      "description": "The set of items in the <code>indexed_in</code> fields are not equal",
    },
    {
      "display_name": "Retraction Changed",
      "field": "is_retracted",
      "field_type": "boolean",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "icon": "mdi-file-excel-outline",
      "description": "The <code>is_retracted</code> fields are not equal",
    },
    {
      "display_name": "Retraction Added",
      "field": "is_retracted",
      "field_type": "boolean",
      "test_func": became_true,
      "test_type": "feature",
      "category": "other",
      "icon": "mdi-file-excel-outline",
      "description": "The <code>is_retracted</code> field became <code>true</code>",
    },
    {
      "display_name": "Retraction Lost",
      "field": "is_retracted",
      "field_type": "boolean",
      "test_func": became_false,
      "test_type": "bug",
      "category": "other",
      "icon": "mdi-file-excel-outline",
      "description": "The <code>is_retracted</code> field became <code>false</code>",
    },
    {
      "display_name": "Related Works Changed",
      "field": "related_works",
      "field_type": "array",
      "test_func": set_does_not_equal,
      "test_type": "bug",
      "category": "other",
      "icon": "mdi-book-arrow-down-outline",
      "description": "The set of items in the <code>related_works</code> fields are not equal",
    },
    {
      "display_name": "Abstract Lost",
      "field": "abstract_inverted_index",
      "field_type": "object",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "other",
      "icon": "mdi-text-box-outline",
      "description": "The <code>abstract_inverted_index</code> field had a value but now is null or missing",
    },
    {
      "display_name": "Abstract Added",
      "field": "abstract_inverted_index",
      "field_type": "object",
      "test_func": value_added,
      "test_type": "feature",
      "category": "other",
      "icon": "mdi-text-box-outline",
      "description": "The <code>abstract_inverted_index</code> field was missing but now has a value",
    },
    {
      "display_name": "Grants Changed",
      "field": "grants",
      "field_type": "array",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "icon": "mdi-cash",
      "description": "The <code>grants</code> fields are not exactly equal",
    },
    {
      "display_name": "Grants Lost",
      "field": "grants",
      "field_type": "array",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "other",
      "icon": "mdi-cash",
      "description": "The <code>grants</code> field had a value but now is null or missing",
    },
    {
      "display_name": "APC List Changed",
      "field": "apc_list",
      "field_type": "number",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "icon": "mdi-currency-usd",
      "description": "The <code>apc_list</code> fields are not equal",
    },
    {
      "display_name": "APC Paid Changed",
      "field": "apc_paid",
      "field_type": "number",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "other",
      "icon": "mdi-currency-usd",
      "description": "The <code>apc_paid</code> fields are not equal",
    },
    # Aboutness
    {
      "display_name": "Primary Topic Changed",
      "field": "primary_topic.id",
      "field_type": "string",
      "test_func": not_exact_match,
      "test_type": "bug",
      "category": "aboutness",
      "icon": "mdi-tag-outline",
      "description": "The <code>primary_topic.id</code> fields are not equal",
    },
    {
      "display_name": "Topics Changed",
      "field": "topics[*].id",
      "field_type": "array",
      "test_func": set_does_not_equal,
      "test_type": "bug",
      "category": "aboutness",
      "icon": "mdi-tag-text-outline",
      "description": "The set of items in the <code>topics[*].id</code> fields are not equal",
    },
    {
      "display_name": "Keywords Lost",
      "field": "keywords",
      "field_type": "array",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "aboutness",
      "icon": "mdi-alpha-k",
      "description": "The <code>keywords</code> field had a value but is now null or missing",
    },
    {
      "display_name": "Keywords Added",
      "field": "keywords",
      "field_type": "array",
      "test_func": value_added,
      "test_type": "feature",
      "category": "aboutness",
      "icon": "mdi-alpha-k",
      "description": "The <code>keywords</code> field was missing but now has a value",
    },
    {
      "display_name": "Concepts Changed",
      "field": "concepts[*].id",
      "field_type": "array",
      "test_func": set_does_not_equal,
      "test_type": "bug",
      "category": "aboutness",
      "icon": "mdi-lightbulb-outline",
      "description": "The set of items in the <code>concepts[*].id</code> fields are not equal",
    },
    {
      "display_name": "Concepts Lost",
      "field": "concepts",
      "field_type": "array",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "aboutness",
      "icon": "mdi-lightbulb-outline",
      "description": "The <code>concepts</code> field had a value but is now null or missing",
    },
    {
      "display_name": "SDGs Changed",
      "field": "sustainable_development_goals[*].id",
      "field_type": "array",
      "test_func": set_does_not_equal,
      "test_type": "bug",
      "category": "aboutness",
      "icon": "mdi-sprout-outline",
      "description": "The set of items in the <code>sustainable_development_goals[*].id</code> fields are not equal",
    },
    {
      "display_name": "SDGs Lost",
      "field": "sustainable_development_goals",
      "field_type": "array",
      "test_func": value_lost,
      "test_type": "bug",
      "category": "aboutness",
      "icon": "mdi-sprout-outline",
      "description": "The <code>sustainable_development_goals</code> field had a value but is now null or missing",
    },
  ],
  "sources": [
    {
      "display_name": "is_oa Added",
      "field": "is_oa",
      "field_type": "boolean",
      "test_func": became_true,
      "test_type": "feature",
      "category": "works",
      "icon": "mdi-file-document-outline",
      "description": "The <code>is_oa</code> field became true",
    },
    {
      "display_name": "Type Changed to Repository",
      "field": "type",
      "field_type": "string",
      "test_func": type_changed_to_repository,
      "test_type": "feature",
      "category": "works",
      "icon": "mdi-file-document-outline",
      "description": "The <code>type</code> field changed to <code>repository</code>",
    },
  ],
  "institutions": [
    {
      "display_name": "Type Changed from Funder",
      "field": "type",
      "field_type": "boolean",
      "test_func": type_changed_from_funder,
      "test_type": "feature",
      "category": "works",
      "icon": "mdi-file-document-outline",
      "description": "The <code>type</code> field changed away from <code>funder</code>",
    },  
  ],
  "publishers": [ 
  ]
}

entities = [
  'authors', 
  'continents', 
  'countries',
  'concepts',
  'domains', 
  'fields', 
  'funders', 
  'institution-types', 
  'institutions', 
  'keywords', 
  'languages', 
  'licenses', 
  'publishers', 
  'sdgs', 
  'source-types', 
  'sources', 
  'subfields', 
  'topics', 
  'work-types', 
  'works'
]

non_works_tests = [
  {
    "display_name": "Works Count Decreased",
    "field": "works_count",
    "field_type": "number",
    "test_func": less_than,
    "test_type": "bug",
    "category": "works",
    "icon": "mdi-file-document-outline",
    "description": "The <code>works_count</code> field decreased",
  },
  {
    "display_name": "Works Count Increased",
    "field": "works_count",
    "field_type": "number",
    "test_func": greater_than,
    "test_type": "feature",
    "category": "works",
    "icon": "mdi-file-document-outline",
    "description": "The <code>works_count</code> field increased",
  },
  {
    "display_name": "Citation Count Decreased",
    "field": "cited_by_count",
    "field_type": "number",
    "test_func": less_than,
    "test_type": "bug",
    "category": "citations",
    "icon": "mdi-file-document-outline",
    "description": "The <code>cited_by_count</code> field decreased",
  },
    {
    "display_name": "Citation Count Increased",
    "field": "cited_by_count",
    "field_type": "number",
    "test_func": greater_than,
    "test_type": "feature",
    "category": "citations",
    "icon": "mdi-file-document-outline",
    "description": "The <code>cited_by_count</code> field increased",
  }
]

def make_tests_schema():
  schema = {}
  for entity in entities:
    if entity in tests_schema_base:
      schema[entity] = tests_schema_base[entity]
    else:
      schema[entity] = []
    if entity != "works":
      schema[entity].extend(non_works_tests)

  return schema

tests_schema = make_tests_schema()