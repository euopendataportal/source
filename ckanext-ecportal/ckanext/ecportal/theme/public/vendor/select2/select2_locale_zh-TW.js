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
 * Select2 Traditional Chinese translation
 */
(function ($) {
    "use strict";
    $.extend($.fn.select2.defaults, {
        formatNoMatches: function () { return "沒有找到相符的項目"; },
        formatInputTooShort: function (input, min) { var n = min - input.length; return "請再輸入" + n + "個字元";},
        formatInputTooLong: function (input, max) { var n = input.length - max; return "請刪掉" + n + "個字元";},
        formatSelectionTooBig: function (limit) { return "你只能選擇最多" + limit + "項"; },
        formatLoadMore: function (pageNumber) { return "載入中…"; },
        formatSearching: function () { return "搜尋中…"; }
    });
})(jQuery);
