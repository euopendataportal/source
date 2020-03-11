import ckan.controllers.group as group
import ckan.lib.helpers as h
import ckan.model as model
import ckan.lib.base as base

from ckan.common import c, request, _

render = base.render

class OrganizationController(group.GroupController):
    ''' The organization controller is pretty much just the group
    controller. It has a few templates defined that are different and sets
    the group_type to organization so that the group controller knows that
    it is in fact the organization controller.  All the main logical
    differences are therefore in the group controller.

    The main differences the group controller provides for organizations are
    a few wrapper functions that swap organization for group when rendering
    templates, redirecting or calling logic actions '''

    # this makes us use organization actions
    group_type = 'organization'

    def _guess_group_type(self, expecting_name=False):
        return 'organization'

    def index(self):
        group_type = self._guess_group_type()

        context = {'model': model, 'session': model.Session,
                   'user': c.user or c.author, 'for_view': True,
                   'with_private': False}

        q = c.q = request.params.get('q', '')
        data_dict = {'all_fields': True, 'q': q}
        sort_by = c.sort_by_selected = request.params.get('sort')
        if sort_by:
            data_dict['sort'] = sort_by
        try:
            self._check_access('site_read', context)
        except NotAuthorized:
            abort(401, _('Not authorized to see this page'))

        # pass user info to context as needed to view private datasets of
        # orgs correctly
        if c.userobj:
            context['user_id'] = c.userobj.id
            context['user_is_admin'] = c.userobj.sysadmin

        results = self._action('organization_list')(context, data_dict)
        filtered_results = [org for org in results if org['packages'] > 0]

        c.page = h.Page(
            collection=filtered_results,
            page=request.params.get('page', 1),
            url=h.pager_url,
            items_per_page=21
        )
        return render(self._index_template(group_type))
