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
 * Select2 Ukrainian translation.
 * 
 * @author  bigmihail <bigmihail@bigmir.net>
 * @author  Uriy Efremochkin <efremochkin@uriy.me>
 */
(function ($) {
    "use strict";

    $.extend($.fn.select2.defaults, {
        formatMatches: function (matches) { return character(matches, "результат") + " знайдено, використовуйте клавіші зі стрілками вверх та вниз для навігації."; },
        formatNoMatches: function () { return "Нічого не знайдено"; },
        formatInputTooShort: function (input, min) { return "Введіть буль ласка ще " + character(min - input.length, "символ"); },
        formatInputTooLong: function (input, max) { return "Введіть буль ласка на " + character(input.length - max, "символ") + " менше"; },
        formatSelectionTooBig: function (limit) { return "Ви можете вибрати лише " + character(limit, "елемент"); },
        formatLoadMore: function (pageNumber) { return "Завантаження даних…"; },
        formatSearching: function () { return "Пошук…"; }
    });

    function character (n, word) {
        return n + " " + word + (n%10 < 5 && n%10 > 0 && (n%100 < 5 || n%100 > 19) ? n%10 > 1 ? "и" : "" : "ів");
    }
})(jQuery);
