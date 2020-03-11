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
  // Serbian Cyrilic
  function ending (count, one, some, many) {
    if (count % 10 == 1 && count % 100 != 11) {
      return one;
    }

    if (count % 10 >= 2 && count % 10 <= 4 &&
      (count % 100 < 12 || count % 100 > 14)) {
        return some;
    }

    return many;
  }

  return {
    errorLoading: function () {
      return 'Преузимање није успело.';
    },
    inputTooLong: function (args) {
      var overChars = args.input.length - args.maximum;

      var message = 'Обришите ' + overChars + ' симбол';

      message += ending(overChars, '', 'а', 'а');

      return message;
    },
    inputTooShort: function (args) {
      var remainingChars = args.minimum - args.input.length;

      var message = 'Укуцајте бар још ' + remainingChars + ' симбол';

      message += ending(remainingChars, '', 'а', 'а');

      return message;
    },
    loadingMore: function () {
      return 'Преузимање још резултата…';
    },
    maximumSelected: function (args) {
      var message = 'Можете изабрати само ' + args.maximum + ' ставк';

      message += ending(args.maximum, 'у', 'е', 'и');

      return message;
    },
    noResults: function () {
      return 'Ништа није пронађено';
    },
    searching: function () {
      return 'Претрага…';
    }
  };
});
