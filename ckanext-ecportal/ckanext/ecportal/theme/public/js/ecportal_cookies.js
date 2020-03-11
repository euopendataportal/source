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

(function ($) {
  if($("#norole").length>0){
    if (Cookies.get("auth_tkt") && !Cookies.get("NOROLECOOKIECKAN")) {
      $("#norole").dialog(
          {
            resizable: false,
            open: function (event, ui) {
              jQuery(".ui-dialog-titlebar-close", ui.dialog | ui).text("X").addClass("pull-right");
            }
          }
      ).on("dialogclose", function () {
        Cookies.set("NOROLECOOKIECKAN", 1);
      });
    }
  }

$('body').not('.sliding-popup-processed').addClass('sliding-popup-processed').each(function() {
  try {
    if (!cookiesEnabled()) {
      return;
    }
    var status = getCurrentStatus();
    var clicking_confirms = 0;
    var agreed_enabled = 0;
    var popup_hide_agreed = 0;
    if (status == 0) {
      var next_status = 1;
      if (clicking_confirms) {
        $('a, input[type=submit]').bind('click.eu_cookie_compliance', function(){
          if(!agreed_enabled) {
            setStatus(1);
            next_status = 2;
          }
          changeStatus(next_status);
        });
      }

      $('.agree-button').click(function(){
        if(!agreed_enabled) {
          setStatus(1);
          next_status = 2;
        }
        changeStatus(next_status);
      });

     createPopup($('<div>').append($('.cookie-popup')).html());
    } else if(status == 1) {
      createPopup($('<div>').append($('.cookie-popup')).html());
      if (popup_hide_agreed) {
        $('a, input[type=submit]').bind('click.eu_cookie_compliance_hideagreed', function(){
          changeStatus(2);
        });
      }

    } else {
      return;
    }
  }
  catch(e) {
    return;
  }
});


  function createPopup(html) {
    var popup = $(html)
      .attr({"id": "sliding-popup"})
      .height('auto')
      .width('100%')
      .hide();
      popup.appendTo("body");
      var height = popup.height();
      popup.show()
        .attr({"class": "sliding-popup-bottom"})
        .css({"bottom": -1 * height})
        .animate({bottom: 0}, 1000);
    attachEvents();
  }

  function attachEvents() {
	var clicking_confirms = 0;
    var agreed_enabled = 0;
    var lang = $('html').attr('lang');
    $('.find-more-button').click(function(){
        window.location.href = '/euodp/'+lang+'/cookiebannerpage';
    });

	/*$('.refuse_cookie_but_this').click(function(){
      window.location.href = '/euodp/'+lang+'/cookiebannerpage';
	  setStatus(3);
    });*/


    $('.agree-button').click(function(){
      var next_status = 1;
      if(!agreed_enabled) {
        setStatus(1);
        next_status = 2;
      }
      if (clicking_confirms) {
        $('a, input[type=submit]').unbind('click.eu_cookie_compliance');
      }
      changeStatus(next_status);
    });

    $('.hide-popup-button').click(function(){
      changeStatus(2);
    });

    $(".hide-banner").click(function(){
      $(".sliding-popup-bottom").animate({bottom: $("#sliding-popup").height() * -1}, 1000, function () {
         $("#sliding-popup").remove();
      });
    });

  }

function getCurrentStatus() {
	var name = 'cookie-agreed';
	var value = getCookie(name);
	return value;
  }

  function changeStatus(value) {
    var status = getCurrentStatus();
    if (status == value) return;
    $(".sliding-popup-bottom").animate({bottom: $("#sliding-popup").height() * -1}, 1000, function () {
      if(status == 0) {
        $("#sliding-popup").html('').animate({bottom: 0}, 1000);
        attachEvents();
      }
      if(status == 1 || status == 2 || status == 3) {
        $("#sliding-popup").remove();
      }
    });
    setStatus(value);
  }

  function setStatus(status) {
    var date = new Date();
    date.setDate(date.getDate() + 100);
    //var cookie = "cookie-agreed=" + status + ";expires=" + date.toUTCString() + ";path=" + "/euodp";
    Cookies.set('cookie-agreed', status, { expires:date, path:"/euodp/" });
    //document.cookie = cookie;
  }

  function hasAgreed() {
    var status = getCurrentStatus();
    if(status == 1 || status == 2) {
      return true;
    }
    return false;
  }


  /**
   * Verbatim copy of Drupal.comment.getCookie().
   */
  function getCookie(name) {
    return Cookies.get(name) || "";
  };

  function cookiesEnabled() {
    var cookieEnabled = (navigator.cookieEnabled) ? true : false;
      if (typeof navigator.cookieEnabled == "undefined" && !cookieEnabled) {
        document.cookie="testcookie";
        cookieEnabled = (document.cookie.indexOf("testcookie") != -1) ? true : false;
      }
    return (cookieEnabled);
  }


})(jQuery)


