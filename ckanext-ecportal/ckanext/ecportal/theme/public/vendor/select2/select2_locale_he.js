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
* Select2 Hebrew translation.
*
* Author: Yakir Sitbon <http://www.yakirs.net/>
*/
(function ($) {
    "use strict";

    $.extend($.fn.select2.defaults, {
        formatNoMatches: function () { return "לא נמצאו התאמות"; },
        formatInputTooShort: function (input, min) { var n = min - input.length; return "נא להזין עוד " + n + " תווים נוספים"; },
        formatInputTooLong: function (input, max) { var n = input.length - max; return "נא להזין פחות " + n + " תווים"; },
        formatSelectionTooBig: function (limit) { return "ניתן לבחור " + limit + " פריטים"; },
        formatLoadMore: function (pageNumber) { return "טוען תוצאות נוספות…"; },
        formatSearching: function () { return "מחפש…"; }
    });
})(jQuery);
