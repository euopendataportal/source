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

module('Dropdown - containerCssClass compatibility');

var $ = require('jquery');
var Utils = require('select2/utils');
var Options = require('select2/options');

var SingleSelection = require('select2/selection/single');
var ContainerCSS = Utils.Decorate(
  SingleSelection,
  require('select2/compat/containerCss')
);

test('all classes will be copied if :all: is used', function (assert) {
  var $element = $('<select class="test copy works"></select>');
  var options = new Options({
    containerCssClass: ':all:'
  });

  var select = new ContainerCSS($element, options);
  var $container = select.render();

  assert.ok($container.hasClass('test'));
  assert.ok($container.hasClass('copy'));
  assert.ok($container.hasClass('works'));
  assert.ok(!$container.hasClass(':all:'));
});

test(':all: can be used with other classes', function (assert) {
  var $element = $('<select class="test copy works"></select>');
  var options = new Options({
    containerCssClass: ':all: other'
  });

  var select = new ContainerCSS($element, options);
  var $container = select.render();

  assert.ok($container.hasClass('test'));
  assert.ok($container.hasClass('copy'));
  assert.ok($container.hasClass('works'));
  assert.ok($container.hasClass('other'));
  assert.ok(!$container.hasClass(':all:'));
});

test('classes can be passed in as a string', function (assert) {
  var $element = $('<select class="test copy works"></select>');
  var options = new Options({
    containerCssClass: 'other'
  });

  var select = new ContainerCSS($element, options);
  var $container = select.render();

  assert.ok($container.hasClass('other'));
});

test('a function can be used based on the element', function (assert){
  var $element = $('<select class="test"></select>');
  var options = new Options({
    containerCssClass: function ($element) {
      return 'function';
    }
  });

  var select = new ContainerCSS($element, options);
  var $container = select.render();

  assert.ok($container.hasClass('function'));
  assert.ok(!$container.hasClass('test'));
});

test(':all: works around custom adapters', function (assert) {
  var $element = $('<select class="test"></select>');
  var options = new Options({
    containerCssClass: ':all: something',
    adaptContainerCssClass: function (clazz) {
      return clazz + '-modified';
    }
  });

  var select = new ContainerCSS($element, options);
  var $container = select.render();

  assert.ok($container.hasClass('something'));

  assert.ok($container.hasClass('test'));
  assert.ok($container.hasClass('test-modified'));
});

module('Selection - adaptContainerCss compatibility');

test('only return when adapted', function (assert) {
  var $element = $('<select class="original"></select>');
  var options = new Options({
    adaptContainerCssClass: function (clazz) {
      return 'modified';
    }
  });

  var select = new ContainerCSS($element, options);
  var $container = select.render();

  assert.ok(!$container.hasClass('original'));
  assert.ok($container.hasClass('modified'));
});
