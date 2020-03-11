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
  // Thai
  return {
    errorLoading: function () {
      return 'ไม่สามารถค้นข้อมูลได้';
    },
    inputTooLong: function (args) {
      var overChars = args.input.length - args.maximum;

      var message = 'โปรดลบออก ' + overChars + ' ตัวอักษร';

      return message;
    },
    inputTooShort: function (args) {
      var remainingChars = args.minimum - args.input.length;

      var message = 'โปรดพิมพ์เพิ่มอีก ' + remainingChars + ' ตัวอักษร';

      return message;
    },
    loadingMore: function () {
      return 'กำลังค้นข้อมูลเพิ่ม…';
    },
    maximumSelected: function (args) {
      var message = 'คุณสามารถเลือกได้ไม่เกิน ' + args.maximum + ' รายการ';

      return message;
    },
    noResults: function () {
      return 'ไม่พบข้อมูล';
    },
    searching: function () {
      return 'กำลังค้นข้อมูล…';
    }
  };
});
