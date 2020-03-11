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
	$(function () {
		var arrow_url = $('body').data('site-root') + 'images/arrow_{0}.gif';
        var dropdown = $('#language-selector ul');
        var dropdown_image = $('#language-selector .root img');
        var span = $('#language-selector .root');$
        var lastElement =  $('#language-selector ul>:last-child');
        //hide the most viewed datasets if they go beyond the foreseen box size
        // var neededHeight = $(".most-viewed").outerHeight() - $(".most-viewed h2").outerHeight() - 145;
        // var totalChildHeight = 0;
        // $(".most-viewed ul").children("li").each(function() {
        //     totalChildHeight+= $(this).outerHeight();
        //     if(totalChildHeight> neededHeight) {
        //        $(this).hide();
        //        $(this).nextAll().hide();
        //        return false;
        //     }
        // });

        /* Toggle the display of the iframe code (i.e.: the preview) of a visualisation resource
         *  in the "Visualisations" list on the dataset page */
        $("a.visualisation-button-dataset").click(function(event) {
        	event.preventDefault();

        	var iframeCode = $(this).attr("data-iframe");

        	if ($(this).attr("preview-displayed")) {
        		$(this).parent().parent().parent().next().replaceWith("");
        		$(this).removeAttr("preview-displayed");
        	} else {
        		$(this).parent().parent().parent().after("<ul style=\"list-style: none;\"><li>" + iframeCode + "</li><br></ul>");
        		$(this).attr("preview-displayed", true);
        	}
        });

        /* Toggle the display of the iframe code (i.e.: the preview) of a visualization resource
         * below the "VISUALIZE" button on the resource page */
        $("a.visualisation-button-resource").click(function(event) {
        	event.preventDefault();

        	var iframeCode = $(this).attr("data-iframe");

        	if ($(this).attr("preview-displayed")) {
        		$(this).parent().next().replaceWith("");
        		$(this).removeAttr("preview-displayed");
        	} else {
        		$(this).parent().after("<div class=\"inner\"><br>" + iframeCode + "</div>");
        		$(this).attr("preview-displayed", true);
        	}
        });

        $("#toggler").click(function(){
			$("div.all-domains").toggle();
			$("span.more").toggle();
			$("span.less").toggle();
			});
        span.bind('focus',function() {
            _dropdown(true);
        });
        $(document).keyup(function(e) {
			if (e.keyCode == 27) { _dropdown(false) }   // esc
		})
		lastElement.focusout(function() {
			_dropdown(false);
        });
        dropdown
                .bind('mouseleave', function() {
                        _dropdown(false);
                })

                .parent()
                .bind('click', function() {
                        _dropdown(true);
                })
                ;
        function _dropdown($show) {
                if ($show) {
                        dropdown.fadeIn();
                        dropdown_image.attr('src', arrow_url.replace('{0}', 'up'));
                } else {
                        dropdown.slideUp();
                        dropdown_image.attr('src', arrow_url.replace('{0}', 'down'));
                }
        }


		if ($('#more-meta dl').length > 0) {
			$('.more-meta a').bind('click', function() {
				$('.more-meta').hide();
				$('.less-meta').show();
				$('#more-meta').show();
			});
			$('.less-meta a').bind('click', function() {
				$('.less-meta').hide();
				$('.more-meta').show();
				$('#more-meta').hide();
			});
		} else {
			$('.more-meta').hide();
		}

		function sortby_dropdown() {
			$('select[name="sort"]').on('change', function() {
				$('input[name="sort"]').val($(this).val());
				$('.page-search form').trigger('submit');
			});
		}
		sortby_dropdown();
	});
}(jQuery));
