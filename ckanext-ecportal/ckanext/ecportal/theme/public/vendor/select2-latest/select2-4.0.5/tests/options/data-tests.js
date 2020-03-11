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

module('Options - Attributes');

var $ = require('jquery');

var Options = require('select2/options');

test('no nesting', function (assert) {
  var $test = $('<select data-test="test"></select>');

  var options = new Options({}, $test);

  assert.equal(options.get('test'), 'test');
});

test('with nesting', function (assert) {
  var $test = $('<select data-first--second="test"></select>');

  if ($test[0].dataset == null) {
    assert.ok(
      true,
      'We can not run this test with jQuery 1.x if dataset is not implemented'
    );

    return;
  }

  var options = new Options({}, $test);

  assert.ok(!(options.get('first-Second')));
  assert.equal(options.get('first').second, 'test');
});

test('overrides initialized data', function (assert) {
  var $test = $('<select data-override="yes" data-data="yes"></select>');

  var options = new Options({
    options: 'yes',
    override: 'no'
  }, $test);

  assert.equal(options.get('options'), 'yes');
  assert.equal(options.get('override'), 'yes');
  assert.equal(options.get('data'), 'yes');
});
