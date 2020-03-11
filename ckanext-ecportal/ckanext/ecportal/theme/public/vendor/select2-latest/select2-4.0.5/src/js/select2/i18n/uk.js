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

define(function () {
  // Ukranian
  function ending (count, one, couple, more) {
    if (count % 100 > 10 && count % 100 < 15) {
      return more;
    }
    if (count % 10 === 1) {
      return one;
    }
    if (count % 10 > 1 && count % 10 < 5) {
      return couple;
    }
    return more;
  }

  return {
    errorLoading: function () {
      return 'Неможливо завантажити результати';
    },
    inputTooLong: function (args) {
      var overChars = args.input.length - args.maximum;
      return 'Будь ласка, видаліть ' + overChars + ' ' +
        ending(args.maximum, 'літеру', 'літери', 'літер');
    },
    inputTooShort: function (args) {
      var remainingChars = args.minimum - args.input.length;
      return 'Будь ласка, введіть ' + remainingChars + ' або більше літер';
    },
    loadingMore: function () {
      return 'Завантаження інших результатів…';
    },
    maximumSelected: function (args) {
      return 'Ви можете вибрати лише ' + args.maximum + ' ' +
        ending(args.maximum, 'пункт', 'пункти', 'пунктів');
    },
    noResults: function () {
      return 'Нічого не знайдено';
    },
    searching: function () {
      return 'Пошук…';
    }
  };
});
