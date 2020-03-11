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

/* jshint -W100 */
/* jslint maxlen: 86 */
define(function () {
  // Farsi (Persian)
  return {
    errorLoading: function () {
      return 'امکان بارگذاری نتایج وجود ندارد.';
    },
    inputTooLong: function (args) {
      var overChars = args.input.length - args.maximum;

      var message = 'لطفاً ' + overChars + ' کاراکتر را حذف نمایید';

      return message;
    },
    inputTooShort: function (args) {
      var remainingChars = args.minimum - args.input.length;

      var message = 'لطفاً تعداد ' + remainingChars + ' کاراکتر یا بیشتر وارد نمایید';

      return message;
    },
    loadingMore: function () {
      return 'در حال بارگذاری نتایج بیشتر...';
    },
    maximumSelected: function (args) {
      var message = 'شما تنها می‌توانید ' + args.maximum + ' آیتم را انتخاب نمایید';

      return message;
    },
    noResults: function () {
      return 'هیچ نتیجه‌ای یافت نشد';
    },
    searching: function () {
      return 'در حال جستجو...';
    }
  };
});
