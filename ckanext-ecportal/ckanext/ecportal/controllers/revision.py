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

from datetime import datetime, timedelta

from pylons.i18n import get_lang

import ckan.controllers.revision as revision
import ckan.lib.base as base
import ckan.model as model
import ckan.lib.helpers as h
import ckanext.ecportal.lib.page_util as page_util

from ckan.common import _, c, request


class ECODPRevisionController(revision.RevisionController):

    def index(self):
        return self.list()

    def list(self):
        format = request.params.get('format', '')
        if format == 'atom':
            # Generate and return Atom 1.0 document.
            from webhelpers.feedgenerator import Atom1Feed
            feed = Atom1Feed(
                title=_(u'CKAN Repository Revision History'),
                link=h.url_for(controller='revision', action='list', id=''),
                description=_(u'Recent changes to the CKAN repository.'),
                language=unicode(get_lang()),
            )
            # TODO: make this configurable?
            # we do not want the system to fall over!
            maxresults = 200
            try:
                dayHorizon = int(request.params.get('days', 5))
            except:
                dayHorizon = 5
            ourtimedelta = timedelta(days=-dayHorizon)
            since_when = datetime.now() + ourtimedelta
            revision_query = model.repo.history()
            revision_query = revision_query.filter(
                model.Revision.timestamp >= since_when).filter(
                    model.Revision.id != None)
            revision_query = revision_query.limit(maxresults)
            for revision in revision_query:
                package_indications = []
                revision_changes = model.repo.list_changes(revision)
                resource_revisions = revision_changes[model.Resource]
                resource_group_revisions = \
                    revision_changes[model.ResourceGroup]
                package_extra_revisions = revision_changes[model.PackageExtra]
                for package in revision.packages:
                    if not package:
                        # package is None sometimes - I don't know why,
                        # but in the meantime while that is fixed,
                        # avoid an exception here
                        continue
                    if package.private:
                        continue
                    number = len(package.all_revisions)
                    package_revision = None
                    count = 0
                    for pr in package.all_revisions:
                        count += 1
                        if pr.revision.id == revision.id:
                            package_revision = pr
                            break
                    if package_revision and package_revision.state == \
                            model.State.DELETED:
                        transition = 'deleted'
                    elif package_revision and count == number:
                        transition = 'created'
                    else:
                        transition = 'updated'
                        for resource_revision in resource_revisions:
                            if resource_revision.continuity.resource_group.\
                                    package_id == package.id:
                                transition += ':resources'
                                break
                        for resource_group_revision in \
                                resource_group_revisions:
                            if resource_group_revision.package_id == \
                                    package.id:
                                transition += ':resource_group'
                                break
                        for package_extra_revision in package_extra_revisions:
                            if package_extra_revision.package_id == \
                                    package.id:
                                if package_extra_revision.key == \
                                        'date_updated':
                                    transition += ':date_updated'
                                    break
                    indication = "%s:%s" % (package.name, transition)
                    package_indications.append(indication)
                pkgs = u'[%s]' % ' '.join(package_indications)
                item_title = u'r%s ' % (revision.id)
                item_title += pkgs
                if revision.message:
                    item_title += ': %s' % (revision.message or '')
                item_link = h.url_for(controller='revision', action='read', id=revision.id)
                item_description = _('Datasets affected: %s.\n') % pkgs
                item_description += '%s' % (revision.message or '')
                item_author_name = revision.author
                item_pubdate = revision.timestamp
                feed.add_item(
                    title=item_title,
                    link=item_link,
                    description=item_description,
                    author_name=item_author_name,
                    pubdate=item_pubdate,
                )
            feed.content_type = 'application/atom+xml'
            return feed.writeString('utf-8')
        else:
            query = model.Session.query(model.Revision)
            c.page = page_util.Page(
                collection=query,
                page=request.params.get('page', 1),
                url=h.pager_url,
                items_per_page=20
            )
            return base.render('revision/list.html')