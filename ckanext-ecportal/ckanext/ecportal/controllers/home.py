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


import ckanext.ecportal.helpers as ckanext_helpers

import time
from ckan.common import OrderedDict, c, g, request, _, response
from odp_common.mdr.controlled_vocabulary_factory import ControlledVocabularyFactory
from odp_common.mdr.controlled_vocabulary import CorporateBodiesUtil
import ckan.lib.helpers as h
import ckan.logic as logic
get_action = logic.get_action
import ckan.lib.base as base
abort = base.abort
import logging
log = logging.getLogger(__name__)
def _encode_params(params):
    return [(k, v.encode('utf-8') if isinstance(v, basestring)
            else str(v))
            for k, v in params]
class ECODPHomeController(base.BaseController):
    def index(self):
        context = {'for_view': True}

        start = time.time()
        locale = ckanext_helpers.current_locale().language
        c.package_count = ckanext_helpers.get_package_count()
        c.approved_search_terms = ckanext_helpers.approved_search_terms()
        c.most_viewed_datasets = ckanext_helpers.most_viewed_datasets()
        c.recent_updates = ckanext_helpers.recent_updates(10)

        publishers = get_action('get_skos_hierarchy')(context, None)
        factory = ControlledVocabularyFactory()
        publ_mdr = factory.get_controlled_vocabulary_util(ControlledVocabularyFactory.CORPORATE_BODY) #type: CorporateBodiesUtil
        for top_level, item in publishers.items():
            translation = publ_mdr.get_translation_for_language(top_level, locale)
            item['name'] = top_level.split('/')[-1].lower()
            item['label'] = translation
            interim = []
            for child in item.get('children', []):
                translation = publ_mdr.get_translation_for_language(child[0], locale)
                interim.append((child[0].split('/')[-1].lower(), translation, child[1]))
            item['children'] = sorted(interim, key=lambda child: child[1])
        c.get_skos_hierarchy = publishers
        c.most_common_themes = get_action('theme_list')(context, {'mode': 'most_common'})
        c.less_common_themes = get_action('theme_list')(context, {'mode': 'less_common'})
        #c.get_eurovoc_domains_by_packages_with_cache_most =homepage.get_eurovoc_domains_by_packages_with_cache('most_common', locale)
        #c.get_eurovoc_domains_by_packages_with_cache_less= homepage.get_eurovoc_domains_by_packages_with_cache('less_common', locale)

        duration = time.time()-start
        log.info("Build all cache took {0}".format(duration))
        if c.userobj is not None:
            msg = None
            url = h.url_for(controller='user', action='edit')
            is_google_id = \
                c.userobj.name.startswith(
                    'https://www.google.com/accounts/o8/id')
            if not c.userobj.email and (is_google_id and
                                        not c.userobj.fullname):
                msg = _(u'Please <a href="{link}">update your profile</a>'
                        u' and add your email address and your full name. '
                        u'{site} uses your email address'
                        u' if you need to reset your password.'.format(
                            link=url, site=g.site_title))
            elif not c.userobj.email:
                msg = _('Please <a href="%s">update your profile</a>'
                        ' and add your email address. ') % url + \
                    _('%s uses your email address'
                        ' if you need to reset your password.') \
                    % g.site_title
            elif is_google_id and not c.userobj.fullname:
                msg = _('Please <a href="%s">update your profile</a>'
                        ' and add your full name.') % (url)
            if msg:
                h.flash_notice(msg, allow_html=True)
        log.info("Use Home extension")
        start = time.time()
        response_str = base.render('home/index.html', cache_force=True)
        duration = time.time() - start
        log.info("Build Render index  took {0}".format(duration))
        # request.environ['CKAN_PAGE_CACHABLE'] = True
        # response.headers["Cache-Control"] = "max-age=604800"
        return response_str
        # return base.render('home/static.html', cache_force=True)