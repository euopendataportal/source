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

//var subtimer;

$(window).load(function(){
	//$(document).on('mouseover focus','.op-h-nav>li>a',function(){  if( ! $('.mobile-menu').is(':visible') ) showSubmenu(this); });
	//$(document).on('mouseout blur','.op-h-nav a',function(){ if( ! $('.mobile-menu').is(':visible') ) hideSubmenuInSec(); });
	//$(document).on('mouseover focus', '.sub-menu a',function(){ if( ! $('.mobile-menu').is(':visible') ) cancelHide(); });

	$(document).on('click', '.mobile-menu',function(){ toggleMobileMenu(this); });
    openExternalLinkNewTab();



});
function showSubmenu(el){
	cancelHide(); hideSubmenu();
	$(el).parents('li').first().find('.sub-menu').first().css({display:'inline-block', top:$(el).position().top+$(el).innerHeight()+'px', left:$(el).position().left+'px' });
}
function hideSubmenuInSec(){
	subtimer = window.setTimeout(function(){hideSubmenu()},1000);
}
function hideSubmenu(){
	$('.sub-menu').css({display:'none'});
}
function cancelHide(){
	window.clearTimeout(subtimer);
}

function toggleMobileMenu(el){
	$('.op-h-nav li').slideToggle();
	//$('.op-h-nav li.mobile-menu').show();
}
function openExternalLinkNewTab(){

	$(document).on("click", "a.external-link, .external", function(event){
		if(event.target.target === "_blank" || !event.target.target){
			event.preventDefault();
			window.open($(this).attr("href"), '_blank');
		}
	});



//
//$(function(){
//	$("a.external-link, .external").on('click', function(event){
//		if(event.target.target === "_blank" || !event.target.target){
//			event.preventDefault();
//			window.open($(this).attr("href"), '_blank');
//		}
//	});
//});


}
//Add the footer from the drupal content
jQuery(function(){
    if(typeof loadFooter == 'function'){
        loadFooter();
    }

    // BEGIN Expanded Menus
	jQuery("li.expandable").on("mouseenter", function(){
		var id = jQuery(this).attr("id");
        if(!jQuery("#expanded-menu-"+id).hasClass("active")){
            jQuery(this).find("a").toggleClass("arrow-right");
            jQuery(this).find("a").toggleClass("arrow-down");
            jQuery('#expanded-menu-'+id).show();
        }

	});

    jQuery("li.expandable").on("mouseleave", function(){
        var id = jQuery(this).attr("id");
        if(!jQuery("#expanded-menu-"+id).hasClass("active")){
            jQuery(this).find("a").toggleClass("arrow-right");
            jQuery(this).find("a").toggleClass("arrow-down");
            jQuery('#expanded-menu-'+id).hide();
        }

    });

    jQuery(".expanded-menu").on("mouseenter", function(){
        var id = jQuery(this).data("mlid");
        if(!jQuery("#expanded-menu-"+id).hasClass("active")){
            jQuery("#"+id).find("a").toggleClass("arrow-right");
            jQuery("#"+id).find("a").toggleClass("arrow-down");
            jQuery('#expanded-menu-'+id).show();
        }

    });

    jQuery(".expanded-menu").on("mouseleave", function(){
        var id = jQuery(this).data("mlid");
        if(!jQuery("#expanded-menu-"+id).hasClass("active")){
            jQuery("#"+id).find("a").toggleClass("arrow-right");
            jQuery("#"+id).find("a").removeClass("arrow-down");
            jQuery('#expanded-menu-'+id).hide();
        }

    });
    // END Expanded Menu
});



