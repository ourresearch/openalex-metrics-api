"""
Test Types
"=" - exact match (default)
"≥" - greater than or equal to
"<5%" - count or number plus/minus 5%
"-5%+" - count or number within -5% or greater
"count =" - count is equal
"set =" - set equality
"len <5%" - length within 5%
"fill-in" - either exact match, or prod is null and walden is not null
"exists-fill-in" - if prod is non-null, walden must be non-null
"""


schema = {
  "works": {
    "abstract_inverted_index": "object|fill-in",
    "authorships": "array|count =",
    "authorships.id": "array|set =",
    "authorships.institutions.id": "array|set =",
    "authorships.countries": "array|set =",
    "apc_list": "object",
    "apc_list.value_usd": "number",
    "apc_paid": "object",
    "apc_paid.value_usd": "number",
    "best_oa_location.source.id": "string|fill-in",
    "best_oa_location.source.pdf_url": "string|exists-fill-in",
    "best_oa_location.source.license": "string|fill-in",
    "best_oa_location.source.is_accepted": "boolean",
    "best_oa_location.source.is_published": "boolean",
    "best_oa_location.source.is_in_doaj": "boolean",
    "best_oa_location.source.type": "string",
    "best_oa_location.source.version": "string",
    "biblio": "object",
    "citation_normalized_percentile": "object",
    "cited_by_api_url": "string",
    "cited_by_count": "number|<5%",
    "concepts": "array",
    "concepts.id": "array|set =",
    "corresponding_author_ids": "array",
    "corresponding_institution_ids": "array",
    "countries_distinct_count": "number",
    "counts_by_year": "array",
    "created_date": "string",
    "display_name": "string",
    "doi": "string",
    "fulltext_origin": "string",
    "fwci": "number",
    "grants": "array",
    "has_fulltext": "boolean",
    "id": "string",
    "ids": "object",
    "indexed_in": "array",
    "institutions_distinct_count": "number|<5%",
    "is_paratext": "boolean",
    "is_retracted": "boolean",
    "keywords": "array|exists-fill-in",
    "language": "string|fill-in",
    "license": "string",
    "locations": "array|≥",
    "locations_count": "number|≥",
    "open_access": "object",
    "open_access.is_oa": "boolean",
    "open_access.oa_status": "string",
    "open_access.any_repository_has_fulltext": "boolean",
    "primary_location.is_oa": "boolean",
    "primary_location.source.id": "string|fill-in",
    "primary_location.source.is_in_doaj": "boolean",
    "primary_location.source.is_core": "boolean",
    "primary_location.source.is_indexed_in_scopus": "boolean",
    "primary_location.source.host_organization": "string",
    "primary_location.source.type": "string",
    "primary_location.source.version": "string",
    "primary_location.source.license": "string",
    "primary_topic": "object",
    "primary_topic.id": "string",
    "publication_date": "string",
    "publication_year": "number",
    "referenced_works_count": "number|-5%+",
    "referenced_works": "array",
    "related_works": "array|set =",
    "sustainable_development_goals": "array",
    "sustainable_development_goals.id": "array|set =",
    "topics": "array",
    "topics.id": "array|set =",
    "title": "string|len <5%",
    "type": "string",
    "type_crossref": "string",
  },
  "authors": {
    "orcid": "string",
  },
  "sources": {
    "issn_l": "string",
  },
  "institutions": {
    "ror": "string",
  },
  "publishers": {
    "ids.wikidata": "string",
  },
}

canonical_ids = {
    "works": "doi",
    "authors": "orcid",
    "sources": "issn_l",
    "institutions": "ror",
    "publishers": "ids.wikidata",
}

test_fields = {
  "works": [
    "title",
    "publication_year",

    "primary_location.is_oa",
    "primary_location.source.id",
    "primary_location.source.is_in_doaj",
    "primary_location.source.is_core",
    "primary_location.source.is_indexed_in_scopus",
    "primary_location.source.host_organization",

    "best_oa_location.source.id",
    "best_oa_location.source.pdf_url",
    "best_oa_location.source.license",
    "best_oa_location.source.is_accepted",
    "best_oa_location.source.is_published",
    "best_oa_location.source.is_in_doaj",

    "open_access.is_oa",
    "open_access.oa_status",
    "open_access.any_repository_has_fulltext",

    "language",
    "type",
    "indexed_in",
    "is_retracted",
    "locations_count",
    "referenced_works_count",
    "related_works",
    "abstract_inverted_index",
    "grants",

    "authorships",
    "authorships.id",
    "authorships.institutions.id",
    "authorships.countries",
    "corresponding_author_ids",

    "apc_list.value_usd",
    "apc_paid.value_usd",

    "primary_topic.id",
    "topics.id",
    "keywords",
    "concepts.id",
    "sustainable_development_goals.id",
  ]
}

sum_fields = {
  "works": [
    "referenced_works",
    "locations",
  ]
}