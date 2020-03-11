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
  // Brazilian Portuguese
  return {
    errorLoading: function () {
      return 'Os resultados não puderam ser carregados.';
    },
    inputTooLong: function (args) {
      var overChars = args.input.length - args.maximum;

      var message = 'Apague ' + overChars + ' caracter';

      if (overChars != 1) {
        message += 'es';
      }

      return message;
    },
    inputTooShort: function (args) {
      var remainingChars = args.minimum - args.input.length;

      var message = 'Digite ' + remainingChars + ' ou mais caracteres';

      return message;
    },
    loadingMore: function () {
      return 'Carregando mais resultados…';
    },
    maximumSelected: function (args) {
      var message = 'Você só pode selecionar ' + args.maximum + ' ite';

      if (args.maximum == 1) {
        message += 'm';
      } else {
        message += 'ns';
      }

      return message;
    },
    noResults: function () {
      return 'Nenhum resultado encontrado';
    },
    searching: function () {
      return 'Buscando…';
    }
  };
});
