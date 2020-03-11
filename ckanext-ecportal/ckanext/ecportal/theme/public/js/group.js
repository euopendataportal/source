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


$('.hidebutton').click(function(event) {
	var selector = $(this).data('selector');
	$("#"+selector).toggle();
	$(this).toggle();
	$(this).siblings('.showbutton').toggle();
});

$('.showbutton').click(function(event) {
	var selector = $(this).data('selector');
	$("#"+selector).toggle();
	$(this).toggle();
	$(this).siblings('.hidebutton').toggle();
});

var set_number = 1
var set_amount = parseInt($("#amount_group_displayed").text())


$('.showmore').click(function(event) {
	set_number++
	var base_url = $("body").attr("data-site-root")
	var q = $("input[name='q']").val()
	var string_data = JSON.stringify({set_number: set_number, set_amount: set_amount, q:q})
    $.ajax({
        url: base_url+'api/action/next_group_list',
        type: 'POST',
        data: string_data,
        dataType: "json",
        success: function(data) {
        	var result = data["result"]
        	var hasmore = result["hasmore"]
        	var groups = result["groups"]
        	// show the new groups
        	groups.forEach(function(group){
        		var new_group = $( ".templates>.group_list" ).clone();

        		new_group.find('p').text(group['display_name'])
        		var group_url = new_group.find('a').attr('href')+'/'+group['name']
        		new_group.find('a').attr('href',group_url);
        		var img_tag = new_group.find('img');
        		img_tag.attr('alt', group['display_name']);
        		if (group['image_display_url'] != ""){
        			img_tag.attr('src', group['image_display_url']);
        		}

        		new_group.appendTo($("#domains_group ul"));
        		$("#domains_group ul").append(document.createTextNode(" "));


        	});

        	// hide the show more if all is shown
        	if (!hasmore){
        		$('.showmore').toggle()
        	}
        }
    });
});
