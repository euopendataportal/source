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

module('Data adapters - Maximum selection length');

var MaximumSelectionLength = require('select2/data/maximumSelectionLength');

var $ = require('jquery');
var Options = require('select2/options');
var Utils = require('select2/utils');

function MaximumSelectionStub () {
  this.called = false;
  this.currentData = [];
}

MaximumSelectionStub.prototype.current = function (callback) {
  callback(this.currentData);
};

MaximumSelectionStub.prototype.val = function (val) {
  this.currentData.push(val);
};

MaximumSelectionStub.prototype.query = function (params, callback) {
  this.called = true;
};

var MaximumSelectionData = Utils.Decorate(
  MaximumSelectionStub,
  MaximumSelectionLength
);

test('0 never displays the notice', function (assert) {
  var zeroOptions = new Options({
    maximumSelectionLength: 0
  });

  var data = new MaximumSelectionData(null, zeroOptions);

  data.trigger = function () {
    assert.ok(false, 'No events should be triggered');
  };

  data.query({
    term: ''
  });

  assert.ok(data.called);

  data = new MaximumSelectionData(null, zeroOptions);

  data.trigger = function () {
    assert.ok(false, 'No events should be triggered');
  };

  data.val('1');

  data.query({
    term: ''
  });

  assert.ok(data.called);

  data = new MaximumSelectionData(null, zeroOptions);

  data.trigger = function () {
    assert.ok(false, 'No events should be triggered');
  };

  data.val('1');
  data.val('2');

  data.query({
    term: ''
  });

  assert.ok(data.called);
});

test('< 0 never displays the notice', function (assert) {
  var negativeOptions = new Options({
    maximumSelectionLength: -1
  });

  var data = new MaximumSelectionData(null, negativeOptions);

  data.trigger = function () {
    assert.ok(false, 'No events should be triggered');
  };

  data.query({
    term: ''
  });

  assert.ok(data.called);

  data = new MaximumSelectionData(null, negativeOptions);

  data.trigger = function () {
    assert.ok(false, 'No events should be triggered');
  };

  data.val('1');

  data.query({
    term: ''
  });

  assert.ok(data.called);

  data = new MaximumSelectionData(null, negativeOptions);

  data.trigger = function () {
    assert.ok(false, 'No events should be triggered');
  };

  data.val('1');
  data.val('2');

  data.query({
    term: ''
  });

  assert.ok(data.called);
});

test('triggers when >= 1 selection' , function (assert) {
  var maxOfOneOptions = new Options({
    maximumSelectionLength: 1
  });
  var data = new MaximumSelectionData(null, maxOfOneOptions);

  data.trigger = function () {
    assert.ok(false, 'No events should be triggered');
  };

  data.query({
    term: ''
  });

  assert.ok(data.called);

  data = new MaximumSelectionData(null, maxOfOneOptions);

  data.trigger = function () {
    assert.ok(true, 'The event should be triggered.');
  };

  data.val('1');

  data.query({
    term: ''
  });

  assert.ok(!data.called);

});

test('triggers when >= 2 selections' , function (assert) {
  var maxOfTwoOptions = new Options({
    maximumSelectionLength: 2
  });
  var data = new MaximumSelectionData(null, maxOfTwoOptions);

  data.trigger = function () {
    assert.ok(false, 'No events should be triggered');
  };

  data.query({
    term: ''
  });

  assert.ok(data.called);

  data = new MaximumSelectionData(null, maxOfTwoOptions);

  data.trigger = function () {
    assert.ok(false, 'No events should be triggered');
  };

  data.val('1');

  data.query({
    term: ''
  });

  assert.ok(data.called);

  data = new MaximumSelectionData(null, maxOfTwoOptions);

  data.trigger = function () {
    assert.ok(true, 'The event should be triggered.');
  };

  data.val('1');
  data.val('2');

  data.query({
    term: ''
  });

  assert.ok(!data.called);

});
