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


    // function toggleSelectedResourceColors(selectedResource) {
    //     // Change the background color
    //     var previouslySelected = $('.resource-list-item-selected');
    //     previouslySelected.toggleClass("resource-list-item-selected resource-list-item");
    //     selectedResource.closest('li').toggleClass("resource-list-item resource-list-item-selected");
    // }




     // Creates and returns the item for the list of resources
    function create_resource_list_item(res_number) {
        var new_resource_list_item = $(".templates_visualization>.resource_list_visualization_item_template").clone();
        new_resource_list_item.attr('id', 'resource-list_visualization-item-' + res_number);
        new_resource_list_item.attr('class', 'ui-state-default resource-edit drag-bars resource-list-item');
        var a_tag = new_resource_list_item.find('.resource-open-my-panel');
        a_tag.attr('data-resnumber', res_number);
        a_tag.click();
        return new_resource_list_item;
    }

    function add_resource_visualization(activeResource){

        var details_panel = $('#main-resource-panel_'+activeResource);
        var res_number;
        if (details_panel.children(".resource-details_"+activeResource+"[data-resnumber]").size() == 0) {
            res_number = 0;
        } else {
            res_number = parseInt(details_panel.children().last().attr("data-resnumber")) + 1;
        }

        var resource_list = $('#resource-list-visualization');
        var new_resource_details = initialize_visualization_resource_details(res_number);


    var new_resource_list_item = create_resource_list_item(res_number);

        new_resource_list_item.appendTo(resource_list);
        new_resource_details.appendTo(details_panel);
        toggleSelectedResourceColors(new_resource_list_item);
        return new_resource_details;
    }

    function initialize_visualization_resource_details(res_number) {
        var default_lang = 'en';
        var new_resource_details = $(".templates_visualization>.resource-details_visualization-template").clone();
        new_resource_details.attr("id", "resource_details_visualization_"+ res_number);
        new_resource_details.attr("data-resnumber", res_number);
        new_resource_details.attr("class", "resource-details_visualization");
        new_resource_details.find(".res-number").text(res_number);
        new_resource_details.html(new_resource_details.html().replace(/template/g, res_number));


        new_resource_details.find("#resources_visualization__"+res_number+"__release_date").datepicker({
            dateFormat: 'yy-mm-dd'
        });
        new_resource_details.find("#resources_visualization__"+res_number+"__modification_date").datepicker({
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
        var title_tag = new_resource_details.find("[name='resources_visualization__"+res_number+"__title']");
        // TODO : fix this, #resource-list-item not correct anymore
        title_tag.keyup(function (event) {
            if (title_tag.val() != '') {
                $("#resource-list_visualization-item-" + res_number).find('em').text(title_tag.val());
            } else {
                $("#resource-list_visualization-item-" + res_number).find('em').text('[new resource]');
            }
        });
        var format_tag = new_resource_details.find("#resources_visualization__"+res_number+"__format");
        format_tag.append($('.templates_visualization #resource_dropdown_format_template').clone().children());

        var language_tag = new_resource_details.find("#resources_visualization__"+res_number+"__language");
        language_tag.append($('.templates_visualization #resource_dropdown_language_template').clone().children());
        language_tag.toggleClass("chzn-select");
         $.getScript("../fanstatic/ecportal/vendor/jquery.chosen/1.4.2/chosen.jquery.js", function(){
            language_tag.chosen(config['.chzn-select']);
        });

        var licence_tag = new_resource_details.find("#resources_visualization__"+res_number+"__licence");
        licence_tag.append($('.templates_visualization #resource_dropdown_licence_template').clone().children());

        var status_tag = new_resource_details.find("#resources_visualization__"+res_number+"__status");
        status_tag.append($('.templates_visualization #resource_dropdown_status_template').clone().children());

        $("#box-main-info").show();

        return new_resource_details;
    }

    function add_translations_inputs(new_lang, id, classes, placeholder, data_module, widgetType) {
        //Title
        if (new_lang == undefined) {
            new_lang = default_lang;
        }

        if (new_lang !== default_lang) {
            if ($("#" + id + "-" + new_lang).length) {
                $("#" + id + "-" + new_lang).show();
            } else {
                if (widgetType == widgetTextarea) {
                    var input = $("<textarea/>").attr("id", id + '-' + new_lang).attr("class", classes).attr("name", id + '-' + new_lang).attr("placeholder", placeholder).data("module", data_module);
                    $("#" + id).after(input);
                } else if (widgetType == widgetInput){
                    var input = $("<input/>").attr("id", id + '-' + new_lang).attr("class", classes).attr("name", id + '-' + new_lang).attr("type", "text").attr("placeholder", placeholder).data("module", data_module);
                    $("#" + id).after(input);
                } else if (widgetType == widgetSelect){

                    var input = $("<select/>").attr("id", id + '-' + new_lang).attr("class", classes).attr("name", id + '-' + new_lang).attr("placeholder", placeholder).data("module", data_module);
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


    // Click on the "New resource..." link at the botton of the resources list
    $('a.js-resource-add').click(function (event) {
        var type = $(this).data('type');
        if(type=="visualization"){
            event.preventDefault();
            $('.resource-details_'+$(this).data('type')).hide();
            //$('.resource-add').show();
            $('.resource-panel').show();
            var url = $('#add-resource-url-file').val();
            $('#add-resource-url-file').val('');
            var new_resource_details = add_resource_visualization($(this).data('type'));
            var res_number = new_resource_details.data('resnumber');
            new_resource_details.find("[name='resources_"+$(this).data('type')+"__" + res_number + "__url']").val(url);
        }
    });


    $(document).on('click', '.resource-lang', function () {
        var type = $(this).closest('.resource-tab').data('type');

        if(type=='visualization'){
            var new_lang = this.text;

            // Hide/show the mandatory star for Title and Description labels
            if (new_lang == "en") {
                $(this).closest(".resource-details_"+type).find(".field_required").show();
            } else {
                $(this).closest(".resource-details_"+type).find(".field_required").hide();
            }

            var resNumber = $(this).closest(".resource-details_"+type).data("resnumber");

            $("#resource_details_" + type + "_"+ resNumber + " .js-resource-edit-title-field").hide();
            $("#resource_details_" + type + "_"+ resNumber + " .js-resource-edit-description").hide();
            // $("#resource_details_" + type + "_"+ resNumber + " .js-resource-edit-download_url").hide();


            add_translations_inputs(new_lang, "resources_visualization__" + resNumber + "__title", "js-resource-edit-title-field translatable-resource-field", "", "", widgetInput);
            add_translations_inputs(new_lang, "resources_visualization__" + resNumber + "__description", "js-resource-edit-description markdown-input translatable-resource-field", "", "", widgetTextarea);
            // add_translations_inputs(new_lang, "resources_visualization__" + resNumber + "__download_url", "js-resource-edit-download_url long translatable-resource-field", "", "", widgetInput);


            $(this).closest("#resource-languages").find(".fake-text").toggleClass("fake-text");
            $(this).toggleClass("fake-text");
        }
    });

});