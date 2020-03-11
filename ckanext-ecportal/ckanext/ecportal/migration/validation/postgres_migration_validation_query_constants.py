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
select  
case when private then 'private' else 'public' end as datasets, count(private) from package 
where state = 'active' group by private;
"""

NUMBER_DATASETS_PER_PUBLISHER = """
select gr.name, count(*) as count from package as ds
JOIN public.group as gr on
ds.owner_org = gr.id 
where ds.state = 'active' 
GROUP BY gr.name order by count DESC;
"""

NUMBER_RESOURCES_PER_DATASET = """
select pr.name, count(rr.id)
from package pr
join resource_group rg on rg.package_id = pr.id and pr.state = 'active' and pr.private = false
join resource rr on rr.resource_group_id = rg.id
where  rr.state = 'active' and rg.state = 'active'
and (rr.resource_type not in ('http://data.europa.eu/euodp/kos/documentation-type/MainDocumentation',
    'http://data.europa.eu/euodp/kos/documentation-type/RelatedWebPage',
    'http://data.europa.eu/euodp/kos/documentation-type/RelatedDocumentation') or rr.resource_type is null and rr.extras not like '%documentation-type%')
group by pr.name order by pr.name asc
;
"""

NUMBER_DOCUMENTS_PER_DATASET = """
select pr.name, count(rr.id)
from package pr
join resource_group rg on rg.package_id = pr.id and pr.state = 'active' and pr.private = false
join resource rr on rr.resource_group_id = rg.id
where  rr.state = 'active' and rg.state = 'active'
and (rr.resource_type in ('http://data.europa.eu/euodp/kos/documentation-type/MainDocumentation',
    'http://data.europa.eu/euodp/kos/documentation-type/RelatedWebPage',
    'http://data.europa.eu/euodp/kos/documentation-type/RelatedDocumentation') or rr.resource_type is null and rr.extras like '%documentation-type%')
group by pr.name order by pr.name asc
;
"""

NUMBER_DATASETS_PER_EUROVOC_DOMAIN = """
select count(public.group.type) from package 
join member on
(package.id = member.table_id and member.state = 'active' and package.state = 'active') 
join public.group on 
(public.group.id = member.group_id and public.group.type = 'eurovoc_domain' and public.group.title in (:domain_list)) 
"""

NUMBER_DATASETS_PER_GROUP = """
select public.group.name, count(public.group.type) from package
join member on 
(package.id = member.table_id and package.state = 'active' and member.state='active') 
join public.group on
(public.group.id = member.group_id and public.group.type = 'group' and public.group.state='active')
group by public.group.name order by name asc
"""

NUMBER_EUROVOC_CONCEPT_PER_DATASET = """
select package.name, count(tag) from package 
join package_tag on 
(package.id = package_tag.package_id and package_tag.state='active'  and package.state = 'active') 
join tag on (package_tag.tag_id = tag.id and tag.vocabulary_id = 'dbfd15ac-a514-4fa0-b3ef-1167c493b831') 
group by package.name order by name asc
"""

NUMBER_EUROVOC_DOMAINS_PER_DATASET = """
select package.name, count(public.group.type) from package
join member on
(package.id = member.table_id and package.state = 'active' and member.state = 'active')
join public.group on
(public.group.id = member.group_id and public.group.type = 'eurovoc_domain' and public.group.title in (:domain_list))
group by package.name order by name asc
;
"""

NUMBER_KEYWORDS_PER_DATASET = """
select package.name, count(DISTINCT(tag.name)) + count(DISTINCT(coalesce(term_translation.term_translation || term_translation.lang_code, term_translation.term))) as num_key from package
join package_tag on
(package.id = package_tag.package_id and package_tag.state='active' and package.state = 'active')
join tag on
(package_tag.tag_id = tag.id and tag.vocabulary_id isnull)
left join term_translation on (term_translation.term = tag.name)
group by package.name ORDER BY num_key desc
"""

NUMBER_CONTACT_POINT_ELEMENTS_PER_DATASET = """
select name, count(package_extra) from package 
join package_extra on 
(package.id = package_extra.package_id and package.state = 'active') 
where (key = 'contact_name' or key = 'contact_address' or key = 'contact_webpage' or key = 'contact_email') and (value != '') 
group by name order by name asc
"""

NUMBER_NAMES_PER_DATASET = """
select name, count(name) from package 
where state = 'active' 
group by name order by name asc;
"""

NUMBER_MAIN_TITLES_PER_DATASET = """
select name, count(title) from package
where state = 'active' 
group by name order by name asc;
"""

NUMBER_TRANSLATED_TITLES_PER_DATASET = """
select name, count(term) from package 
join term_translation on 
(package.title = term_translation.term and package.state = 'active')
group by name order by name asc;
"""

NUMBER_MAIN_DESCRIPTIONS_PER_DATASET = """
select name, count(notes) from package 
where state = 'active' 
group by name order by name asc;
"""

NUMBER_TRANSLATED_DESCRIPTIONS_PER_DATASET = """
select name, count(term) from package 
join term_translation on
(package.notes = term_translation.term and package.state = 'active') 
group by name order by name asc;
"""

DATASET_TITLE_WITH_TRANSLATIONS = """
select package.name, package.title, term_translation.term_translation
from package
LEFT JOIN term_translation on term_translation.term = package.title
where package.state = 'active'
order by package.name
"""

DATASET_DESCRIPTION_WITH_TRANSLATIONS = """
select package.name, package.notes
from package
where package.state = 'active'
UNION
select package.name, term_translation.term_translation
from package
JOIN term_translation on term_translation.term = package.notes
where package.state = 'active'
"""


DATASET_TAGS_WITH_TRANSLATIONS = """
select package.name, tag.name, term_translation.term_translation  from package
join package_tag on
(package.id = package_tag.package_id and package_tag.state='active' and package.state = 'active')
join tag on
(package_tag.tag_id = tag.id and tag.vocabulary_id isnull)
left join term_translation on (term_translation.term = tag.name)
order by package.name
"""

DATASET_ALTERNATIVE_TITLES = """
SELECT package.name AS package_name , package_extra.value
FROM package
join package_extra on package_extra.package_id = package.id and package_extra.key = 'alternative_title' and package_extra.value != '' and package.state = 'active'
UNION
SELECT package.name AS package_name ,term_translation.term_translation
FROM package
join package_extra on package_extra.package_id = package.id and package_extra.key = 'alternative_title' and package_extra.value != '' and package.state = 'active'
join term_translation on term_translation.term = package_extra.value
"""
