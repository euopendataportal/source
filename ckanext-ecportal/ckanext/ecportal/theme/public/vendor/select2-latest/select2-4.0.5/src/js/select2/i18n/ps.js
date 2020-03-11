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

/* jslint maxlen: 87 */
define(function () {
  // Pashto (پښتو)
  return {
    errorLoading: function () {
      return 'پايلي نه سي ترلاسه کېدای';
    },
    inputTooLong: function (args) {
      var overChars = args.input.length - args.maximum;

      var message = 'د مهربانۍ لمخي ' + overChars + ' توری ړنګ کړئ';

      if (overChars != 1) {
        message = message.replace('توری', 'توري');
      }

      return message;
    },
    inputTooShort: function (args) {
      var remainingChars = args.minimum - args.input.length;

      var message = 'لږ تر لږه ' + remainingChars + ' يا ډېر توري وليکئ';

      return message;
    },
    loadingMore: function () {
      return 'نوري پايلي ترلاسه کيږي...';
    },
    maximumSelected: function (args) {
      var message = 'تاسو يوازي ' + args.maximum + ' قلم په نښه کولای سی';

      if (args.maximum != 1) {
        message = message.replace('قلم', 'قلمونه');
      }

      return message;
    },
    noResults: function () {
      return 'پايلي و نه موندل سوې';
    },
    searching: function () {
      return 'لټول کيږي...';
    }
  };
});
