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
  // Khmer
  return {
    errorLoading: function () {
      return 'មិនអាចទាញយកទិន្នន័យ';
    },
    inputTooLong: function (args) {
      var overChars = args.input.length - args.maximum;

      var message = 'សូមលុបចេញ  ' + overChars + ' អក្សរ';

      return message;
    },
    inputTooShort: function (args) {
      var remainingChars = args.minimum - args.input.length;

      var message = 'សូមបញ្ចូល' + remainingChars + ' អក្សរ រឺ ច្រើនជាងនេះ';

      return message;
    },
    loadingMore: function () {
      return 'កំពុងទាញយកទិន្នន័យបន្ថែម...';
    },
    maximumSelected: function (args) {
      var message = 'អ្នកអាចជ្រើសរើសបានតែ ' + args.maximum + ' ជម្រើសប៉ុណ្ណោះ';

      return message;
    },
    noResults: function () {
      return 'មិនមានលទ្ធផល';
    },
    searching: function () {
      return 'កំពុងស្វែងរក...';
    }
  };
});
