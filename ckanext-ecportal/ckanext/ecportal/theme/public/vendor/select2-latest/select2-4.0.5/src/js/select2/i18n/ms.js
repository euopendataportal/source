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
  // Malay
  return {
    errorLoading: function () {
      return 'Keputusan tidak berjaya dimuatkan.';
    },
    inputTooLong: function (args) {
      var overChars = args.input.length - args.maximum;

      return 'Sila hapuskan ' + overChars + ' aksara';
    },
    inputTooShort: function (args) {
      var remainingChars = args.minimum - args.input.length;

      return 'Sila masukkan ' + remainingChars + ' atau lebih aksara';
    },
    loadingMore: function () {
      return 'Sedang memuatkan keputusan…';
    },
    maximumSelected: function (args) {
      return 'Anda hanya boleh memilih ' + args.maximum + ' pilihan';
    },
    noResults: function () {
      return 'Tiada padanan yang ditemui';
    },
    searching: function () {
      return 'Mencari…';
    }
  };
});