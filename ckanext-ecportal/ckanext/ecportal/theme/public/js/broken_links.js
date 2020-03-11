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

$(function () {
    var url = $('#broken_links_url').data("url");
    var button = $('#broken_links_showmore');
    var loading = $('.views_infinite_scroll-ajax-loader');

    function get_organisations_html(url, last_id) {
        disableButton();
        enableLoader()
        $.ajax({
            url: last_id !== undefined ? url+"&last_id="+last_id : url,
            processData: false,
            contentType: false,
            type: 'GET',
            success: function (data) {
                var broken_links_list_before = $('#broken_links_list li>div');
                $('#broken_links_list').append(data);
                var broken_links_list_after= $('#broken_links_list li>div');
                if(broken_links_list_before.length < broken_links_list_after.length) {
                    enableButton();
                }
                disableLoader()
            },
            error: function (data) {
                $('#broken_links_list').append("<p>Failed to get broken links.</p>");
                disableLoader()
            }
        })
    }

    function disableButton() {
        button.addClass('hidden')
    }

    function enableButton() {
        button.removeClass('hidden')
    }

    function disableLoader() {
        loading.addClass('hidden')
    }

    function enableLoader() {
        loading.removeClass('hidden')
    }

    $( document ).ready(function() {
        get_organisations_html(url, undefined)
    });

    $("#broken_links_showmore").on("click", function () {
        var broken_links_list = $('#broken_links_list li>div');
        var last_id = undefined;
        if(broken_links_list.length > 0) {
            last_id = broken_links_list.last().attr('index');
        }

        get_organisations_html(url, last_id);
    });
});