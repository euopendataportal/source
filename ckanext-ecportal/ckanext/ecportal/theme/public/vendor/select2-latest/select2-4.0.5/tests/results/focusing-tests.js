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

module('Results - highlighting results');

test('results:all with no data skips results:focus', function (assert) {
  assert.expect(0);

  var $ = require('jquery');

  var $select = $('<select></select>');
  var $parent = $('<div></div>');

  var $container = $('<span></span>');
  var container = new MockContainer();

  $parent.appendTo($('#qunit-fixture'));
  $select.appendTo($parent);

  var Utils = require('select2/utils');
  var Options = require('select2/options');

  var Results = require('select2/results');

  var results = new Results($select, new Options({}));

  // Fake the data adapter for the `setClasses` method
  results.data = {};
  results.data.current = function (callback) {
    callback([{ id: 'test' }]);
  };

  results.render();

  results.bind(container, $container);

  results.on('results:focus', function (params) {
    assert.ok(false, 'The results:focus event was triggered');
  });

  container.trigger('results:all', {
    data: {
      results: []
    }
  });
});

test('results:all triggers results:focus on the first item', function (assert) {
  assert.expect(2);

  var $ = require('jquery');

  var $select = $('<select></select>');
  var $parent = $('<div></div>');

  var $container = $('<span></span>');
  var container = new MockContainer();

  $parent.appendTo($('#qunit-fixture'));
  $select.appendTo($parent);

  var Utils = require('select2/utils');
  var Options = require('select2/options');

  var Results = require('select2/results');

  var results = new Results($select, new Options({}));

  // Fake the data adapter for the `setClasses` method
  results.data = {};
  results.data.current = function (callback) {
    callback([{ id: 'test' }]);
  };

  results.render();

  results.bind(container, $container);

  results.on('results:focus', function (params) {
    assert.equal(params.data.id, 'test');
    assert.equal(params.data.text, 'Test');
  });

  container.trigger('results:all', {
    data: {
      results: [
        {
          id: 'test',
          text: 'Test'
        }
      ]
    }
  });
});

test('results:append does not trigger results:focus', function (assert) {
  assert.expect(0);

  var $ = require('jquery');

  var $select = $('<select></select>');
  var $parent = $('<div></div>');

  var $container = $('<span></span>');
  var container = new MockContainer();

  $parent.appendTo($('#qunit-fixture'));
  $select.appendTo($parent);

  var Utils = require('select2/utils');
  var Options = require('select2/options');

  var Results = require('select2/results');

  var results = new Results($select, new Options({}));

  // Fake the data adapter for the `setClasses` method
  results.data = {};
  results.data.current = function (callback) {
    callback([{ id: 'test' }]);
  };

  results.render();

  results.bind(container, $container);

  results.on('results:focus', function () {
    assert.ok(false, 'The results:focus event was triggered');
  });

  container.trigger('results:append', {
    data: {
      results: [
        {
          id: 'test',
          text: 'Test'
        }
      ]
    }
  });
});