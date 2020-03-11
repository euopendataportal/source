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

/*
 * Cookie Storage for jQuery Collapse
 * --
 * source: http://github.com/danielstocks/jQuery-Collapse/
 * site: http://webcloud.se/jQuery-Collapse
 *
 * @author Daniel Stocks (http://webcloud.se)
 * Copyright 2013, Daniel Stocks
 * Released under the MIT, BSD, and GPL Licenses.
 */

(function($) {

  var cookieStorage = {
    expires: function() {
      var now = new Date();
      return now.setDate(now.getDate() + 1);
    }(),
    setItem: function(key, value) {
      document.cookie = key + '=' + value + '; expires=' + this.expires +'; path=/';
    },
    getItem: function(key) {
      key+= "=";
      var item = "";
      $.each(document.cookie.split(';'), function(i, cookie) {
        while (cookie.charAt(0)==' ') cookie = cookie.substring(1,cookie.length);
        if(cookie.indexOf(key) === 0) {
          item = cookie.substring(key.length,cookie.length);
        }
      });
      return item;
    }
  };

  $.fn.collapse.cookieStorage = cookieStorage;

})(jQuery);
