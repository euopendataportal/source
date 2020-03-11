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
    var default_lang = 'en';
    var widgetInput = 'input';
    var widgetTextarea = 'textarea';
    var widgetSelect = 'select';
    // Click on the "New resource..." link at the botton of the resources list
    $('a.js-resource-add').on('click', function (event) {
        var type = $(this).data('type');
        if(type=="documentation") {
            var index = $(this).closest('.dataset_panel').data('index');
            var type = $(this).closest('.resource-tab').data("type");

            init_resource_type(index, type);

            event.preventDefault();
            $('.resource-details_'+type).hide();
            //$('.resource-panel').show();
            var url = $('#add-resource-url-file').val();
            $('#add-resource-url-file').val('');

            //$('.resource-add').show();
            var new_resource_details = add_resource_documentation(index);
            var res_number = new_resource_details.attr('data-resnumber');
            new_resource_details.find("[name='dataset__" + index + "__resources__" + res_number + "__url']").val(url);

            calculate_resource_number();
        }
    });

     function create_resource_list_item(res_number, type, index) {
        var dataset_panel = $("div[data-index='"+index+"']");
        var id_panel = dataset_panel.attr("id");
        var new_resource_list_item = $("#"+id_panel + " .templates_documentation>.resource_list_documentation_item_template").clone();
        new_resource_list_item.attr('id', 'dataset-'+index+'-'+type+'-resource-list_documentation-item-' + res_number);
        new_resource_list_item.attr('class', 'ui-state-default resource-edit drag-bars resource-list-item');
        var a_tag = new_resource_list_item.find('.resource-open-my-panel');
        a_tag.attr('data-resnumber', res_number);
        a_tag.click();
        return new_resource_list_item;
    }

     // Create the item for the list of resources and the resource details panel for the new resource and add them to the page.
	function add_resource_documentation(index) {

        var details_panel = $('#main-resource-panel_documentation_'+index);

        var activeResource = $("#tabs-documentation_" + index).find("ul li.ui-state-active a");
        var dataset_type = activeResource.data('resource');
        var resource_list = $('#resource-list-documentation-div_' + index);
        var displayIframe = false;

        var res_number;
        if (details_panel.children(".resource-details_documentation[data-resnumber]").size() == 0) {
            res_number = 0;
        } else {
            res_number = parseInt(details_panel.children().last().attr("data-resnumber")) + 1;
        }
        var new_resource_details = initialize_documentation_resource_details(res_number, index);
        var new_resource_list_item = create_resource_list_item(res_number, dataset_type, index);
        new_resource_list_item.appendTo(resource_list.find('ul'));
        new_resource_details.appendTo(details_panel);
        toggleSelectedResourceColors(new_resource_list_item);


        new_resource_details.find("#dataset_" + index + "-resources__" + res_number + "__last_modified").datepicker({
            dateFormat: 'yy-mm-dd'
        });
         new_resource_details.find("#dataset_"+index+"-resources__" + res_number + "__iframe_code").closest('.control-group').toggle(displayIframe); //Show/Hide

        return new_resource_details;
    }



    function initialize_documentation_resource_details(res_number, index) {
        var default_lang = 'en';
        var dataset_panel = $("div[data-index='"+index+"']");
        var id_panel = dataset_panel.attr("id");
        var new_resource_details = $("#"+id_panel + " .templates_documentation>.resource-details_documentation-template").clone();
        new_resource_details.attr("id", "dataset_"+index+"-resource_details_documentation_"+ res_number);
        new_resource_details.attr("data-resnumber", res_number);
        new_resource_details.attr("class", "resource-details_documentation");
        new_resource_details.find(".res-number").text(res_number);
        new_resource_details.html(new_resource_details.html().replace(/name="resources_documentation__template/g, "name=\"dataset__"+index+"__resources_documentation__"+res_number));
        new_resource_details.html(new_resource_details.html().replace(/id="resources_documentation__template/g, "id=\"dataset_"+index+"-resources_documentation__"+res_number));


        new_resource_details.find("#dataset_"+index+"-resources_documentation__"+res_number+"__release_date").datepicker({
            dateFormat: 'yy-mm-dd'
        });
        new_resource_details.find("#dataset_"+index+"-resources_documentation__"+res_number+"__modification_date").datepicker({
            dateFormat: 'yy-mm-dd'
        });


        var langs = new_resource_details.find(".resource-lang");
        langs.each(function () {
            var id = $(this).attr("id");
            id = id.replace("__template__", "-" + res_number);
            $(this).attr("id", id);
            if ($(this).text() == default_lang) {
                $(this).addClass('fake-text');
            }
        });

        var title_tag = new_resource_details.find("[name='dataset_"+index+"-resources_documentation__"+res_number+"__title']");
        // TODO : fix this, #resource-list-item not correct anymore
        title_tag.keyup(function (event) {
            if (title_tag.val() != '') {
                $("#dataset_"+index+"-resource-list_documentation-item-" + res_number).find('em').text(title_tag.val());
            } else {
                $("#dataset_"+index+"-resource-list_documentation-item-" + res_number).find('em').text('[new resource]');
            }
        });
        var format_tag = new_resource_details.find("#dataset_"+index+"-resources_documentation__"+res_number+"__format");
        format_tag.append($('.templates_documentation #resource_dropdown_format_template').clone().children());

        var language_tag = new_resource_details.find("#dataset_"+index+"-resources_documentation__"+res_number+"__language");
        language_tag.append($('.templates_documentation #resource_dropdown_language_template').clone().children());
        language_tag.toggleClass("chzn-select");
         $.getScript("../fanstatic/ecportal/vendor/jquery.chosen/1.4.2/chosen.jquery.js", function(){
            language_tag.chosen(config['.chzn-select']);
        });

        var licence_tag = new_resource_details.find("#dataset_"+index+"-resources_documentation__"+res_number+"__licence");
        licence_tag.append($('.templates_documentation #resource_dropdown_licence_template').clone().children());

        var status_tag = new_resource_details.find("#dataset_"+index+"-resources_documentation__"+res_number+"__status");
        status_tag.append($('.templates_documentation #resource_dropdown_status_template').clone().children());

        $("#box-main-info").show();

        return new_resource_details;
    }

    function add_translations_inputs(new_lang, id, name, classes, placeholder, data_module, widgetType) {
        //Title
        if (new_lang == undefined) {
            new_lang = default_lang;
        }

        if (new_lang !== default_lang) {
            if ($("#" + id + "-" + new_lang).length) {
                $("#" + id + "-" + new_lang).show();
            } else {
                if (widgetType == widgetTextarea) {
                    var input = $("<textarea/>").attr("id", id + '-' + new_lang).attr("class", classes).attr("name", name + '-' + new_lang).attr("placeholder", placeholder).data("module", data_module);
                    $("#" + id).after(input);
                } else if (widgetType == widgetInput){
                    var input = $("<input/>").attr("id", id + '-' + new_lang).attr("class", classes).attr("name", name + '-' + new_lang).attr("type", "text").attr("placeholder", placeholder).data("module", data_module);
                    $("#" + id).after(input);
                } else if (widgetType == widgetSelect){

                    var input = $("<select/>").attr("id", id + '-' + new_lang).attr("class", classes).attr("name", name + '-' + new_lang).attr("placeholder", placeholder).data("module", data_module);
                    var options = $("#"+id+" option");
                    var opt = [];
                    $.each(options, function(key, value){
                        opt.push($("<option/>", {'value': $(this).val(), 'text': $(this).text()}));
                    });
                    input.append(opt);

                    $("#"+ id).after(input);
                }
            }
            $('#' + id).hide();
            $('#' + id).closest('.control-group').find("label[for=" + id + "] span").hide();
        } else {
            $('#' + id).show();
            $('#' + id).closest('.control-group').find("label[for=" + id + "] span").show();
        }
    }
});