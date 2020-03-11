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
  // Russian
  function ending (count, one, couple, more) {
    if (count % 10 < 5 && count % 10 > 0 &&
        count % 100 < 5 || count % 100 > 20) {
      if (count % 10 > 1) {
        return couple;
      }
    } else {
      return more;
    }

    return one;
  }

  return {
    errorLoading: function () {
      return 'Невозможно загрузить результаты';
    },
    inputTooLong: function (args) {
      var overChars = args.input.length - args.maximum;

      var message = 'Пожалуйста, введите на ' + overChars + ' символ';

      message += ending(overChars, '', 'a', 'ов');

      message += ' меньше';

      return message;
    },
    inputTooShort: function (args) {
      var remainingChars = args.minimum - args.input.length;

      var message = 'Пожалуйста, введите еще хотя бы ' + remainingChars +
        ' символ';

      message += ending(remainingChars, '', 'a', 'ов');

      return message;
    },
    loadingMore: function () {
      return 'Загрузка данных…';
    },
    maximumSelected: function (args) {
      var message = 'Вы можете выбрать не более ' + args.maximum + ' элемент';

      message += ending(args.maximum, '', 'a', 'ов');

      return message;
    },
    noResults: function () {
      return 'Совпадений не найдено';
    },
    searching: function () {
      return 'Поиск…';
    }
  };
});
