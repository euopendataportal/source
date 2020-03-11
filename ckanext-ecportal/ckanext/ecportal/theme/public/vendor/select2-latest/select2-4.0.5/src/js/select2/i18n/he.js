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
  // Hebrew
  return {
    errorLoading: function () {
      return 'שגיאה בטעינת התוצאות';
    },
    inputTooLong: function (args) {
      var overChars = args.input.length - args.maximum;

      var message = 'נא למחוק ';

      if (overChars === 1) {
        message += 'תו אחד';
      } else {
        message += overChars + ' תווים';
      }

      return message;
    },
    inputTooShort: function (args) {
      var remainingChars = args.minimum - args.input.length;

      var message = 'נא להכניס ';

      if (remainingChars === 1) {
        message += 'תו אחד';
      } else {
        message += remainingChars + ' תווים';
      }

      message += ' או יותר';

      return message;
    },
    loadingMore: function () {
      return 'טוען תוצאות נוספות…';
    },
    maximumSelected: function (args) {
      var message = 'באפשרותך לבחור עד ';

      if (args.maximum === 1) {
        message += 'פריט אחד';
      } else {
        message += args.maximum + ' פריטים';
      }

      return message;
    },
    noResults: function () {
      return 'לא נמצאו תוצאות';
    },
    searching: function () {
      return 'מחפש…';
    }
  };
});
