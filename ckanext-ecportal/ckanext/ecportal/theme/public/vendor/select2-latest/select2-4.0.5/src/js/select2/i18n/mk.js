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
  // Macedonian
  return {
    inputTooLong: function (args) {
      var overChars = args.input.length - args.maximum;

      var message = 'Ве молиме внесете ' + args.maximum + ' помалку карактер';

      if (args.maximum !== 1) {
        message += 'и';
      }

      return message;
    },
    inputTooShort: function (args) {
      var remainingChars = args.minimum - args.input.length;

      var message = 'Ве молиме внесете уште ' + args.maximum + ' карактер';

      if (args.maximum !== 1) {
        message += 'и';
      }

      return message;
    },
    loadingMore: function () {
      return 'Вчитување резултати…';
    },
    maximumSelected: function (args) {
      var message = 'Можете да изберете само ' + args.maximum + ' ставк';

      if (args.maximum === 1) {
        message += 'а';
      } else {
        message += 'и';
      }

      return message;
    },
    noResults: function () {
      return 'Нема пронајдено совпаѓања';
    },
    searching: function () {
      return 'Пребарување…';
    }
  };
});
