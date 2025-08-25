
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
  return func in [set_equals]


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

def exact_match(prod_value, walden_value):
  return prod_value == walden_value


@expects_numbers
def greater_than(prod_value, walden_value):
  return prod_value > walden_value


@expects_numbers
def greater_than_or_equal(prod_value, walden_value):
  return prod_value >= walden_value


@expects_numbers
def within_5_percent(prod_value, walden_value):  
  if prod_value == 0 and walden_value == 0:
      return True

  if prod_value == 0:
      return False

  return abs((walden_value - prod_value) / prod_value * 100) <= 5


@expects_numbers
def within_5_percent_or_more(prod_value, walden_value):
  return walden_value > prod_value or within_5_percent(prod_value, walden_value)


@expects_lists
def count_within_5_percent(prod_value, walden_value):
  return within_5_percent(len(prod_value), len(walden_value))


@expects_strings
def length_within_5_percent(prod_value, walden_value):
  return within_5_percent(len(prod_value), len(walden_value))


@expects_lists
def count_equals(prod_value, walden_value):
  return len(prod_value) == len(walden_value)


@expects_lists
def set_equals(prod_value, walden_value):
  return set(prod_value) == set(walden_value)


def status_equal_except_gold(prod_value, walden_value):
  return walden_value == "gold" or prod_value == walden_value


def status_became_gold(prod_value, walden_value):
  return prod_value != "gold" and walden_value == "gold"


def didnt_become_false(prod_value, walden_value):
  return prod_value == walden_value or walden_value is True


def didnt_become_null(prod_value, walden_value):
  return prod_value == walden_value or walden_value is not None


def fill_in_bug(prod_value, walden_value):
  return prod_value == walden_value or (prod_value is None and walden_value is not None)


def fill_in_feature(prod_value, walden_value):
  return prod_value is None and walden_value is not None


def object_fill_in(prod_value, walden_value):
  return prod_value == walden_value or (prod_value is None and walden_value is not None)


def exists_fill_in(prod_value, walden_value):
  return prod_value is None or walden_value is not None


"""
TEST DEFINITIONS
"""

tests_schema = {
  "works": [
    {
      "display_name": "Title Changed",
      "field": "title",
      "field_type": "string",
      "test_func": length_within_5_percent,
      "test_type": "bug",
      "icon": "mdi-format-title"
    },
    {
      "display_name": "Publication Year Changed",
      "field": "publication_year",
      "field_type": "number",
      "test_func": exact_match,
      "test_type": "bug",
      "icon": "mdi-calendar-month"
    },

    {
      "display_name": "Is OA Changed",
      "field": "primary_location.is_oa",
      "field_type": "boolean",
      "test_func": exact_match,
      "test_type": "bug",
      "icon": "mdi-lock-open-outline"
    },
    {
      "display_name": "OA Lost",
      "field": "primary_location.is_oa",
      "field_type": "boolean",
      "test_func": didnt_become_false,
      "test_type": "bug",
      "icon": "mdi-lock-open-outline"
    },
    {
      "display_name": "OA Became Null",
      "field": "primary_location.is_oa",
      "field_type": "boolean",
      "test_func": didnt_become_null,
      "test_type": "bug",
      "icon": "mdi-lock-open-outline"
    },
    {
      "display_name": "Source ID Lost",
      "field": "primary_location.source.id",
      "field_type": "string",
      "test_func": fill_in_bug,
      "test_type": "bug",
      "icon": "mdi-map-marker-account"
    },
    {
      "display_name": "Source ID Added",
      "field": "primary_location.source.id",
      "field_type": "string",
      "test_func": fill_in_feature,
      "test_type": "feature",
      "icon": "mdi-map-marker-account"
    },
    {
      "display_name": "In DOAJ Changed",
      "field": "primary_location.source.is_in_doaj",
      "field_type": "boolean",
      "test_func": exact_match,
      "test_type": "bug",
      "icon": "mdi-map-marker-check"
    },
    {
      "display_name": "Is Core Changed",
      "field": "primary_location.source.is_core",
      "field_type": "boolean",
      "test_func": exact_match,
      "test_type": "bug",
      "icon": "mdi-map-marker-check"
    },
    {
      "display_name": "Host Organization Changed",
      "field": "primary_location.source.host_organization",
      "field_type": "string",
      "test_func": exact_match,
      "test_type": "bug",
      "icon": "mdi-map-marker-star"
    },

    {
      "display_name": "Best OA Source ID Changed or Lost",
      "field": "best_oa_location.source.id",
      "field_type": "string",
      "test_func": fill_in_bug,
      "test_type": "bug",
      "icon": "mdi-map-marker-account-outline"
    },
    {
      "display_name": "Best OA Source ID Added",
      "field": "best_oa_location.source.id",
      "field_type": "string",
      "test_func": fill_in_feature,
      "test_type": "feature",
      "icon": "mdi-map-marker-account-outline"  
    },
    {
      "display_name": "PDF URL Lost",
      "field": "best_oa_location.source.pdf_url",
      "field_type": "string",
      "test_func": exists_fill_in,
      "test_type": "bug",
      "icon": "mdi-file-pdf-box"
    },
    {
      "display_name": "PDF URL Added",
      "field": "best_oa_location.source.pdf_url",
      "field_type": "string",
      "test_func": fill_in_feature,
      "test_type": "feature",
      "icon": "mdi-file-pdf-box"
    },
    {
      "display_name": "Best OA License Changed or Lost",
      "field": "best_oa_location.source.license",
      "field_type": "string",
      "test_func": fill_in_bug,
      "test_type": "bug",
      "icon": "mdi-license"
    },
    {
      "display_name": "Best OA License Added",
      "field": "best_oa_location.source.license",
      "field_type": "string",
      "test_func": fill_in_feature,
      "test_type": "feature",
      "icon": "mdi-license"
    },
    {
      "display_name": "Best OA Is Published",
      "field": "best_oa_location.source.is_published",
      "field_type": "boolean",
      "test_func": exact_match,
      "test_type": "bug",
      "icon": "mdi-map-marker-check-outline"
    },
    {
      "display_name": "Best OA Is In DOAJ",
      "field": "best_oa_location.source.is_in_doaj",
      "field_type": "boolean",
      "test_func": exact_match,
      "test_type": "bug",
      "icon": "mdi-map-marker-check-outline"
    },

    {
      "display_name": "OA Lost",
      "field": "open_access.is_oa",
      "field_type": "boolean",
      "test_func": didnt_become_false,
      "test_type": "bug",
      "icon": "mdi-lock-open-outline"
    },
    {
      "display_name": "OA Status Change",
      "field": "open_access.oa_status",
      "field_type": "string",
      "test_func": status_equal_except_gold,
      "test_type": "bug",
      "icon": "mdi-lock-percent-open-outline"
    },
    {
      "display_name": "OA Status Found Gold",
      "field": "open_access.oa_status",
      "field_type": "string",
      "test_func": status_became_gold,
      "test_type": "feature",
      "icon": "mdi-lock-percent-open-outline"
    },
    {
      "display_name": "OA Has Fulltext Changed",
      "field": "open_access.any_repository_has_fulltext",
      "field_type": "boolean",
      "test_func": exact_match,
      "test_type": "bug",
      "icon": "mdi-lock-percent-open-outline"
    },

    {
      "display_name": "Language Changed",
      "field": "language",
      "field_type": "string",
      "test_func": fill_in_bug,
      "test_type": "bug",
      "icon": "mdi-translate"
    },
    {
      "display_name": "Language Added",
      "field": "language",
      "field_type": "string",
      "test_func": fill_in_feature,
      "test_type": "feature",
      "icon": "mdi-translate"
    },
    {
      "display_name": "Type Changed",
      "field": "type",
      "field_type": "string",
      "test_func": exact_match,
      "test_type": "bug",
      "icon": "mdi-shape-outline"
    },
    {
      "display_name": "Indexed In Changed",
      "field": "indexed_in",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
      "icon": "mdi-database-outline"
    },
    {
      "display_name": "Is Retracted Changed",
      "field": "is_retracted",
      "field_type": "boolean",
      "test_func": exact_match,
      "test_type": "bug",
      "icon": "mdi-file-excel-outline"
    },
    {
      "display_name": "Location Lost",
      "field": "locations_count",
      "field_type": "number",
      "test_func": greater_than_or_equal,
      "test_type": "bug",
      "icon": "mdi-map-marker-multiple-outline"
    },
    {
      "display_name": "Location Added",
      "field": "locations_count",
      "field_type": "number",
      "test_func": greater_than,
      "test_type": "feature",
      "icon": "mdi-map-marker-multiple-outline"
    },
    {
      "display_name": "Referenced Works Count",
      "field": "referenced_works_count",
      "field_type": "number",
      "test_func": within_5_percent_or_more,
      "test_type": "bug",
      "icon": "mdi-book-arrow-down-outline"
    },
    {
      "display_name": "Related Works",
      "field": "related_works",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
      "icon": "mdi-book-arrow-down-outline"
    },
    {
      "display_name": "Abstract",
      "field": "abstract_inverted_index",
      "field_type": "object",
      "test_func": object_fill_in,
      "test_type": "bug",
      "icon": "mdi-text-box-outline"
    },
    {
      "display_name": "Abstract Added",
      "field": "abstract_inverted_index",
      "field_type": "object",
      "test_func": fill_in_feature,
      "test_type": "feature",
      "icon": "mdi-text-box-outline"
    },
    {
      "display_name": "Grants",
      "field": "grants",
      "field_type": "array",
      "test_func": exact_match,
      "test_type": "bug",
      "icon": "mdi-cash"
    },
    {
      "display_name": "Authorships",
      "field": "authorships",
      "field_type": "array",
      "test_func": count_equals,
      "test_type": "bug",
      "icon": "mdi-account-multiple-outline"
    },
    {
      "display_name": "Authorships IDs",
      "field": "authorships[*].id",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
      "icon": "mdi-account-multiple-check-outline"
    },
    {
      "display_name": "Institutions IDs",
      "field": "authorships[*].institutions[*].id",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
      "icon": "mdi-town-hall"
    },
    {
      "display_name": "Countries",
      "field": "authorships[*].countries",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
      "icon": "mdi-earth"
    },
    {
      "display_name": "Corresponding Author IDs",
      "field": "corresponding_author_ids",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
      "icon": "mdi-account-check-outline"
    },

    {
      "display_name": "APC List",
      "field": "apc_list",
      "field_type": "number",
      "test_func": exact_match,
      "test_type": "bug",
      "icon": "mdi-currency-usd"
    },
    {
      "display_name": "APC Paid",
      "field": "apc_paid",
      "field_type": "number",
      "test_func": exact_match,
      "test_type": "bug",
      "icon": "mdi-currency-usd"
    },

    {
      "display_name": "Primary Topic ID",
      "field": "primary_topic.id",
      "field_type": "string",
      "test_func": exact_match,
      "test_type": "bug",
      "icon": "mdi-tag-outline"
    },
    {
      "display_name": "Topic IDs",
      "field": "topics[*].id",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
      "icon": "mdi-tag-text-outline"
    },
    {
      "display_name": "Keywords Lost",
      "field": "keywords",
      "field_type": "array",
      "test_func": exists_fill_in,
      "test_type": "bug",
      "icon": "mdi-alpha-k"
    },
    {
      "display_name": "Keywords Added",
      "field": "keywords",
      "field_type": "array",
      "test_func": fill_in_feature,
      "test_type": "feature",
      "icon": "mdi-alpha-k"
    },
    {
      "display_name": "Concept IDs",
      "field": "concepts[*].id",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
      "icon": "mdi-lightbulb-outline"
    },
    {
      "display_name": "SDG IDs",
      "field": "sustainable_development_goals[*].id",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
      "icon": "mdi-sprout-outline"
    },
  ]
}

"""
Notes
- primary_location.is_oa vs open_access.is_oa?

"""