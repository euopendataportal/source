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

module('Selection containers - Placeholders');

var Placeholder = require('select2/selection/placeholder');
var SingleSelection = require('select2/selection/single');

var $ = require('jquery');
var Options = require('select2/options');
var Utils = require('select2/utils');

var SinglePlaceholder = Utils.Decorate(SingleSelection, Placeholder);

var placeholderOptions = new Options({
  placeholder: {
    id: 'placeholder',
    text: 'This is the placeholder'
  }
});

test('normalizing placeholder ignores objects', function (assert) {
  var selection = new SinglePlaceholder(
    $('#qunit-fixture .single'),
    placeholderOptions
  );

  var original = {
    id: 'test',
    text: 'testing'
  };

  var normalized = selection.normalizePlaceholder(original);

  assert.equal(original, normalized);
});

test('normalizing placeholder gives object for string', function (assert) {
  var selection = new SinglePlaceholder(
    $('#qunit-fixture .single'),
    placeholderOptions
  );

  var normalized = selection.normalizePlaceholder('placeholder');

  assert.equal(normalized.id, '');
  assert.equal(normalized.text, 'placeholder');
});


test('text is shown for placeholder option on single', function (assert) {
  var selection = new SinglePlaceholder(
    $('#qunit-fixture .single'),
    placeholderOptions
  );

  var $selection = selection.render();

  selection.update([{
    id: 'placeholder'
  }]);

  assert.equal($selection.text(), 'This is the placeholder');
});

test('placeholder is shown when no options are selected', function (assert) {
  var selection = new SinglePlaceholder(
    $('#qunit-fixture .multiple'),
    placeholderOptions
  );

  var $selection = selection.render();

  selection.update([]);

  assert.equal($selection.text(), 'This is the placeholder');
});
