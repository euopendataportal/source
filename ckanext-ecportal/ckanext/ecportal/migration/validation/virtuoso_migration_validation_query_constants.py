#    Copyright (C) <2018>  <Publications Office of the European Union>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#    contact: <https://publications.europa.eu/en/web/about-us/contact>

COUNT_ALL_DATASETS_QUERY = """
prefix g1: <dcatapop-public>
prefix g2: <dcatapop-private>

SELECT (count(?s1) as ?number_public_datasets) (count(?s2) AS ?number_private_datasets)
{
  {
    GRAPH g1: {
      ?s1 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/dcat#Dataset>
    }
  } UNION {
    GRAPH g2: {
      ?s2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://www.w3.org/ns/dcat#Dataset>
    }
  }
} 
"""

NUMBER_DATASETS_PER_PUBLISHER = """
select (count(DISTINCT ?s) as ?count) ?pub FROM <dcatapop-public> from <dcatapop-private> where 
{
   {
      ?s ?p ?o .  ?s a <http://www.w3.org/ns/dcat#Dataset> .  
      ?s <http://purl.org/dc/terms/publisher> ?pub
   }
} GROUP BY ?pub ORDER BY DESC(?count)
"""

NUMBER_RESOURCES_PER_DATASET = """
select ?uri, count(?resource) as ?number_resources from <dcatapop-public> from <dcatapop-private> where
{
   ?uri <http://www.w3.org/ns/dcat#distribution> ?o . 
   ?o <http://www.w3.org/ns/dcat#accessURL> ?resource
} order by asc(?uri)
"""

NUMBER_DOCUMENTS_PER_DATASET = """
select ?uri, count(?document) as ?number_documents from <dcatapop-public> from <dcatapop-private> where 
{
   ?uri <http://xmlns.com/foaf/0.1/page> ?o . 
   ?o <http://schema.org/url> ?document
} order by asc(?uri)
"""

NUMBER_DATASETS_PER_EUROVOC_DOMAIN = """
select ?eurovoc_domain count(distinct ?s) as ?number_datasets from <dcatapop-public> from <dcatapop-private> where 
{
   ?s <http://www.w3.org/ns/dcat#theme> ?eurovoc_domain
} order by ?eurovoc_domain
"""

NUMBER_DATASETS_PER_GROUP = """
select ?group count(distinct ?s) as ?number_datasets from <dcatapop-public> from <dcatapop-private> where
{
   ?s <http://data.europa.eu/88u/ontology/dcatapop#datasetGroup> ?group 
} order by ?group 
"""

NUMBER_EUROVOC_CONCEPT_PER_DATASET = """
select ?uri count(distinct ?o) as ?number_eurovoc_concepts from <dcatapop-public> from <dcatapop-private> where
{
   ?uri <http://purl.org/dc/terms/subject> ?o
} order by asc(?uri)
"""

NUMBER_EUROVOC_DOMAINS_PER_DATASET = """
select ?uri count(distinct ?o) as ?number_eurovoc_domains from <dcatapop-public> from <dcatapop-private> where 
{
   ?uri <http://www.w3.org/ns/dcat#theme> ?o
} order by asc(?uri)
"""

NUMBER_KEYWORDS_PER_DATASET = """
select ?uri count(distinct ?o) as ?number_keywords from <dcatapop-public> from <dcatapop-private> where 
{
   ?uri <http://www.w3.org/ns/dcat#keyword> ?o
} order by asc(?uri)
"""

NUMBER_CONTACT_POINT_ELEMENTS_PER_DATASET = """
select ?dataset (count(?pub) + count(?o)) as ?number_contact_elements FROM <dcatapop-public> from <dcatapop-private> where 
{
  {
    ?dataset <http://www.w3.org/ns/dcat#contactPoint> ?kind . 
    ?kind <http://www.w3.org/2006/vcard/ns#hasEmail>|<http://www.w3.org/2006/vcard/ns#organisation-name> ?pub .
  }
  union 
  {
    ?dataset <http://www.w3.org/ns/dcat#contactPoint> ?kind . 
    ?kind <http://www.w3.org/2006/vcard/ns#hasAddress>|<http://xmlns.com/foaf/0.1/homePage> ?contact_element .
    ?contact_element ?p ?o filter isLiteral(?o)
  }
} order by ?dataset
"""

NUMBER_NAMES_PER_DATASET = """
select ?uri count(distinct ?package_name) as ?number_names from <dcatapop-public> from <dcatapop-private> where
{
   ?uri ?p <http://www.w3.org/ns/dcat#Dataset> .
   ?uri <http://data.europa.eu/88u/ontology/dcatapop#ckanName> ?package_name
}  order by asc(?uri)
"""

NUMBER_MAIN_TITLES_PER_DATASET = """
select ?uri count(distinct ?english_title) as ?number_titles from <dcatapop-public>  from <dcatapop-private> where
{
   ?uri ?p <http://www.w3.org/ns/dcat#Dataset> .
   ?uri <http://purl.org/dc/terms/title> ?english_title .
   FILTER (lang(?english_title) = 'en')
}  order by asc(?uri)"""

NUMBER_TRANSLATED_TITLES_PER_DATASET = """
select ?uri count(distinct ?title) as ?number_titles from <dcatapop-public> from <dcatapop-private> where
{
   ?uri ?p <http://www.w3.org/ns/dcat#Dataset> .
   ?uri <http://purl.org/dc/terms/title> ?title .
   FILTER (lang(?title) != 'en')
} order by asc(?uri)
"""

NUMBER_MAIN_DESCRIPTIONS_PER_DATASET = """
select ?uri count(distinct ?description) as ?number_descriptions from <dcatapop-public> from <dcatapop-private> where
{
   ?uri ?p <http://www.w3.org/ns/dcat#Dataset> .
   ?uri <http://purl.org/dc/terms/description> ?description .
   FILTER (lang(?description) = 'en')
} order by asc(?uri)
"""

NUMBER_TRANSLATED_DESCRIPTIONS_PER_DATASET = """
select ?uri count(distinct ?description) as ?number_descriptions from <dcatapop-public> from <dcatapop-private> where
{
   ?uri ?p <http://www.w3.org/ns/dcat#Dataset> .
   ?uri <http://purl.org/dc/terms/description> ?description .
   FILTER (lang(?description) != 'en')
} order by asc(?uri)
"""
