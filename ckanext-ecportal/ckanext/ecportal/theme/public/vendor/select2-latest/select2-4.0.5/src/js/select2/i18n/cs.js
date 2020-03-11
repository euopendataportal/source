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
  // Czech
  function small (count, masc) {
    switch(count) {
      case 2:
        return masc ? 'dva' : 'dvě';
      case 3:
        return 'tři';
      case 4:
        return 'čtyři';
    }
    return '';
  }
  return {
    errorLoading: function () {
      return 'Výsledky nemohly být načteny.';
    },
    inputTooLong: function (args) {
      var n = args.input.length - args.maximum;

      if (n == 1) {
        return 'Prosím, zadejte o jeden znak méně.';
      } else if (n <= 4) {
        return 'Prosím, zadejte o ' + small(n, true) + ' znaky méně.';
      } else {
        return 'Prosím, zadejte o ' + n + ' znaků méně.';
      }
    },
    inputTooShort: function (args) {
      var n = args.minimum - args.input.length;

      if (n == 1) {
        return 'Prosím, zadejte ještě jeden znak.';
      } else if (n <= 4) {
        return 'Prosím, zadejte ještě další ' + small(n, true) + ' znaky.';
      } else {
        return 'Prosím, zadejte ještě dalších ' + n + ' znaků.';
      }
    },
    loadingMore: function () {
      return 'Načítají se další výsledky…';
    },
    maximumSelected: function (args) {
      var n = args.maximum;

      if (n == 1) {
        return 'Můžete zvolit jen jednu položku.';
      } else if (n <= 4) {
        return 'Můžete zvolit maximálně ' + small(n, false) + ' položky.';
      } else {
        return 'Můžete zvolit maximálně ' + n + ' položek.';
      }
    },
    noResults: function () {
      return 'Nenalezeny žádné položky.';
    },
    searching: function () {
      return 'Vyhledávání…';
    }
  };
});
