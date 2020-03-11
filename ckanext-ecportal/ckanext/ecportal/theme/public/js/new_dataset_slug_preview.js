/*   Copyright (C) <2018>  <Publications Office of the European Union>
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Affero General Public License as
*    published by the Free Software Foundation, either version 3 of the
*    License, or (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Affero General Public License for more details.
*
*    You should have received a copy of the GNU Affero General Public License
*    along with this program.  If not, see <https://www.gnu.org/licenses/>.
*
*    contact: <https://publications.europa.eu/en/web/about-us/contact>
*/

this.ckan.module('custom_slug-preview-target', {
  initialize: function () {
    var sandbox = this.sandbox;
    var options = this.options;
    var el = this.el;

    sandbox.subscribe('custom_slug-preview-created', function (preview) {
      // Append the preview string after the target input.
      el.after(preview);
    });

    // Make sure there isn't a value in the field already...
    if (el.val() == '') {
      // Once the preview box is modified stop watching it.
      sandbox.subscribe('custom_slug-preview-modified', function () {
        el.off('.custom_slug-preview');
      });

      // Watch for updates to the target field and update the hidden slug field
      // triggering the "change" event manually.
      el.on('keyup.custom_slug-preview', function (event) {
        sandbox.publish('custom_slug-target-changed', this.value);
        //slug.val(this.value).trigger('change');
      });
    }
  }
});

this.ckan.module('custom_slug-preview-slug', function (jQuery, _) {
  return {
    options: {
      prefix: '',
      placeholder: '<slug>',
      i18n: {
        url:  _('URL'),
        edit: _('Edit')
      }
    },

    initialize: function () {
      var sandbox = this.sandbox;
      var options = this.options;
      var el = this.el;
      var _ = sandbox.translate;

      var slug = el.slug();
      var parent = slug.parents('.control-group');
      var preview;

      if (!(parent.length)) {
        return;
      }


      // Watch for updates to the target field and update the hidden slug field
      // triggering the "change" event manually.
      sandbox.subscribe('custom_slug-target-changed', function (value) {
        slug.val(value).trigger('change');
      });
    }
  };
});
