schema = {
  "works": {
    "abstract_inverted_index": "object",
    "authorships": "array|<5%",
    "apc_list": "object",
    "apc_paid": "object",
    "best_oa_location.source.display_name": "string",
    "best_oa_location.source.type": "string",
    "best_oa_location.source.is_oa": "boolean",
    "best_oa_location.source.is_in_doaj": "boolean",
    "best_oa_location.source.version": "string",
    "best_oa_location.source.license": "string",
    "biblio": "object",
    "citation_normalized_percentile": "object",
    "cited_by_api_url": "string",
    "cited_by_count": "number|<5%",
    "concepts": "array",
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
    "keywords": "array",
    "language": "string",
    "license": "string",
    "locations": "array|≥",
    "locations_count": "number|≥",
    "mesh": "array",
    "open_access": "object",
    "open_access.oa_status": "string",
    "primary_location.source.display_name": "string",
    "primary_location.source.type": "string",
    "primary_location.source.is_oa": "boolean",
    "primary_location.source.is_in_doaj": "boolean",
    "primary_location.source.version": "string",
    "primary_location.source.license": "string",
    "primary_topic": "object",
    "primary_topic.id": "string",
    "publication_date": "string",
    "publication_year": "number",
    "referenced_works_count": "number|<5%",
    "referenced_works": "array",
    "related_works": "array",
    "sustainable_development_goals": "array",
    "topics": "array",
    "title": "string",
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
    "doi",
    "authorships",
    "locations",
    "primary_topic.id",
    "institutions_distinct_count",
    "referenced_works_count",
    "cited_by_count",
  ]
}

sum_fields = {
  "works": [
    "referenced_works",
    "locations",
  ]
}