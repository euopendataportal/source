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

$(function(){
    var default_lang = 'en';
    var widgetInput = 'input';
    var widgetTextarea = 'textarea';
    var widgetSelect = 'select';
    $(".ingestion_package_tabs").tabs();
	// Click on the "X" button in the resource details panel
	$('.resource-panel-close').on('click',function(event) {
		event.preventDefault();
		$('.resource-panel').hide();
		$("#box-main-info").hide();
	});



	// Click on the "Choose file" button for "Upload a file"
	$(document).on('change','.file-upload', function(event){
		var filename = $(this).val().replace(/C:\\fakepath\\/i, '');
		var timestamp = new Date().toISOString().replace(/\:/g,'').slice(0, -5);
		var file_id =  timestamp+"/"+ filename;
		$(this).parent().find('.fileinfo').text(file_id);
	});


	// Click on the Upload button for "Upload a file"
	// see in form_resources.html and storage.upload_handle
	$(document).on('click', '.upload',function(event){
		var $t = $(this);
		var fd = new FormData();
		var new_resource_details = $t.closest(".resource-details");
		var res_number = new_resource_details.attr('data-resnumber');
		fd.append('file', $('#file-'+res_number)[0].files[0]);
		fd.append('key', $('div.fileinfo').text());
		$.ajax({
		  url: $t.attr('action'),
		  data: fd,
		  processData: false,
		  contentType: false,
		  type: 'POST',
		  success: function(data){
			url = data;
			var new_resource_details = $t.parent().closest(".resource-details");
			var res_number = new_resource_details.attr('data-resnumber');
			$('#file-'+res_number).val('');
			$('#file-'+res_number).find('.fileinfo').text('');
			new_resource_details.find("[name='resources__"+res_number+"__url']").val(url);
		  }
		});

	});

	$('#validate').on('click',function(event){
		var new_hidden = $('<input>').attr({
			type: 'hidden',
			name: "validate",
		})
		new_hidden.val("Validate Changes");
		new_hidden.appendTo($('#dataset-edit'));
	});

	$('#save_published').on('click',function(event){
		$('#field-private-false').prop("checked", true);
		var new_hidden = $('<input>').attr({
			type: 'hidden',
			name: "save",
		})
		new_hidden.val("Save Changes");
		new_hidden.appendTo($('#dataset-edit'));
	});

	$('#save_draft').on('click',function(event){
		$('#field-private-true').prop("checked", true);
		var new_hidden = $('<input>').attr({
			type: 'hidden',
			name: "save",
		})
		new_hidden.val("Save Changes");
		new_hidden.appendTo($('#dataset-edit'));
	});

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
					name: "resources__"+res_number+"__"+key
				});
				new_hidden.val(value);
				new_hidden.appendTo($('#dataset-edit'));
				$('#file-'+res_number).remove();
				$('.upload').remove();
			}
		});
		$('.templates').each(function(){
			$(this).remove();
		});


		return true;
	});



	//Languages list interaction
    $("a[class*='dataset-lang']").on("click", function () {
		var index = $(this).closest(".div_toggle").data("index");
        var new_lang = this.text;

        //Hide input field of the prev lang
        $(this).closest(".div_toggle").find(".js-title").hide();
        $(this).closest(".div_toggle").find(".js-alt-title").hide();
        $(this).closest(".div_toggle").find(".js-description").hide();

        //Display or create input for new lang
        add_translations_inputs(new_lang, "dataset_"+index+"-title", "dataset__"+index+"__title", "js-title translatable-field", "A short descriptive title for the dataset", "custom_slug-preview-target", widgetInput);
        add_translations_inputs(new_lang, "dataset_"+index+"-alternative_title", "dataset__"+index+"__alternative_title", "js-alt-title translatable-field", "", "", widgetInput);
        add_translations_inputs(new_lang, "dataset_"+index+"-description", "dataset__"+index+"__description", "js-description markdown-input translatable-field", "The main description of the dataset ...", "", widgetTextarea);


        $("#dataset_"+index+"-dataset-languages .fake-text").toggleClass("fake-text");
        $(this).toggleClass("fake-text");
    });

	$("div[id^='tabs-']").each(function(){
        var index = $(this).closest(".div_toggle").data("index");
        add_translations_inputs(default_lang, "dataset_"+index+"__title", "js-title", "A short descriptive title for the dataset", "custom_slug-preview-target", widgetInput);
    	$("#dataset_"+index+"-dataset-lang-" + default_lang).toggleClass("fake-text");

        $(".dataset_"+index+"-resource-lang").each(function(){
            if($(this).text() == default_lang){
                $(this).toggleClass("fake-text");
            }
        });


    });

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


	$(document).on('click', "a[class*='resource-lang']", function () {
		var index = $(this).closest(".div_toggle").data("index");
        var type = $(this).closest(".resource-tab").data("type");
        var new_lang = this.text;

        // Hide/show the mandatory star for Title and Description labels
        if (new_lang == default_lang) {
            $(this).closest(".resource-details_"+type).find(".field_required").show();
        } else {
            $(this).closest(".resource-details_"+type).find(".field_required").hide();
        }

        var resNumber = $(this).closest(".resource-details_"+type).data("resnumber");
        $("#dataset_"+index+"-resource_details_" + type + "_" + resNumber + " .js-resource-edit-title-field").hide();
        $("#dataset_"+index+"-resource_details_" + type + "_" + resNumber + " .js-resource-edit-description").hide();
        //$("#resource_details_" + resNumber + " .js-resource-edit-format").hide();
        //$("#resource_details_" + resNumber + " .js-resource-edit-mimetype").hide();

        add_translations_inputs(new_lang, "dataset_"+index+"-resources_"+type+"__" + resNumber + "__title", "dataset_"+index+"-resources_"+type+"__" + resNumber + "__title", "js-resource-edit-title-field translatable-resource-field", "", "", widgetInput);
        add_translations_inputs(new_lang, "dataset_"+index+"-resources_"+type+"__" + resNumber + "__description", "dataset_"+index+"-resources_"+type+"__" + resNumber + "__description", "js-resource-edit-description markdown-input translatable-resource-field", "", "", widgetTextarea);

        $(this).closest("#dataset_"+index+"-resource-languages").find(".fake-text").toggleClass("fake-text");
        $(this).toggleClass("fake-text");
    });

	$(document).on("change", ".translatable-field", function(){
        show_up_translations($(this), false);
    });

    $(document).on("change", ".translatable-resource-field", function(){
        show_up_translations($(this), true);
    });


    function show_up_translations(elem, isResource){
        var type = elem.closest(".resource-tab").data("type");
		var index = elem.closest(".div_toggle").data("index");
        if(isResource){
            var selector = elem.closest(".resource-details_"+type);
            var translatable = ".translatable-resource-field";
            var langList = selector.find(".dataset_"+index+"-resource-lang");
        }else{
            var selector = elem.closest(".div_toggle");
            var translatable = ".translatable-field";
            var langList = selector.find(".dataset_"+index+"-dataset-lang");
        }

        var langTab = elem.attr('id').split('-');

        var lang = langTab[2];

        if(langTab.length == 4){
            lang = langTab[3];
        }else if(!lang || lang.length > 2){
            lang = default_lang; //Fallback
        }

        var oneFill = false;

        selector.find(translatable).each(function(){
           var languageTab = $(this).attr('id').split('-');
            if(languageTab.length == 3){
                if(languageTab[2] == lang || (languageTab[2].length>2 && lang == default_lang)){
                    if($(this).val()) oneFill = true
                }

            }else if(lang == default_lang && languageTab.length == 2){
                if($(this).val()){
                    oneFill = true
                }
            }else if(languageTab.length == 4){
                 if(languageTab[3] == lang || (languageTab[3].length>2 && lang == default_lang)){
                    if($(this).val()) oneFill = true
                }
            }
        });

        if(oneFill){
           langList.each(function(){
                if($(this).text() == lang){
                    $(this).css("font-weight", "bold");
                    $(this).css("text-transform", "uppercase");
                }
            });
        }else{
            langList.each(function(){
                if($(this).text() == lang) {
                    $(this).css("font-weight", "");
                    $(this).css("text-transform", "");
                }
            });

        }
    }

    function init_show_up_translation_edit(){
        $(".translatable-field").each(function(){
            show_up_translations($(this), false);
        });

        $(".translatable-resource-field").each(function(){
            show_up_translations($(this), true);
        });
    }

    init_show_up_translation_edit();


});