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

module('Dropdown - selectOnClose');

var $ = require('jquery');

var Utils = require('select2/utils');
var Options = require('select2/options');

var SelectData = require('select2/data/select');

var Results = require('select2/results');
var SelectOnClose = require('select2/dropdown/selectOnClose');

var ModifiedResults = Utils.Decorate(Results, SelectOnClose);

var options = new Options({
  selectOnClose: true
});

test('will not trigger if no results were given', function (assert) {
  assert.expect(0);

  var $element = $('<select></select>');
  var select = new ModifiedResults($element, options, new SelectData($element));

  var $dropdown = select.render();

  var container = new MockContainer();
  select.bind(container, $('<div></div>'));

  select.on('select', function () {
    assert.ok(false, 'The select event should not have been triggered');
  });

  container.trigger('close');
});

test('will not trigger if the results list is empty', function (assert) {
  assert.expect(1);

  var $element = $('<select></select>');
  var select = new ModifiedResults($element, options, new SelectData($element));

  var $dropdown = select.render();

  var container = new MockContainer();
  select.bind(container, $('<div></div>'));

  select.on('select', function () {
    assert.ok(false, 'The select event should not have been triggered');
  });

  select.append({
    results: []
  });

  assert.equal(
    $dropdown.find('li').length,
    0,
    'There should not be any results in the dropdown'
  );

  container.trigger('close');
});

test('will not trigger if no results here highlighted', function (assert) {
  assert.expect(2);

  var $element = $('<select></select>');
  var select = new ModifiedResults($element, options, new SelectData($element));

  var $dropdown = select.render();

  var container = new MockContainer();
  select.bind(container, $('<div></div>'));

  select.on('select', function () {
    assert.ok(false, 'The select event should not have been triggered');
  });

  select.append({
    results: [
      {
        id: '1',
        text: 'Test'
      }
    ]
  });

  assert.equal(
    $dropdown.find('li').length,
    1,
    'There should be one result in the dropdown'
  );

  assert.equal(
    $.trim($dropdown.find('li').text()),
    'Test',
    'The result should be the same as the one we appended'
  );

  container.trigger('close');
});

test('will trigger if there is a highlighted result', function (assert) {
  assert.expect(2);

  var $element = $('<select></select>');
  var select = new ModifiedResults($element, options, new SelectData($element));

  var $dropdown = select.render();

  var container = new MockContainer();
  select.bind(container, $('<div></div>'));

  select.on('select', function () {
    assert.ok(true, 'The select event should have been triggered');
  });

  select.append({
    results: [
      {
        id: '1',
        text: 'Test'
      }
    ]
  });

  assert.equal(
    $dropdown.find('li').length,
    1,
    'There should be one result in the dropdown'
  );

  $dropdown.find('li').addClass('select2-results__option--highlighted');

  container.trigger('close');
});
