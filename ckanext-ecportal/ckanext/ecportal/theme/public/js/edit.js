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

// Click on one item of the resources list
$('.resource-edit a').click(show_resource_details);

// Show the resource details panel associated to the selected resource
function show_resource_details(event){
	var resnumber = $(this).attr('data-resnumber');
	event.preventDefault();
	var resnumber = $(this).attr('data-resnumber');
	$('.resource-details').hide();
	$('#resource_details_'+resnumber).show();
	$('.resource-panel').show();

}



$('.format_dropdown').change(add_change_format_listener);

// Filter the mimetype once a format has been selected
function add_change_format_listener(event) {
	var res_number = $(this).parents(".resource-details").first().attr("data-resnumber");
	var selected_format = $(this).find(':selected').val();
	var selected_format_name = $(this).find(':selected').text();
	mimetype_id = 'resources__'+res_number+'__mimetype'
	var mimetype = $('#'+mimetype_id);
	// need to build the drop_down up again (could be filtered).

    // only if a value is selected, we filter
    if (!$.isEmptyObject(selected_format) && !selected_format == "") {
    	var filterValues = [];
    	// getting the values and storing them into an array
    	$.each(resource_mapping_json, function (index, value) {
    		if (selected_format == value[0]) {
    			filterValues.push(index);
    		}
    	});

    	// We filter the mimetype list only if there is a mapping
    	if (!$.isEmptyObject(filterValues)) {
        	$.unique(filterValues);
    		mimetype.empty();
	    	$.each(filterValues, function (index, value) {
	    		mimetype.append($("<option></option>").attr("value", value).text(value));
	    	});
    	} else {
    		// Else we put back the original list and select the mimetype corresponding to the selected format
    		mimetype.empty();
    		mimetype.append($('#resources__template__mimetype').find('option').clone());
    		mimetype.attr('id',mimetype_id);
    		mimetype.find('option[value=\"'+selected_format+'\"]').attr('selected', true);
    	}
    } else {
    	mimetype.empty()
    }

}






// Click on the "X" button in the resource details panel
$('.resource-panel-close').click(function(event) {
	event.preventDefault();
	$('.resource-panel').hide();
});

// Click on the "Delete Resource" button in resource details panel
$('.resource-edit-delete').click(function(event) {
	var res_number = $(this).parents(".resource-details").first().attr("data-resnumber");
	$(this).parents(".resource-details").remove();
	$('#resource-list-item-'+res_number).remove();
	$('.resource-panel').hide();
});

// Click on the "New resource..." link at the botton of the resources list
$('a.js-resource-add').click(function(event) {
	event.preventDefault();
	$('.resource-details').hide();
	$('.resource-add').show();
	$('.resource-panel').show();
});

// Click on the Add button for "Link to a file"
$('#add_link_file').click(function(event) {
	var url = $('#add-resource-url-file').val();
	$('#add-resource-url-file').val('');
	var new_resource_details = add_resource();
	var res_number = new_resource_details.attr('data-resnumber');
	new_resource_details.find("[name='resources__"+res_number+"__url']").val(url);
});


// Click on the Add button for "Link to API"
$('#add_link_api').click(function(event) {
	var url = $('#add-resource-url-api').val();
	$('#add-resource-url-api').val('');
	var new_resource_details = add_resource();
	var res_number = new_resource_details.attr('data-resnumber');
	new_resource_details.find("[name='resources__"+res_number+"__url']").val(url);
});

// Click on the "Choose file" button for "Upload a file"
$('#file').change(function(event){
	var filename = $(this).val().replace(/C:\\fakepath\\/i, '');
	var timestamp = new Date().toISOString().replace(/\:/g,'').slice(0, -5);
	var file_id =  timestamp+"/"+ filename;
	$('div.fileinfo').text(file_id);
});

// Click on the Upload button for "Upload a file"
// see in form_resources.html and storage.upload_handle
$('#upload').click(function(event){
	var fd = new FormData();
	fd.append('file', $('#file')[0].files[0]);
	fd.append('key', $('div.fileinfo').text());
	$.ajax({
	  url: $(this).attr('action'),
	  data: fd,
	  processData: false,
	  contentType: false,
	  type: 'POST',
	  success: function(data){
		url = data;
		$('#file').val('');
		$('div.fileinfo').text('');
		var new_resource_details = add_resource();
		var res_number = new_resource_details.attr('data-resnumber');
		new_resource_details.find("[name='resources__"+res_number+"__url']").val(url);
	  }
	});

});

// Create the item for the list of resources and the resource details panel for the new resource and add them to the page.
function add_resource(){

	var details_panel = $('#main-resource-panel');
	var resource_list = $('#resource-list');
	var res_number;
	if(details_panel.children(".resource-details[data-resnumber]").size() == 0) {
	  res_number = 0;
	} else {
	   res_number = parseInt(details_panel.children().last().attr("data-resnumber"))+1;
	}
	var new_resource_details = initialize_resource_details(res_number);
	var new_resource_list_item = create_resource_list_item(res_number);

	new_resource_list_item.appendTo(resource_list);
	new_resource_details.appendTo(details_panel);
	$('.resource-add').hide();

	return new_resource_details;
}

// Creates and returns the item for the list of resources
function create_resource_list_item(res_number){
	var new_resource_list_item = $( ".templates>.resource_list_item_template" ).clone();
	new_resource_list_item.attr('id','resource-list-item-'+res_number);
	new_resource_list_item.attr('class','ui-state-default resource-edit drag-bars');
	var a_tag = new_resource_list_item.find('.resource-open-my-panel');
	a_tag.attr('data-resnumber', res_number);
	a_tag.click(show_resource_details);
	return new_resource_list_item;
}

//Click on the "X" button of an extra field button to remove it
$('.remove-resource-extra').click(remove_extra_field);

function remove_extra_field(event){
	event.preventDefault();
	$(this).parent().remove();
}

// Click on the "Add Extra Field" button in the resource details panel
$('.add-resource-extra').click(add_resource_extra);

function add_resource_extra(event) {
	event.preventDefault();
	var dn = $(this).parents(".control-group").find(".dynamic-extras");
	var res_number = $(this).parents(".resource-details").first().attr("data-resnumber");
	var new_extra = $( ".templates>.dynamic-extra-template" ).clone();
	new_extra.attr("data-resnumber",res_number);
	new_extra.attr("class","dynamic-extra");
	new_extra.children('.remove-resource-extra').click(remove_extra_field);
	new_extra.appendTo(dn);
}

// Click on the "Save Changes" button at the bottom of the page
$('#dataset-edit').submit(function() {
	$(".dynamic-extra").each(function() {
		var key = $(this).find(".extra-key").first().val();
		if(key != ''){
			var value = $(this).find(".extra-value").first().val();
			var res_number = $(this).attr("data-resnumber");
			console.log(key + ":" + value + " - "+ res_number);
			var new_hidden = $('<input>').attr({
			    type: 'hidden',
			    name: "resources__"+res_number+"__"+key,
			})
			new_hidden.val(value);
			new_hidden.appendTo($('#dataset-edit'));
		}
	});
	$('.templates').each(function(){
		$(this).remove();
	});
	$('#file').remove();
	$('#upload').remove();
	var new_hidden = $('<input>').attr({
	    type: 'hidden',
	    name: "save",
	});
	new_hidden.val("Save Changes");
	new_hidden.appendTo($('#dataset-edit'));

	return true;
});

// Select the new resource panel if there are no resource for the dataset
if($('#main-resource-panel').children(".resource-details[data-resnumber]").size() == 0) {
	$('.js-resource-add').click();
}
