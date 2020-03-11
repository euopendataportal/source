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

function calculate_resource_number() {
   $('.dataset_panel').each(function () {
       var index = $(this).data('index');
       $("#distribution-resource-number_" + index).text($("#resource-list-distribution-div_" + index + " li").length);
       $("#documentation-resource-number_" + index).text($("#resource-list-documentation-div_" + index + " li").length);
       $("#visualization-resource-number_" + index).text($("#resource-list-visualization-div_" + index + " li").length);
   })
}

var toggleSelectedResourceColors = function(selectedResource) {
     // Change the background color
    var tab = selectedResource.closest(".resource-tab");
    var previouslySelected = tab.find('.resource-list-item-selected');
    previouslySelected.toggleClass("resource-list-item-selected resource-list-item");
    selectedResource.closest('li').toggleClass("resource-list-item resource-list-item-selected");
};

function remove_extra_field(event) {
    event.preventDefault();
    $(this).parent().remove();
}

function add_resource_extra(event) {
    event.preventDefault();
    var dn = $(this).parents(".control-group").find(".dynamic-extras");
    var res_number = $(this).parents(".resource-details").first().attr("data-resnumber");
    var new_extra = $(".templates>.dynamic-extra-template").clone();
    new_extra.attr("data-resnumber", res_number);
    new_extra.attr("class", "dynamic-extra");
    new_extra.children('.remove-resource-extra').click(remove_extra_field);
    new_extra.appendTo(dn);
}

function resource_type_options_display(arrayList, index, activeResource){
    $('#resource_details_' +activeResource+ '_template select').find("option").remove();
    arrayList.each(function(){
        var tabText = $(this).text().split('|');
        $($('#resource_details_' +activeResource+ '_template select[name="resources_'+activeResource+'__template__resource_type"]').get(index)).append($('<option>', {
            value: tabText[0],
            text :tabText[1]
        }));
    });
}

function init_resource_type(index, type){
    //var resourceSelect = $(".resource-details").find("select[name$='resource_type']");
    if(!index){
        index = 0
    };
    var activeResource = $("#tabs-"+type+"_"+index).find("ul li.ui-state-active a");
    if (activeResource.data('resource') == "distribution") {
        var distrib = $("#list-resource-distribution_"+ index +" div");
        resource_type_options_display(distrib, index, "distribution");
    //Documentation
    } else if (activeResource.data('resource') == "documentation") {
        var documentation = $("#list-resource-documentation_"+ index +" div");
        resource_type_options_display(documentation, index, "documentation");
    //Visualisation
    } else {
        var visualization = $("#list-resource-visualization_"+ index +" div");
        resource_type_options_display(visualization, index, "visualization");
    }
    $(".resource-add").hide();


}

$(function () {


    // Show the resource details panel associated to the selected resource
    $(document).on('click', 'a.resource-open-my-panel', function (event) {
        var type = $(this).closest(".resource-tab").data('type');
        var resnumber = $(this).attr('data-resnumber');
        event.preventDefault();
        var resnumber = $(this).attr('data-resnumber');
        $('.resource-details_' + type).hide();
        // find dataset index
        var index = $(this).closest('.dataset_panel').data('index');
        var id_str = "dataset_"+index+'-resource_details_'+type+"_"+resnumber;
        $("[id$="+id_str+"]").show();
        toggleSelectedResourceColors($(this));

    });


    // $('.format_dropdown').change(add_change_format_listener);

    // Click on one item of the resources list
    // $('.resource-edit a').on('click', show_resource_details);


	// Click on the Add button for "Link to a file"
	$("input[id^='add_link_file_']").on('click',function(event) {
		$(this).closest('div').find('.resource-add').hide();
		var index = $(this).closest('.div_toggle:visible').data('index');
		var url = $('#dataset-'+index+'-add-resource-url-file').val();
		$('#add-resource-url-file').val('');
		var new_resource_details = add_resource(index);
		var res_number = new_resource_details.attr('data-resnumber');
		new_resource_details.find("[dataset_"+index+"_name='resources__"+res_number+"__url']").val(url);
	});


	// Click on the Add button for "Link to API"
	$("input[id^='add_link_api']").on('click',function(event) {
		var index = $(this).closest('.div_toggle:visible').data('index');
		var url = $('#dataset-'+index+'-add-resource-url-api').val();
		$('#aataset-'+index+'-add-resource-url-api').val('');
		var new_resource_details = add_resource(index);
		var res_number = new_resource_details.attr('data-resnumber');
		new_resource_details.find("[name='dataset__"+index+"__resources__"+res_number+"__url']").val(url);
	});

    // Click on the "Delete Resource" button in resource details panel
	$('.resource-edit-delete').on('click',function(event) {
		var res_number = $(this).parents(".resource-details").first().attr("data-resnumber");
		var index = $(this).closest('.div_toggle:visible').data('index');
		//find resource
		var resource_type = $('select[name=dataset__'+index+'__resources__'+res_number+'__resource_type] option:selected').text();
		var split = resource_type.split(':');
		$('#dataset-'+index+'-'+split[0].toLowerCase()+'-list-item-'+res_number).remove();
		$(this).parents(".resource-details").remove();
		$("#box-main-info").hide();
		$('.resource-panel').hide();
	});

    //TODO: debug this is doing anything?
    $(document).on('click', 'a.js-resource-add', function(event){
        $('.resource-add').hide();
        $(".resource-details:last").show();
    });

       //Click on the "X" button of an extra field button to remove it
    $('.remove-resource-extra').on('click', remove_extra_field);

        // Click on the "Add Extra Field" button in the resource details panel
    $('.add-resource-extra').on('click',add_resource_extra);

        // Click on the "Save Changes" button at the bottom of the page
    $('#ingestion-package-edit').submit(function () {
        $(".dynamic-extra").each(function () {
            var index = $(this).closest('.dataset_panel').data('index');
            var key = $(this).find(".extra-key").first().val();
            if (key != '') {
                var value = $(this).find(".extra-value").first().val();
                var res_number = $(this).attr("data-resnumber");
                console.log(key + ":" + value + " - " + res_number);
                var new_hidden = $('<input>').attr({
                    type: 'hidden',
                    name: "dataset__"+index+"__resources__" + res_number + "__" + key,
                })
                new_hidden.val(value);
                new_hidden.appendTo($('#dataset-edit'));
                $('#file-' + res_number).remove();
                $('.upload').remove();
            }
        });
        $('.templates').each(function () {
            $(this).remove();
        });


        return true;
    });

        $('.js-resource-edit-format').on('change', function (event) {
        var resource_number = $(this).closest('.resource-details').data('resnumber');
        var targetDropDown = 'resources__' + resource_number + '__mimetype';
        var target_select = $('#'+targetDropDown);
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
                        $('#' + targetDropDown.name + ' option[value="' + value[0] + '"]').prop('selected', true);
                    }
                });
            }
        }

    });



	var europeanCountries = [
		'http://publications.europa.eu/resource/authority/country/AUT',
		'http://publications.europa.eu/resource/authority/country/BEL',
		'http://publications.europa.eu/resource/authority/country/BGR',
		'http://publications.europa.eu/resource/authority/country/HRV', //Croatia
		'http://publications.europa.eu/resource/authority/country/CYP',
		'http://publications.europa.eu/resource/authority/country/CZE',
		'http://publications.europa.eu/resource/authority/country/DNK',
		'http://publications.europa.eu/resource/authority/country/EST',
		'http://publications.europa.eu/resource/authority/country/FIN',
		'http://publications.europa.eu/resource/authority/country/FRA',
		'http://publications.europa.eu/resource/authority/country/DEU',
		'http://publications.europa.eu/resource/authority/country/GRC',
		'http://publications.europa.eu/resource/authority/country/HUN',
		'http://publications.europa.eu/resource/authority/country/IRL',
		'http://publications.europa.eu/resource/authority/country/ITA',
		'http://publications.europa.eu/resource/authority/country/LVA',
		'http://publications.europa.eu/resource/authority/country/LTU',
		'http://publications.europa.eu/resource/authority/country/LUX',
		'http://publications.europa.eu/resource/authority/country/MLT',
		'http://publications.europa.eu/resource/authority/country/NLD',
		'http://publications.europa.eu/resource/authority/country/POL',
		'http://publications.europa.eu/resource/authority/country/PRT',
		'http://publications.europa.eu/resource/authority/country/ROU',
		'http://publications.europa.eu/resource/authority/country/SVK',
		'http://publications.europa.eu/resource/authority/country/SVN',
		'http://publications.europa.eu/resource/authority/country/ESP',
		'http://publications.europa.eu/resource/authority/country/SWE',
		'http://publications.europa.eu/resource/authority/country/GBR'
	];

    $(".chzn-select2").select2({width: '94%', placeholder: "Select Some Options"});
	$("input[id*='select-28-countries']").on('click', function () {
        var index = $(this).closest('.div_toggle:visible').data('index');
        var selectedCountries = $("#dataset_" + index + "-geographical_coverage").val() || [];
        for (var i in europeanCountries) {
            if (!~$.inArray(europeanCountries[i], selectedCountries)) {
                selectedCountries.push(europeanCountries[i]);
            }
        }

        $("#dataset_" + index + "-geographical_coverage").val(selectedCountries);
        $("#dataset_" + index + "-geographical_coverage").trigger("change");
    });

    $("input[id*='select-27-countries']").on('click', function () {
        var index = $(this).closest('.div_toggle:visible').data('index');
        var selectedCountries = $("#dataset_" + index + "-geographical_coverage").val() || [];
        var croatia = 'http://publications.europa.eu/resource/authority/country/HRV';
        // european countries - croatia
        var european = europeanCountries.slice();
        european.splice(european.indexOf(croatia), 1);
        for (var i in european) {
            if (!~$.inArray(european[i], selectedCountries)) {
                selectedCountries.push(european[i]);
            }
        }

        $("#dataset_" + index + "-geographical_coverage").val(selectedCountries);
        $("#dataset_" + index + "-geographical_coverage").trigger("change");
    });

    $("input[id*='clear-geographical-coverage']").on('click', function () {
        var index = $(this).closest('.div_toggle:visible').data('index');
        $("#dataset_" + index + "-geographical_coverage").val([]);
        $("#dataset_" + index + "-geographical_coverage").trigger("change");
    });

    //Adding datepickers to inputs
    $("input[id*='temporal_coverage_from']").datepicker({
        dateFormat: 'yy-mm-dd'
    });
    $("input[id*='temporal_coverage_to']").datepicker({
        dateFormat: 'yy-mm-dd'
    });
    $("input[id*='release_date']").datepicker({
        dateFormat: 'yy-mm-dd'
    });
    $("input[id*='modified_date']").datepicker({
        dateFormat: 'yy-mm-dd'
    });


    // Filter the mimetype once a format has been selected
    function add_change_format_listener(event) {
        var index = $(this).closest('.div_toggle:visible').data('index');
        var res_number = $(this).parents(".resource-details").first().attr("data-resnumber");
        var selected_format = $(this).find(':selected').val();
        var selected_format_name = $(this).find(':selected').text();
        var mimetype_id = 'dataset__' + index + '__resources__' + res_number + '__mimetype'
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

    $("div[id^='tabs-']").each(function(){
        var index = $(this).closest(".div_toggle").data("index");
        init_resource_type(index);
        /*$("#resource-list-distribution-div_"+ index).sortable();
        $("#resource-list-documentation-div_"+index).sortable();
        $("#resource-list-visualisation-div_"+index).sortable();*/
    });


	//Distribution
	//Init Resource Type
	//Resource type interaction
	$("div[id^='tabs-']" ).find("li a.ui-tabs-anchor").on("click",function(){
		$('.resource-panel-close').click();
		$('.resource-list-item-selected').toggleClass('resource-list-item-selected resource-list-item');
        var index = $(this).closest(".div_toggle").data("index");
		init_resource_type(index);
	});


    $("li[aria-labelledby]").each(function(){
        if($(this).find("a").data('resource') == 'visualization'){
            $(this).find("a").click();
        }
    });

    calculate_resource_number();


});