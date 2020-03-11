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

module('Decorators');

var Utils = require('select2/utils');

test('overridden - method', function (assert) {
  function BaseClass () {}

  BaseClass.prototype.hello = function () {
    return 'A';
  };

  function DecoratorClass () {}

  DecoratorClass.prototype.hello = function () {
    return 'B';
  };

  var DecoratedClass = Utils.Decorate(BaseClass, DecoratorClass);

  var inst = new DecoratedClass();

  assert.strictEqual(inst.hello(), 'B');
});

test('overridden - constructor', function (assert) {
  function BaseClass () {
    this.inherited = true;
  }

  BaseClass.prototype.hello = function () {
    return 'A';
  };

  function DecoratorClass (decorated) {
    this.called = true;
  }

  DecoratorClass.prototype.other = function () {
    return 'B';
  };

  var DecoratedClass = Utils.Decorate(BaseClass, DecoratorClass);

  var inst = new DecoratedClass();

  assert.ok(inst.called);
  assert.ok(!inst.inherited);
});

test('not overridden - method', function (assert) {
  function BaseClass () {}

  BaseClass.prototype.hello = function () {
    return 'A';
  };

  function DecoratorClass () {}

  DecoratorClass.prototype.other = function () {
    return 'B';
  };

  var DecoratedClass = Utils.Decorate(BaseClass, DecoratorClass);

  var inst = new DecoratedClass();

  assert.strictEqual(inst.hello(), 'A');
});

test('not overridden - constructor', function (assert) {
  function BaseClass () {
    this.called = true;
  }

  BaseClass.prototype.hello = function () {
    return 'A';
  };

  function DecoratorClass () {}

  DecoratorClass.prototype.other = function () {
    return 'B';
  };

  var DecoratedClass = Utils.Decorate(BaseClass, DecoratorClass);

  var inst = new DecoratedClass();

  assert.ok(inst.called);
});

test('inherited - method', function (assert) {
  function BaseClass () {}

  BaseClass.prototype.hello = function () {
    return 'A';
  };

  function DecoratorClass (decorated) {}

  DecoratorClass.prototype.hello = function (decorated) {
    return 'B' + decorated.call(this) + 'C';
  };

  var DecoratedClass = Utils.Decorate(BaseClass, DecoratorClass);

  var inst = new DecoratedClass();

  assert.strictEqual(inst.hello(), 'BAC');
});

test('inherited - constructor', function (assert) {
  function BaseClass () {
    this.inherited = true;
  }

  BaseClass.prototype.hello = function () {
    return 'A';
  };

  function DecoratorClass (decorated) {
    this.called = true;

    decorated.call(this);
  }

  DecoratorClass.prototype.other = function () {
    return 'B';
  };

  var DecoratedClass = Utils.Decorate(BaseClass, DecoratorClass);

  var inst = new DecoratedClass();

  assert.ok(inst.called);
  assert.ok(inst.inherited);
});

test('inherited - three levels', function (assert) {
  function BaseClass (testArgument) {
    this.baseCalled = true;
    this.baseTestArgument = testArgument;
  }

  BaseClass.prototype.test = function (a) {
    return a + 'c';
  };

  function MiddleClass (decorated, testArgument) {
    this.middleCalled = true;
    this.middleTestArgument = testArgument;

    decorated.call(this, testArgument);
  }

  MiddleClass.prototype.test = function (decorated, a) {
    return decorated.call(this, a + 'b');
  };

  function DecoratorClass (decorated, testArgument) {
    this.decoratorCalled = true;
    this.decoratorTestArgument = testArgument;

    decorated.call(this, testArgument);
  }

  DecoratorClass.prototype.test = function (decorated, a) {
    return decorated.call(this, a + 'a');
  };

  var DecoratedClass = Utils.Decorate(
    Utils.Decorate(BaseClass, MiddleClass),
    DecoratorClass
  );

  var inst = new DecoratedClass('test');

  assert.ok(inst.baseCalled, 'The base class contructor was called');
  assert.ok(inst.middleCalled, 'The middle class constructor was called');
  assert.ok(inst.decoratorCalled, 'The decorator constructor was called');

  assert.strictEqual(inst.baseTestArgument, 'test');
  assert.strictEqual(inst.middleTestArgument, 'test');
  assert.strictEqual(inst.decoratorTestArgument, 'test');

  var out = inst.test('test');

  assert.strictEqual(out, 'testabc');
});
