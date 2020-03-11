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

module('Data adapters - Maximum input length');

var MaximumInputLength = require('select2/data/maximumInputLength');
var $ = require('jquery');
var Options = require('select2/options');
var Utils = require('select2/utils');

function MaximumInputStub () {
  this.called = false;
}

MaximumInputStub.prototype.query = function (params, callback) {
  this.called = true;
};

var MaximumInputData = Utils.Decorate(MaximumInputStub, MaximumInputLength);

test('0 never displays the notice', function (assert) {
  var zeroOptions = new Options({
    maximumInputLength: 0
  });

  var data = new MaximumInputData(null, zeroOptions);

  data.trigger = function () {
    assert.ok(false, 'No events should be triggered');
  };

  data.query({
    term: ''
  });

  assert.ok(data.called);

  data = new MaximumInputData(null, zeroOptions);

  data.query({
    term: 'test'
  });

  assert.ok(data.called);
});

test('< 0 never displays the notice', function (assert) {
  var negativeOptions = new Options({
    maximumInputLength: -1
  });

  var data = new MaximumInputData(null, negativeOptions);

  data.trigger = function () {
    assert.ok(false, 'No events should be triggered');
  };

  data.query({
    term: ''
  });

  assert.ok(data.called);

  data = new MaximumInputData(null, negativeOptions);

  data.query({
    term: 'test'
  });

  assert.ok(data.called);
});

test('triggers when input is too long', function (assert) {
  var options = new Options({
    maximumInputLength: 1
  });

  var data = new MaximumInputData(null, options);

  data.trigger = function () {
    assert.ok(true, 'The event should be triggered.');
  };

  data.query({
    term: 'no'
  });

  assert.ok(!data.called, 'The adapter should not be called');
});

test('does not trigger when equal', function (assert) {
  var options = new Options({
    maximumInputLength: 10
  });

  var data = new MaximumInputData(null, options);

  data.trigger = function () {
    assert.ok(false, 'The event should not be triggered.');
  };

  data.query({
    term: '1234567890'
  });

  assert.ok(data.called);
});

test('does not trigger when less', function (assert) {
  var options = new Options({
    maximumInputLength: 10
  });

  var data = new MaximumInputData(null, options);

  data.trigger = function () {
    assert.ok(false, 'The event should not be triggered.');
  };

  data.query({
    term: '123'
  });

  assert.ok(data.called);
});

test('works with null term', function (assert) {
  var options = new Options({
    maximumInputLength: 1
  });

  var data = new MaximumInputData(null, options);

  data.trigger = function () {
    assert.ok(false, 'The event should not be triggered');
  };

  data.query({});

  assert.ok(data.called);
});
