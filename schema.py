"""
TEST FUNCTIONS
"""

def exact_match(prod_value, walden_value):
  return prod_value == walden_value


def greater_than(prod_value, walden_value):
  return prod_value > walden_value


def greater_than_or_equal(prod_value, walden_value):
  return prod_value >= walden_value


def within_5_percent(prod_value, walden_value):  
  if prod_value == 0 and walden_value == 0:
      return True

  if prod_value == 0:
      return False

  return abs((walden_value - prod_value) / prod_value * 100) <= 5


def within_5_percent_or_more(prod_value, walden_value):
  return walden_value > prod_value or within_5_percent(prod_value, walden_value)


def count_within_5_percent(prod_value, walden_value):
  return within_5_percent(len(prod_value), len(walden_value))


def length_within_5_percent(prod_value, walden_value):
  return within_5_percent(len(prod_value), len(walden_value))


def count_equals(prod_value, walden_value):
  return len(prod_value) == len(walden_value)


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


def deep_equals(obj1, obj2):
    """Deep equality comparison for lists and dicts"""
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


def object_fill_in(prod_value, walden_value):
  return deep_equals(prod_value, walden_value) or (prod_value is None and walden_value is not None)


def exists_fill_in(prod_value, walden_value):
  return prod_value is None or walden_value is not None


"""
TEST DEFINITIONS
"""

tests = {
  "works": [
    {
      "display_name": "Title Changed",
      "field": "title",
      "field_type": "string",
      "test_func": length_within_5_percent,
      "test_type": "bug",
    },
    {
      "display_name": "Publication Year Changed",
      "field": "publication_year",
      "field_type": "number",
      "test_func": exact_match,
      "test_type": "bug",
    },

    {
      "display_name": "Is OA Changed",
      "field": "primary_location.is_oa",
      "field_type": "boolean",
      "test_func": exact_match,
      "test_type": "bug",
    },
    {
      "display_name": "OA Lost",
      "field": "primary_location.is_oa",
      "field_type": "boolean",
      "test_func": didnt_become_false,
      "test_type": "bug",
    },
    {
      "display_name": "OA Became Null",
      "field": "primary_location.is_oa",
      "field_type": "boolean",
      "test_func": didnt_become_null,
      "test_type": "bug",
    },
    {
      "display_name": "Source ID Lost",
      "field": "primary_location.source.id",
      "field_type": "string",
      "test_func": fill_in_bug,
      "test_type": "bug",
    },
    {
      "display_name": "Source ID Added",
      "field": "primary_location.source.id",
      "field_type": "string",
      "test_func": fill_in_feature,
      "test_type": "feature",
    },
    {
      "display_name": "In DOAJ Changed",
      "field": "primary_location.source.is_in_doaj",
      "field_type": "boolean",
      "test_func": exact_match,
      "test_type": "bug",
    },
    {
      "display_name": "Is Core Changed",
      "field": "primary_location.source.is_core",
      "field_type": "boolean",
      "test_func": exact_match,
      "test_type": "bug",
    },
    {
      "display_name": "Host Organization Changed",
      "field": "primary_location.source.host_organization",
      "field_type": "string",
      "test_func": exact_match,
      "test_type": "bug",
    },

    {
      "display_name": "Best OA Source ID Changed or Lost",
      "field": "best_oa_location.source.id",
      "field_type": "string",
      "test_func": fill_in_bug,
      "test_type": "bug",
    },
    {
      "display_name": "Best OA Source ID Added",
      "field": "best_oa_location.source.id",
      "field_type": "string",
      "test_func": fill_in_feature,
      "test_type": "feature",
    },
    {
      "display_name": "PDF URL Lost",
      "field": "best_oa_location.source.pdf_url",
      "field_type": "string",
      "test_func": exists_fill_in,
      "test_type": "bug",
    },
    {
      "display_name": "PDF URL Added",
      "field": "best_oa_location.source.pdf_url",
      "field_type": "string",
      "test_func": fill_in_feature,
      "test_type": "feature",
    },
    {
      "display_name": "Best OA License Changed or Lost",
      "field": "best_oa_location.source.license",
      "field_type": "string",
      "test_func": fill_in_bug,
      "test_type": "bug",
    },
    {
      "display_name": "Best OA License Added",
      "field": "best_oa_location.source.license",
      "field_type": "string",
      "test_func": fill_in_feature,
      "test_type": "feature",
    },
    {
      "display_name": "Best OA Is Published",
      "field": "best_oa_location.source.is_published",
      "field_type": "boolean",
      "test_func": exact_match,
      "test_type": "bug",
    },
    {
      "display_name": "Best OA Is In DOAJ",
      "field": "best_oa_location.source.is_in_doaj",
      "field_type": "boolean",
      "test_func": exact_match,
      "test_type": "bug",
    },

    {
      "display_name": "OA Lost",
      "field": "open_access.is_oa",
      "field_type": "boolean",
      "test_func": didnt_become_false,
      "test_type": "bug",
    },
    {
      "display_name": "OA Status Change",
      "field": "open_access.oa_status",
      "field_type": "string",
      "test_func": status_equal_except_gold,
      "test_type": "bug",
    },
    {
      "display_name": "OA Status Found Gold",
      "field": "open_access.oa_status",
      "field_type": "string",
      "test_func": status_became_gold,
      "test_type": "feature",
    },
    {
      "display_name": "OA Has Fulltext Changed",
      "field": "open_access.any_repository_has_fulltext",
      "field_type": "boolean",
      "test_func": exact_match,
      "test_type": "bug",
    },

    {
      "display_name": "Language Changed",
      "field": "language",
      "field_type": "string",
      "test_func": fill_in_bug,
      "test_type": "bug",
    },
    {
      "display_name": "Language Added",
      "field": "language",
      "field_type": "string",
      "test_func": fill_in_feature,
      "test_type": "feature",
    },
    {
      "display_name": "Type Changed",
      "field": "type",
      "field_type": "string",
      "test_func": exact_match,
      "test_type": "bug",
    },
    {
      "display_name": "Indexed In Changed",
      "field": "indexed_in",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
    },
    {
      "display_name": "Is Retracted Changed",
      "field": "is_retracted",
      "field_type": "boolean",
      "test_func": exact_match,
      "test_type": "bug",
    },
    {
      "display_name": "Location Lost",
      "field": "locations_count",
      "field_type": "number",
      "test_func": greater_than_or_equal,
      "test_type": "bug",
    },
    {
      "display_name": "Location Added",
      "field": "locations_count",
      "field_type": "number",
      "test_func": greater_than,
      "test_type": "feature",
    },
    {
      "display_name": "Referenced Works Count",
      "field": "referenced_works_count",
      "field_type": "number",
      "test_func": within_5_percent_or_more,
      "test_type": "bug",
    },
    {
      "display_name": "Related Works",
      "field": "related_works",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
    },
    {
      "display_name": "Abstract",
      "field": "abstract_inverted_index",
      "field_type": "object",
      "test_func": object_fill_in,
      "test_type": "bug",
    },
    {
      "display_name": "Abstract Added",
      "field": "abstract_inverted_index",
      "field_type": "object",
      "test_func": fill_in_feature,
      "test_type": "feature",
    },
    {
      "display_name": "Grants",
      "field": "grants",
      "field_type": "array",
      "test_func": deep_equals,
      "test_type": "bug",
    },
    {
      "display_name": "Authorships",
      "field": "authorships",
      "field_type": "array",
      "test_func": count_equals,
      "test_type": "bug",
    },
    {
      "display_name": "Authorships IDs",
      "field": "authorships[*].id",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
    },
    {
      "display_name": "Institutions IDs",
      "field": "authorships[*].institutions[*].id",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
    },
    {
      "display_name": "Countries",
      "field": "authorships[*].countries",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
    },
    {
      "display_name": "Corresponding Author IDs",
      "field": "corresponding_author_ids",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
    },

    {
      "display_name": "APC List",
      "field": "apc_list",
      "field_type": "number",
      "test_func": exact_match,
      "test_type": "bug",
    },
    {
      "display_name": "APC Paid",
      "field": "apc_paid",
      "field_type": "number",
      "test_func": exact_match,
      "test_type": "bug",
    },

    {
      "display_name": "Primary Topic ID",
      "field": "primary_topic.id",
      "field_type": "string",
      "test_func": exact_match,
      "test_type": "bug",
    },
    {
      "display_name": "Topic IDs",
      "field": "topics[*].id",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
    },
    {
      "display_name": "Keywords Lost",
      "field": "keywords",
      "field_type": "array",
      "test_func": exists_fill_in,
      "test_type": "bug",
    },
    {
      "display_name": "Keywords Added",
      "field": "keywords",
      "field_type": "array",
      "test_func": fill_in_feature,
      "test_type": "feature",
    },
    {
      "display_name": "Concept IDs",
      "field": "concepts[*].id",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
    },
    {
      "display_name": "SDG IDs",
      "field": "sustainable_development_goals[*].id",
      "field_type": "array",
      "test_func": set_equals,
      "test_type": "bug",
    },
  ]
}

"""
Notes
- primary_location.is_oa vs open_access.is_oa?

"""