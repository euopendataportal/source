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

module('Dropdown - dropdownCssClass compatibility');

var $ = require('jquery');
var Utils = require('select2/utils');
var Options = require('select2/options');

var Dropdown = require('select2/dropdown');
var DropdownCSS = Utils.Decorate(
  Dropdown,
  require('select2/compat/dropdownCss')
);

test('all classes will be copied if :all: is used', function (assert) {
  var $element = $('<select class="test copy works"></select>');
  var options = new Options({
    dropdownCssClass: ':all:'
  });

  var select = new DropdownCSS($element, options);
  var $dropdown = select.render();

  assert.ok($dropdown.hasClass('test'));
  assert.ok($dropdown.hasClass('copy'));
  assert.ok($dropdown.hasClass('works'));
  assert.ok(!$dropdown.hasClass(':all:'));
});

test(':all: can be used with other classes', function (assert) {
  var $element = $('<select class="test copy works"></select>');
  var options = new Options({
    dropdownCssClass: ':all: other'
  });

  var select = new DropdownCSS($element, options);
  var $dropdown = select.render();

  assert.ok($dropdown.hasClass('test'));
  assert.ok($dropdown.hasClass('copy'));
  assert.ok($dropdown.hasClass('works'));
  assert.ok($dropdown.hasClass('other'));
  assert.ok(!$dropdown.hasClass(':all:'));
});

test('classes can be passed in as a string', function (assert) {
  var $element = $('<select class="test copy works"></select>');
  var options = new Options({
    dropdownCssClass: 'other'
  });

  var select = new DropdownCSS($element, options);
  var $dropdown = select.render();

  assert.ok($dropdown.hasClass('other'));
});

test('a function can be used based on the element', function (assert){
  var $element = $('<select class="test"></select>');
  var options = new Options({
    dropdownCssClass: function ($element) {
      return 'function';
    }
  });

  var select = new DropdownCSS($element, options);
  var $dropdown = select.render();

  assert.ok($dropdown.hasClass('function'));
  assert.ok(!$dropdown.hasClass('test'));
});

test(':all: works around custom adapters', function (assert) {
  var $element = $('<select class="test"></select>');
  var options = new Options({
    dropdownCssClass: ':all: something',
    adaptDropdownCssClass: function (clazz) {
      return clazz + '-modified';
    }
  });

  var select = new DropdownCSS($element, options);
  var $dropdown = select.render();

  assert.ok($dropdown.hasClass('something'));

  assert.ok($dropdown.hasClass('test'));
  assert.ok($dropdown.hasClass('test-modified'));
});

module('Dropdown - adaptDropdownCss compatibility');

test('only return when adapted', function (assert) {
  var $element = $('<select class="original"></select>');
  var options = new Options({
    adaptDropdownCssClass: function (clazz) {
      return 'modified';
    }
  });

  var select = new DropdownCSS($element, options);
  var $dropdown = select.render();

  assert.ok(!$dropdown.hasClass('original'));
  assert.ok($dropdown.hasClass('modified'));
});
