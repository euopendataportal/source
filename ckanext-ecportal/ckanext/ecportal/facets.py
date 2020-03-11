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

import ckan.plugins as p
from ckan.common import OrderedDict, _

class ECPortalFacets(p.SingletonPlugin):
    p.implements(p.IFacets)

    def _common_facets(self, facets_dict):
        facets_dict['vocab_catalog']=u'ecodp.common.facet.vocab_catalog'
        facets_dict['vocab_theme']=u'ecodp.common.facet.theme'
        facets_dict['groups']=u'ecodp.common.facet.groups'
        facets_dict['organization']=u'ecodp.common.facet.publishers'
        facets_dict['vocab_concepts_eurovoc']=u'ecodp.common.eurovoc_concepts'
        facets_dict['tags']=u'ecodp.common.facet.keywords'
        facets_dict['res_format']=u'ecodp.common.facet.formats'
        facets_dict['vocab_geographical_coverage']=u'ecodp.common.facet.geographical_coverage'
        facets_dict['vocab_language']=u'ecodp.common.language'
        return facets_dict

    def dataset_facets(self, facets_dict, package_type):
        facets_dict = OrderedDict()
        facets_dict = self._common_facets(facets_dict)
        return facets_dict

    def group_facets(self, facets_dict, group_type, package_type):
        facets_dict = OrderedDict()
        facets_dict = self._common_facets(facets_dict)
        return facets_dict

    def organization_facets(self, facets_dict, organization_type, package_type):
        facets_dict = OrderedDict()
        facets_dict = self._common_facets(facets_dict)
        return facets_dict

    def dashboard_facets(self, facets_dict, package_type):
        facets_dict = OrderedDict()
        facets_dict['capacity']=u'ecodp.common.privacy_state'
        facets_dict = self._common_facets(facets_dict)
        return facets_dict