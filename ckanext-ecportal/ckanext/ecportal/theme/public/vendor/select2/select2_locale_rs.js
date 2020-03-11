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

/**
 * Select2 Serbian translation.
 *
 * @author  Limon Monte <limon.monte@gmail.com>
 */
(function ($) {
    "use strict";

    $.extend($.fn.select2.defaults, {
        formatNoMatches: function () { return "Ništa nije pronađeno"; },
        formatInputTooShort: function (input, min) { var n = min - input.length; return "Ukucajte bar još " + n + " simbol" + (n % 10 == 1 && n % 100 != 11 ? "" : "a"); },
        formatInputTooLong: function (input, max) { var n = input.length - max; return "Obrišite " + n + " simbol" + (n % 10 == 1 && n % 100 != 11	 ? "" : "a"); },
        formatSelectionTooBig: function (limit) { return "Možete izabrati samo " + limit + " stavk" + (limit % 10 == 1 && limit % 100 != 11	 ? "u" : (limit % 10 >= 2 && limit % 10 <= 4 && (limit % 100 < 12 || limit % 100 > 14)? "e" : "i")); },
        formatLoadMore: function (pageNumber) { return "Preuzimanje još rezultata…"; },
        formatSearching: function () { return "Pretraga…"; }
    });
})(jQuery);
