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
 * Select2 Catalan translation.
 * 
 * Author: David Planella <david.planella@gmail.com>
 */
(function ($) {
    "use strict";

    $.extend($.fn.select2.defaults, {
        formatNoMatches: function () { return "No s'ha trobat cap coincidència"; },
        formatInputTooShort: function (input, min) { var n = min - input.length; return "Introduïu " + n + " caràcter" + (n == 1 ? "" : "s") + " més"; },
        formatInputTooLong: function (input, max) { var n = input.length - max; return "Introduïu " + n + " caràcter" + (n == 1? "" : "s") + "menys"; },
        formatSelectionTooBig: function (limit) { return "Només podeu seleccionar " + limit + " element" + (limit == 1 ? "" : "s"); },
        formatLoadMore: function (pageNumber) { return "S'estan carregant més resultats…"; },
        formatSearching: function () { return "S'està cercant…"; }
    });
})(jQuery);
