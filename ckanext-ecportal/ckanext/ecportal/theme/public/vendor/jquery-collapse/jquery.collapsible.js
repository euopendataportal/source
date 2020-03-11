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

/*!
* Collapsible.js v1.1.2
* https://github.com/jordnkr/collapsible
*
* Copyright 2016, Jordan Ruedy
* This content is released under the MIT license
* http://opensource.org/licenses/MIT
*/

(function($, undefined) {
    $.fn.collapsible = function(options) {

        var defaults = {
            accordion: false,
            accordionUpSpeed: 400,
            accordionDownSpeed: 400,
            collapseSpeed: 400,
			contentOpen: null,
            arrowRclass: 'arrow-r',
            arrowDclass: 'arrow-d',
            animate: true
        };

        var settings = $.extend(defaults, options);

        return this.each(function() {
            if (settings.animate === false) {
                settings.accordionUpSpeed = 0;
                settings.accordionDownSpeed = 0;
                settings.collapseSpeed = 0;
            }

            var $thisEven = $(this).children(':even');
            var $thisOdd = $(this).children(':odd');
			var accord = 'accordion-active';

            if (settings.accordion === true) {
                if (settings.contentOpen !== null) {
                    $($thisEven[settings.contentOpen]).children(':first-child').toggleClass(settings.arrowRclass + ' ' + settings.arrowDclass);
                    $($thisOdd[settings.contentOpen]).show().addClass(accord);
                }
                $($thisEven).click(function() {
                    if ($(this).next().attr('class') === accord) {
                        $(this).next().slideUp(settings.accordionUpSpeed).removeClass(accord);
                        $(this).children(':first-child').toggleClass(settings.arrowRclass + ' ' + settings.arrowDclass);
                    } else {
                        $($thisEven).children().removeClass(settings.arrowDclass).addClass(settings.arrowRclass);
                        $($thisOdd).slideUp(settings.accordionUpSpeed).removeClass(accord);
                        $(this).next().slideDown(settings.accordionDownSpeed).addClass(accord);
                        $(this).children(':first-child').toggleClass(settings.arrowRclass + ' ' + settings.arrowDclass);
                    }
                });
            } else {
                if (settings.contentOpen !== null) {
                    if (Array.isArray( settings.contentOpen )) {
                        for (var i = 0; i < settings.contentOpen.length; i++) {
                            var index = settings.contentOpen[i];
                            $($thisEven[index]).children(':first-child').toggleClass(settings.arrowRclass + ' ' + settings.arrowDclass);
                            $($thisOdd[index]).show();
                        }
                    } else {
                        $($thisEven[settings.contentOpen]).children(':first-child').toggleClass(settings.arrowRclass + ' ' + settings.arrowDclass);
                        $($thisOdd[settings.contentOpen]).show();
                    }
                }
                $($thisEven).click(function() {
                    $(this).children(':first-child').toggleClass(settings.arrowRclass + ' ' + settings.arrowDclass);
                    $(this).next().slideToggle(settings.collapseSpeed);
                });
            }
        });
    };
})(jQuery);
