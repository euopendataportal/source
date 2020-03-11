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
  // Italian
  return {
    errorLoading: function () {
      return 'I risultati non possono essere caricati.';
    },
    inputTooLong: function (args) {
      var overChars = args.input.length - args.maximum;

      var message = 'Per favore cancella ' + overChars + ' caratter';

      if (overChars !== 1) {
        message += 'i';
      } else {
        message += 'e';
      }

      return message;
    },
    inputTooShort: function (args) {
      var remainingChars = args.minimum - args.input.length;

      var message = 'Per favore inserisci ' +remainingChars+ ' o più caratteri';

      return message;
    },
    loadingMore: function () {
      return 'Caricando più risultati…';
    },
    maximumSelected: function (args) {
      var message = 'Puoi selezionare solo ' + args.maximum + ' element';

      if (args.maximum !== 1) {
        message += 'i';
      } else {
        message += 'o';
      }

      return message;
    },
    noResults: function () {
      return 'Nessun risultato trovato';
    },
    searching: function () {
      return 'Sto cercando…';
    }
  };
});
