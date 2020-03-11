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

    var widgetInput = 'input';
    var widgetTextarea = 'textarea';
    var widgetSelect = 'select';

    var arrow_url = $('body').data('site-root') + 'images/arrow_{0}.gif';
    var dropdown = $('#language-selector ul');
    var dropdown_image = $('#language-selector .root img');
    var span = $('#language-selector .root');
    var lastElement = $('#language-selector ul>:last-child');
    //hide the most viewed datasets if they go beyond the foreseen box size
    // var neededHeight = $(".most-viewed").outerHeight() - $(".most-viewed h2").outerHeight() - 145;
    // var totalChildHeight = 0;
    // $(".most-viewed ul").children("li").each(function () {
    //     totalChildHeight += $(this).outerHeight();
    //     if (totalChildHeight > neededHeight) {
    //         $(this).hide();
    //         $(this).nextAll().hide();
    //         return false;
    //     }
    // });


    $(".to-datepicker").each(function(){
        $(this).datepicker({
            dateFormat: 'yy-mm-dd'
        });
    });


    /* Toggle the display of the iframe code (i.e.: the preview) of a visualisation resource
     *  in the "Visualisations" list on the dataset page */
    $("a.visualisation-button-dataset").click(function (event) {
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
    $("a.visualisation-button-resource").click(function (event) {
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

    $("#toggler").click(function () {
        $("div.all-domains").toggle();
        $("span.more").toggle();
        $("span.less").toggle();
    });

    span.bind('focus', function () {
        _dropdown(true);
    });
    $(document).keyup(function (e) {
        if (e.keyCode == 27) {
            _dropdown(false)
        }   // esc
    });
    lastElement.focusout(function () {
        _dropdown(false);
    });
    dropdown
        .bind('mouseleave', function () {
            _dropdown(false);
        })

        .parent()
        .bind('click', function () {
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
        $('.more-meta a').bind('click', function () {
            $('.more-meta').hide();
            $('.less-meta').show();
            $('#more-meta').show();
        });
        $('.less-meta a').bind('click', function () {
            $('.less-meta').hide();
            $('.more-meta').show();
            $('#more-meta').hide();
        });
    } else {
        $('.more-meta').hide();
    }

    function sortby_dropdown() {
        $('select[name="sort"]').on('change', function () {
            $('input[name="sort"]').val($(this).val());
            $('.page-search form').trigger('submit');
        });
    }

    sortby_dropdown();

    function sticky_relocate() {
        var window_top = $(window).scrollTop();
        if ($('#sticky-anchor').length > 0) {
            var div_top = $('#sticky-anchor').offset().top;
            if (window_top > div_top) {
                $('#sticky').addClass('stick');
                $('#sticky-anchor').height($('#sticky').outerHeight());
            } else {
                $('#sticky').removeClass('stick');
                $('#sticky-anchor').height(0);
            }

            if (($("#sticky").offset().top + $('#sticky').outerHeight()) > $("#resources-list-anchor").offset().top) {
                var currentCss = parseInt($(".resources-list").css("top"));

                //$(".resources-list").css("top", ($("#sticky").offset().top+$('#sticky').outerHeight())-$(".resources-list").offset().top+currentCss);
            } else {
                $(".resources-list").css("top", 0);
            }
        }
    }


    var default_lang = 'en';

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
                } else if (widgetType == widgetInput) {
                    var input = $("<input/>").attr("id", id + '-' + new_lang).attr("class", classes).attr("name", id + '-' + new_lang).attr("type", "text").attr("placeholder", placeholder).data("module", data_module);
                    $("#" + id).after(input);
                } else if (widgetType == widgetSelect) {

                    var input = $("<select/>").attr("id", id + '-' + new_lang).attr("class", classes).attr("name", id + '-' + new_lang).attr("placeholder", placeholder).data("module", data_module);
                    var options = $("#" + id + " option");
                    var opt = [];
                    $.each(options, function (key, value) {
                        opt.push($("<option/>", {'value': $(this).val(), 'text': $(this).text()}));
                    });
                    input.append(opt);

                    $("#" + id).after(input);
                }
            }
            $('#' + id).hide();
            $('#' + id).closest('.control-group').find("label[for=" + id + "] span").hide();
        } else {
            $('#' + id).show();
            $('#' + id).closest('.control-group').find("label[for=" + id + "] span").show();
        }
    }

    function copy_translations_select(new_lang, id) {
        if (new_lang == undefined) {
            new_lang = default_lang;
        }

        if (new_lang !== default_lang) {
            if ($("#" + id + "-" + new_lang).length) {
                $("#" + id + "-" + new_lang).show();
            } else {
                var select = $('#' + id).clone();
                select.find("option").prop("selected", false);
                select.attr('id', id + "-" + new_lang).attr("name", id + "-" + new_lang);
                $("#" + id).after(select);
                select.show();
                if (select.attr('id').indexOf("mimetype") >= 0) {
                    select.find("option").remove();
                    select.val('');
                }

            }
            $('#' + id).hide();
            $('#' + id).closest('.control-group').find("label[for=" + id + "] span").hide();
        } else {
            $('#' + id).show();
            $('#' + id).closest('.control-group').find("label[for=" + id + "] span").show();
        }
    }


    function resource_type_options_display(arrayList, type) {
        $('#resource_details_' + type + '_template select').find("option").remove();
        arrayList.each(function () {
            var tabText = $(this).text().split('|');
            $('#resource_details_' + type + '_template select[name="resources_' + type + '__template__resource_type"]').append($('<option>', {
                value: tabText[0],
                text: tabText[1]
            }));
        });
    }

    function init_resource_type(activeResource) {
        //var resourceSelect = $(".resource-details").find("select[name$='resource_type']");
        if (activeResource == "distribution") {
            // $("#resource-list-distribution-div").show();
            // $("#resource-list-documentation-div").hide();
            // $("#resource-list-visualisation-div").hide();
            var distrib = $("#list-resource-distribution div");
            resource_type_options_display(distrib, activeResource);
            //Documentation
        } else if (activeResource == "documentation") {
            // $("#resource-list-distribution-div").hide();
            // $("#resource-list-documentation-div").show();
            // $("#resource-list-visualisation-div").hide();
            var documentation = $("#list-resource-documentation div");
            resource_type_options_display(documentation, activeResource);
            //Visualisation
        }
        else {
            // $("#resource-list-distribution-div").hide();
            // $("#resource-list-documentation-div").hide();
            // $("#resource-list-visualisation-div").show();
            var visualisation = $("#list-resource-visualization div");
            resource_type_options_display(visualisation, activeResource);
        }

        // $(".resource-add").hide();
    }

    function calculate_resource_number() {
        $("#distribution-resource-number").text($("#resource-list-distribution li").length);
        $("#documentation-resource-number").text($("#resource-list-documentation li").length);
        $("#visualization-resource-number").text($("#resource-list-visualization li").length);
    }

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
    //$(".chzn-select").chosen();

    $("#geographical_coverage").select2({width: '94%', placeholder: "Select Some Options"});
    $("#select-28-countries").on('click', function () {
         var selectedCountries = $("#geographical_coverage").val() || [];
        for (var i in europeanCountries) {
            if (!~$.inArray(europeanCountries[i], selectedCountries)) {
                selectedCountries.push(europeanCountries[i]);
            }
        }


        $("#geographical_coverage").val(selectedCountries);
        $("#geographical_coverage").trigger('change');
    });

    $("#select-27-countries").on('click', function () {
        var selectedCountries = $("#geographical_coverage").val() || [];
        var croatia = 'http://publications.europa.eu/resource/authority/country/HRV';
        // european countries - croatia
        var european = europeanCountries.slice();
        european.splice(european.indexOf(croatia), 1);
        for (var i in european) {
            if (!~$.inArray(european[i], selectedCountries)) {
                selectedCountries.push(european[i]);
            }
        }

        $("#geographical_coverage").val(selectedCountries);
        $("#geographical_coverage").trigger("change");
    });

    $("#clear-geographical-coverage").on('click', function () {
        $("#geographical_coverage").val([]);
        $("#geographical_coverage").trigger("change");
    });

    $(window).scroll(sticky_relocate);
    sticky_relocate();

    //Adding datepickers to inputs
    if ($("#temporal_coverage_from").length) {
        $("#temporal_coverage_from").datepicker({
            dateFormat: 'yy-mm-dd'
        });
        $("#temporal_coverage_to").datepicker({
            dateFormat: 'yy-mm-dd'
        });
        $("#release_date").datepicker({
            dateFormat: 'yy-mm-dd'
        });
        $("#modified_date").datepicker({
            dateFormat: 'yy-mm-dd'
        });
    }

    $("#div.span3").height($('#resource-anchor').outerHeight());

    add_translations_inputs(default_lang, "title", "js-title", "A short descriptive title for the dataset", "custom_slug-preview-target");
    $(".dataset-lang[data-language='" + default_lang + "']").toggleClass("fake-text");

    $(".resource-lang").each(function () {
        if ($(this).text() == default_lang) {
            $(this).toggleClass("fake-text");
        }
    });


    if ($("#tabs-distribution").length && $("#tabs-documentation").length && $("#tabs-visualization").length) {
        //Tabs for Resources
        $("#tabs-distribution").tabs();
        $("#tabs-documentation").tabs();
        $("#tabs-visualization").tabs();


        init_resource_type();

        //Distribution
        //Init Resource Type
        //Resource type interaction
        $("#tabs-distribution").find("li a.ui-tabs-anchor").on("click", function () {
            $('.resource-panel-close').click();
            $('.resource-list-item-selected').toggleClass('resource-list-item-selected resource-list-item');
            init_resource_type();
        });
        $("#tabs-documentation").find("li a.ui-tabs-anchor").on("click", function () {
            $('.resource-panel-close').click();
            $('.resource-list-item-selected').toggleClass('resource-list-item-selected resource-list-item');
            init_resource_type();
        });
        $("#tabs-visualization").find("li a.ui-tabs-anchor").on("click", function () {
            $('.resource-panel-close').click();
            $('.resource-list-item-selected').toggleClass('resource-list-item-selected resource-list-item');
            init_resource_type();
        });

        $("#resource-list-distribution").sortable();
        $("#resource-list-documentation").sortable();
        $("#resource-list-visualization").sortable();
    }
    //Languages list interaction
    $(".dataset-lang").on("click", function () {

        var new_lang = $(this).data('language');

        //Hide input field of the prev lang
        $(".js-title").hide();
        $(".js-alt-title").hide();
        $(".js-description").hide();

        //Display or create input for new lang
        add_translations_inputs(new_lang, "title", "js-title translatable-field", "A short descriptive title for the dataset", "custom_slug-preview-target", widgetInput);
        add_translations_inputs(new_lang, "alternative_title", "js-alt-title translatable-field", "", "", widgetInput);
        add_translations_inputs(new_lang, "description", "js-description markdown-input translatable-field", "The main description of the dataset ...", "", widgetTextarea);

        $(".fake-text").toggleClass("fake-text");
        $(".dataset-lang[data-language='" + new_lang + "']" ).toggleClass("fake-text");
    });

    $(document).on('click', '.resource-lang', function () {
        // var new_lang = this.text;
        //
        // var type = $(this).closest('.resource-tab').data('type');
        // // Hide/show the mandatory star for Title and Description labels
        // if (new_lang == "en") {
        //     $(this).closest(".resource-details_"+type).find(".field_required").show();
        // } else {
        //     $(this).closest(".resource-details_"+type).find(".field_required").hide();
        // }
        //
        // var resNumber = $(this).closest(".resource-details_"+type).data("resnumber");
        //
        // $("#resource_details_" + type + "_"+ resNumber + " .js-resource-edit-name-field").hide();
        // $("#resource_details_" + type + "_"+ resNumber + " .js-resource-edit-description").hide();
        // $("#resource_details_" + type + "_"+ resNumber + " .js-resource-edit-url").hide();
        // $("#resource_details_" + type + "_"+ resNumber + " .js-resource-edit-last_modified").hide();
        // $("#resource_details_" + type + "_"+ resNumber + " .js-resource-edit-size").hide();
        // $("#resource_details_" + type + "_"+ resNumber + " .js-resource-iframe-code").hide();
        // //$("#resource_details_" + resNumber + " .js-resource-edit-format").hide();
        // //$("#resource_details_" + resNumber + " .js-resource-edit-mimetype").hide();
        //
        //
        // add_translations_inputs(new_lang, "resources_"+type+"__" + resNumber + "__name", "js-resource-edit-name-field translatable-resource-field", "", "");
        // add_translations_inputs(new_lang, "resources_"+type+"__" + resNumber + "__description", "js-resource-edit-description markdown-input translatable-resource-field", "", "", true);
        //
        // add_translations_inputs(new_lang, "resources_"+type+"__" + resNumber + "__iframe_code", "js-resource-iframe-code markdown-input translatable-resource-field", "", "", true);
        //
        // add_translations_inputs(new_lang, "resources_"+type+"__" + resNumber + "__url", "js-resource-edit-url long translatable-resource-field", "", "");
        // add_translations_inputs(new_lang, "resources_"+type+"__" + resNumber + "__last_modified", "js-resource-edit-last_modified input-small half-input-resource image-calendar image-input translatable-resource-field", "", "");
        // $("#resources_"+type+"__" + resNumber + "__last_modified-" + new_lang).datepicker({
        //     dateFormat: 'yy-mm-dd'
        // });
        //
        // add_translations_inputs(new_lang, "resources_"+type+"__" + resNumber + "__size", "js-resource-edit-size long half-input-resource half-input-resource-right translatable-resource-field", "", "");
        //
        // //copy_translations_select(new_lang, "resources__" + resNumber + "__format");
        // //copy_translations_select(new_lang, "resources__" + resNumber + "__mimetype");
        //
        //
        // //$("#resources__" + resNumber.text() + "__format-"+new_lang).addClass("format_dropdown");
        //
        //
        // $(this).closest("#resource-languages").find(".fake-text").toggleClass("fake-text");
        // $(this).toggleClass("fake-text");
    });

    $(".js-resource-add").on("click", function () {
        init_resource_type($(this).data('type'));
        calculate_resource_number();
    });

    calculate_resource_number();

    $("#box-main-info").hide();


    $(document).on("change", ".translatable-field", function () {
        show_up_translations($(this), false);
    });

    $(document).on("change", ".translatable-resource-field", function () {
        show_up_translations($(this), true);
    });

    /*$(document).on("change", "select.half-input-resource-right", function(){
     var type = $(this).closest('.resource-tab').data('type');
     var dataResNum = $(this).closest('.resource-details_'+type).data('resnumber');
     if($(this).attr('name') == 'resources_'+type+'__'+dataResNum+'__resource_type'){
     if($(this).val() == 'http://publications.europa.eu/resource/authority/distribution-type/VISUALIZATION'){
     $("#resources_"+type+"__"+ dataResNum +"__iframe_code").closest('.control-group').show();
     }else{
     $("#resources_"+type+"__"+ dataResNum +"__iframe_code").val("");
     $("#resources_"+type+"__"+ dataResNum +"__iframe_code").closest('.control-group').hide();
     show_up_translations($("#resources_"+type+"__"+ dataResNum +"__iframe_code"), true);
     $(document).find('.js-resource-iframe-code+.translatable-resource-field').each(function(){
     $(this).val("");
     show_up_translations($(this), true);
     });
     };
     }
     });*/


    function show_up_translations(elem, isResource) {
        if (isResource) {
            var type = elem.closest('.resource-tab').data('type');
            var selector = elem.closest(".resource-details_" + type);
            var translatable = ".translatable-resource-field";
            var langList = selector.find(".resource-lang");
        } else {
            var selector = $("#dataset-edit");
            var translatable = ".translatable-field";
            var langList = selector.find(".dataset-lang");
        }

        var lang = elem.attr('id').split('-')[1];


        if (!lang || lang.length > 2) {
            //console.log(elem.attr('id'))
            lang = default_lang; //Fallback
        }

        var oneFill = false;

        selector.find(translatable).each(function () {
            var languageTab = $(this).attr('id').split('-');
            if (languageTab.length == 2) {
                if (languageTab[1] == lang || (languageTab[1].length > 2 && lang == default_lang)) {
                    if ($(this).val()) oneFill = true
                }
            } else if (languageTab.length == 3) {
                if (languageTab[2] == lang || (languageTab[2].length > 2 && lang == default_lang)) {
                    if ($(this).val()) oneFill = true
                }
            } else if (lang == default_lang && languageTab.length == 1) {
                if ($(this).val()) {
                    oneFill = true
                }
            }
        });

        if (oneFill) {
            langList.each(function () {
                if ($(this).text() == lang) {
                    $(this).css("font-weight", "bold");
                    $(this).css("text-transform", "uppercase");
                }
            });
        } else {
            langList.each(function () {
                if ($(this).text() == lang) {
                    $(this).css("font-weight", "");
                    $(this).css("text-transform", "");
                }
            });

        }
    }

    function init_show_up_translation_edit() {
        $(".translatable-field").each(function () {
            show_up_translations($(this), false);
        });

        $(".translatable-resource-field").each(function () {
            show_up_translations($(this), true);
        });
    }

    init_show_up_translation_edit();
    if($("#creation-dataset-form").length>0){
        $("#creation-dataset-form").tabs();
    }

    var popupContainer = $(".data-citation.popup-container");
    $(".data-citation.button").on('click', function() {
        popupContainer.toggleClass("disabled");
        $("body").addClass("overlaid");

    });

    $(".data-citation.overlay").on('click', function() {
        popupContainer.toggleClass("disabled");
        $("body").removeClass("overlaid");
    });

    $(".data-citation.pull-right.close-button").on('click', function() {
        popupContainer.toggleClass("disabled");
        $("body").removeClass("overlaid");
    });

});




