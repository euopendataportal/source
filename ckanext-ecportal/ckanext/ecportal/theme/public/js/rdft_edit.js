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

var toggleSelectedResourceColors = function(selectedResource) {
         // Change the background color
        var tab = selectedResource.closest(".resource-tab");
        var previouslySelected = tab.find('.resource-list-item-selected');
        previouslySelected.toggleClass("resource-list-item-selected resource-list-item");
        selectedResource.closest('li').toggleClass("resource-list-item resource-list-item-selected");
    };

$(function () {

    function calculate_resource_number() {
        $("#distribution-resource-number").text($("#resource-list-distribution li").length);
        $("#documentation-resource-number").text($("#resource-list-documentation li").length);
        $("#visualization-resource-number").text($("#resource-list-visualization li").length);
    }

    // Click on one item of the resources list
    $('.resource-edit a').click();
    $('.remove-extra-metadata').click(remove_extra_field);



    // Show the resource details panel associated to the selected resource
    $(document).on('click', 'a.resource-open-my-panel', function (event) {
        var type = $(this).closest(".resource-tab").data('type');
        var resnumber = $(this).attr('data-resnumber');
        event.preventDefault();
        var resnumber = $(this).attr('data-resnumber');
        $('.resource-details_' + type).hide();
        $('#resource_details_' + type + '_' + resnumber).show();
        $("#box-main-info").show();
        $('.resource-panel').show();
        toggleSelectedResourceColors($(this));

    });


    $(document).on('change', '.format_dropdown', add_change_format_listener);

    // Filter the mimetype once a format has been selected
    function add_change_format_listener(event) {
        var type = $(this).closest('.resource-tab').data('type');
        var res_number = $(this).parents(".resource-details_"+type).first().attr("data-resnumber");
        var selected_format = $(this).find(':selected').val();
        var selected_format_name = $(this).find(':selected').text();
        var mimetype_id = $(this).attr('id').replace('format', 'mimetype');
        var mimetype = $('#' + mimetype_id);
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
                mimetype.attr('id', mimetype_id);
                mimetype.find('option[value=\"' + selected_format + '\"]').attr('selected', true);
            }
        } else {
            mimetype.empty()
        }

    }


    // Click on the "X" button in the resource details panel
    $('.resource-panel-close').click(function (event) {
        event.preventDefault();
        $('.resource-panel').hide();
        $("#box-main-info").hide();
    });

    // Click on the "Delete Resource" button in resource details panel
    // TODO : fix this, #resource-list-item not correct anymore
    $(document).on('click', '.resource-edit-delete', function (event) {
        var type = $(this).closest('.resource-tab').data('type');
        var res_number = $(this).parents(".resource-details_"+type).first().attr("data-resnumber");
        $(this).parents(".resource-details_"+type).remove();
        $('#resource-list_'+ type + '-item-' +res_number).remove();
        $("#box-main-info").hide();
        $('.resource-panel').hide();
        calculate_resource_number();
    });

    // Click on the "New resource..." link at the botton of the resources list
    $('a.js-resource-add').click(function (event) {
        // event.preventDefault();
        // $('.resource-details_'+$(this).data('type')).hide();
        // //$('.resource-add').show();
        // $('.resource-panel').show();
        // var url = $('#add-resource-url-file').val();
        // $('#add-resource-url-file').val('');
        // var new_resource_details = add_resource($(this).data('type'));
        // var res_number = new_resource_details.data('resnumber');
        // new_resource_details.find("[name='resources_"+$(this).data('type')+"__" + res_number + "__url']").val(url);
    });

    $(document).on('click', 'a.js-resource-add', function(event){
        $('.resource-add').hide();
        $(".resource-details_"+$(this).data('type')+":last").show();
    });

    // Click on the Add button for "Link to a file"
    $('#add_link_file').click(function (event) {

    });


    // Click on the Add button for "Link to API"
    $('#add_link_api').click(function (event) {
        var url = $('#add-resource-url-api').val();
        $('#add-resource-url-api').val('');
        var new_resource_details = add_resource();
        var res_number = new_resource_details.attr('data-resnumber');
        new_resource_details.find("[name='resources"+$(this).data('type')+"__" + res_number + "__url']").val(url);
    });

    // Click on the "Choose file" button for "Upload a file"
    $(document).on('change', '.file-upload', function (event) {
        var filename = $(this).val().replace(/C:\\fakepath\\/i, '');
        var timestamp = new Date().toISOString().replace(/\:/g, '').slice(0, -5);
        var file_id = timestamp + "/" + filename;
        $(this).parent().find('.fileinfo').text(file_id);
    });


    // Click on the Upload button for "Upload a file"
    // see in form_resources.html and storage.upload_handle
    $(document).on('click', '.upload', function (event) {
        var default_lang = 'en';
        var $t = $(this);
        var fd = new FormData();
        var type = $(this).closest(".resource-tab").data('type');
        var new_resource_details = $t.closest(".resource-details_"+type);
        var res_number = new_resource_details.attr('data-resnumber');
        fd.append('file', $('#file_'+type+'__' + res_number + '__')[0].files[0]);
        fd.append('key', $('div.fileinfo').text());
        $.ajax({
            url: $t.attr('action'),
            data: fd,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function (data) {
                var url = data;
                var new_resource_details = $t.parent().closest(".resource-details_"+type);
                var res_number = new_resource_details.attr('data-resnumber');
                $('#file_'+type+'__' + res_number + '__').val('');
                $('#file_'+type+'__' + res_number + '__').parent().find('.fileinfo').text('');
                var new_lang = $("#file_"+type+"__"+res_number+'__').closest(".resource-frame").find(".resource-lang + .fake-text").text();
                var field_url = 'download_url'
                if(type == 'documentation'){
                    field_url = 'url'
                }

                if(new_lang != default_lang){
                    new_resource_details.find("[name='resources_"+type+"__" + res_number + "__"+field_url+"-"+new_lang+"']").val(url);
                }else{
                    new_resource_details.find("[name='resources_"+type+"__" + res_number + "__"+field_url+"']").val(url);
                }
            }
        });

    });

    $('#validate').on('click', function (event) {
        var new_hidden = $('<input>').attr({
            type: 'hidden',
            name: "validate",
        })
        new_hidden.val("Validate Changes");
        new_hidden.appendTo($('#dataset-edit'));
    });

    $('#save_published').on('click', function (event) {
        var new_hidden = $('<input>').attr({
            type: 'hidden',
            name: "save"
        });
        new_hidden.val("Save Changes");
        new_hidden.appendTo($('#dataset-edit'));

        var privacy_hidden = $('<input>').attr({
			type: 'hidden',
			name: "private",
		})
		privacy_hidden.val("False");
        privacy_hidden.appendTo($('#dataset-edit'));
    });

    $('#save_draft').on('click', function (event) {
        $('#field-private-true').prop("checked", true);
        var new_hidden = $('<input>').attr({
            type: 'hidden',
            name: "save"
        });
        new_hidden.val("Save Changes");
        new_hidden.appendTo($('#dataset-edit'));
        var privacy_hidden = $('<input>').attr({
			type: 'hidden',
			name: "private",
		})
		privacy_hidden.val("True");
        privacy_hidden.appendTo($('#dataset-edit'));
    });

    $('#cancel').on('click', function (event) {
       $('#dataset-edit').attr('action', $(this).attr( "action" ));
    });


    $(".assign-doi-line-button").on('click', function(e){
        var action = $(this).data("action");
        var publisher = $("#owner_org").val();
        var uri = $(this).data("uri") || undefined;
        if(action && publisher){
            $.post($(this).data("action"), {"publisher" : publisher, "uri": uri} ,function(data){
                $("#doi").val(data);
                $(".assign-doi-line-button").data("action", null).removeAttr('data-action').prop("disabled", true);
            });
        }

    });

        // Click on the "Add Extra Field" button in the resource details panel
    $(document).on('click', '.add-resource-extra', function(event){
        event.preventDefault();
        var type = $(this).closest('.resource-tab').data('type');
        var dn = $(this).parents(".control-group").find(".dynamic-extras");
        var res_number = $(this).parents(".resource-details_"+type).attr("data-resnumber");

        var new_extra = $(".templates_"+type+">.dynamic-extra-template").clone();
        new_extra.attr("data-resnumber", res_number);
        new_extra.attr("data-type", type);
        var count = $(".dynamic-extra[data-type='"+type+"']").size();
        new_extra.attr("class", "dynamic-extra");
        new_extra.children('.remove-resource-extra').click(remove_extra_field);
        new_extra.children('.extra-key').attr("name", "resources_"+type+"__"+res_number+"__extras__"+count+"__key");
        new_extra.children('.extra-value').attr("name", "resources_"+type+"__"+res_number+"__extras__"+count+"__value");
        new_extra.appendTo(dn);
    });


    $("#extra-add").on('click', function(event){
        var dn = $("#extra_fields_all_groups");
        var res_number = $("#extra_fields_all_groups .extra_fields_group").length;
        var new_extra = $("#extras > div.templates > div.extra_fields_group").clone();
        new_extra.data("num", res_number);
        new_extra.find("#key > div > input").attr("id","extras__"+res_number+"__key")
        new_extra.find("#key > div > input").attr("name","extras__"+res_number+"__key")
        new_extra.find("#key").attr("id", "extra-group-key-"+res_number);
        new_extra.find('.remove-extra').click(remove_extra_field);
        new_extra.find("#value > div > input").attr("id","extras__"+res_number+"__value")
        new_extra.find("#value > div > input").attr("name","extras__"+res_number+"__value")
        new_extra.find("#value").attr("id", "extra-group-value-"+res_number);
        new_extra.appendTo(dn);
    });

// Create the item for the list of resources and the resource details panel for the new resource and add them to the page.
function add_resource(activeResource){
    }

    // Creates and returns the resource details panel
    function initialize_resource_details(res_number, type) {
    }

    // Creates and returns the item for the list of resources
    function create_resource_list_item(res_number, type) {
    }

    //Click on the "X" button of an extra field button to remove it
    $('.remove-resource-extra').click(remove_extra_field);

    $('.remove-extra').on('click', function(){
        $(this).parent().remove();
    });

    function remove_extra_field(event) {
        event.preventDefault();
        $(this).parent().remove();
    }


    // Click on the "Save Changes" button at the bottom of the page
    $('#dataset-edit').submit(function () {
        $(".dynamic-extra").each(function () {
            var key = $(this).find(".extra-key").first().val();
            if (key != '') {
                var value = $(this).find(".extra-value").first().val();
                var res_number = $(this).attr("data-resnumber");
                var type = $(this).closest('.resource-tab').data('type');
                var new_hidden = $('<input>').attr({
                    type: 'hidden',
                    name: "resources_"+type+"__" + res_number + "__" + key,
                });
                new_hidden.val(value);
                new_hidden.appendTo($('#dataset-edit'));
                $('#file_'+type+'-' + res_number).remove();
                $('.upload').remove();
            }
        });
        $('.templates_distribution').each(function () {
            $(this).remove();
        });
          $('.templates_documentation').each(function () {
            $(this).remove();
        });
        $('.templates_visualization').each(function () {
            $(this).remove();
        });

        return true;
    });

    $('.js-resource-edit-format').on('change', function (event) {
        var resource_number = $(this).closest('.resource-details').data('resnumber');
        var targetDropDown = 'resources__'+resource_number+'__mimetype';
        var target_select = $('#' + targetDropDown);
        $(target_select).empty();
        $.each(resource_dropdown, function (index, value) {
            $(target_select).append($("<option></option>").attr("value", value[0]).text(value[0]));
        });
        // search value for the format
        var selectedFormatName = $(this).find(":selected").val();

        // only if a value is selected, we filter
        if (!jQuery.isEmptyObject(selectedFormatName) && !selectedFormatName == "") {
            var filterValues = [];
            // getting the values and storing them into an array
            $.each(resource_mapping_json, function (index, value) {
                if (selectedFormatName == value[0]) {
                    filterValues.push(index);
                }
            });

            // only if we have any values, we filter, otherwise the default list is returned
            if (!jQuery.isEmptyObject(filterValues)) {
                // remove duplicates
                $.unique(filterValues);
                // empty dropdown
                $(target_select).empty();
                $.each(filterValues, function (index, value) {
                    $(target_select).append($("<option></option>").attr("value", value).text(value));
                });
            } else {
                // if the filterValues are empty, lets preselect the value from the default dropdown
                // find the value
                $.each(resource_dropdown, function (index, value) {
                    if (selectedFormatName == value[0]) {
                        $('#' + targetDropDown + ' option[value="' + value[0] + '"]').prop('selected', true);
                    }
                });
            }
        }

    });
});
