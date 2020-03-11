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
  // Upper Sorbian
  var charsWords = ['znamješko', 'znamješce', 'znamješka','znamješkow'];
  var itemsWords = ['zapisk', 'zapiskaj', 'zapiski','zapiskow'];

  var pluralWord = function pluralWord(numberOfChars, words) {
    if (numberOfChars === 1) {
        return words[0];
    } else if (numberOfChars === 2) {
      return words[1];
    }  else if (numberOfChars > 2 && numberOfChars <= 4) {
      return words[2];
    } else if (numberOfChars >= 5) {
      return words[3];
    }
  };
  
  return {
    errorLoading: function () {
      return 'Wuslědki njedachu so začitać.';
    },
    inputTooLong: function (args) {
      var overChars = args.input.length - args.maximum;

      return 'Prošu zhašej ' + overChars + ' ' + 
        pluralWord(overChars, charsWords);
    },
    inputTooShort: function (args) {
      var remainingChars = args.minimum - args.input.length;
      
      return 'Prošu zapodaj znajmjeńša ' + remainingChars + ' ' +
        pluralWord(remainingChars, charsWords);
    },
    loadingMore: function () {
      return 'Dalše wuslědki so začitaja…';
    },
    maximumSelected: function (args) {
      return 'Móžeš jenož ' + args.maximum + ' ' +
        pluralWord(args.maximum, itemsWords) + 'wubrać';
    },
    noResults: function () {
      return 'Žane wuslědki namakane';
    },
    searching: function () {
      return 'Pyta so…';
    }
  };
});
