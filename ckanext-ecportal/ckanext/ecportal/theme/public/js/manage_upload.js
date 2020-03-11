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

    showEmptyUploadForm();

    $("#dataset-upload").on('change', function () {
        var filename = $('#dataset-upload').val().replace(/C:\\fakepath\\/i, '');
        var timestamp = new Date().toISOString().replace(/\:/g, '').slice(0, -5);
        var file_id = timestamp + "/" + filename;
        var fd = new FormData();
        fd.append('file', $('#dataset-upload')[0].files[0]);
        fd.append('key', file_id);
        $.ajax({
            url: $('#dataset-upload-action').val(),
            data: fd,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function (data) {
                data = decode(data);
                $('#uploaded-file-link').val(data);
                $('#dataset-upload').val(null);
                $('#dataset-fileinfo').text(file_id);
                $("#zip-datasets-upload").hide();
                $("#add-dataset-upload").show();
            }
        });
    });

    $("#add-dataset-upload").on("click", function () {
        var file_path = $('#uploaded-file-link').val().substring($('#uploaded-file-link').val().indexOf("/f/") + 3, $('#uploaded-file-link').val().length);
        var fd = new FormData();
        fd.append('file_path', file_path);
        $('#upload-file').hide();
        $("#add-dataset-upload").hide();
        $("#validate-dataset-upload").show();
        $.ajax({
            url: $('#add-dataset-upload').attr('action'),
            data: fd,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function (data) {
                var data_json = jQuery.parseJSON(data)
                if (data_json) {
                    if (data_json.response_type == 'table') {
                        $("#container-table-import").html(data_json.response);

                        $("#upload-file-container").hide();
                        $("#import-dataset-table").tablesorter({headers: {5: {sorter: false}}});
                        $("#zip-datasets-upload").show();

                    } else {
                        displayErrorMessages(data_json, 'error')
                    }
                } else {
                    $('#upload-file').show();
                }
                $("#add-dataset-upload").show();

            },
            error: function (data) {
                onError(data);
                $("#add-dataset-upload").hide();
            },
            complete: function () {
                $('#dataset-fileinfo').text('');
            }
        });
    });

    $("#package-upload").on('change', function () {
        var filename = $('#package-upload').val().replace(/C:\\fakepath\\/i, '');
        var file_id = filename;
        var fd = new FormData();
        fd.append('file', $('#package-upload')[0].files[0]);
        fd.append('key', file_id);
        fd.append('upload', 'upload');
        $.ajax({
            url: $('#package-upload-action').val(),
            data: fd,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function (data) {
                $('#uploaded-file-link').val(file_id);
                $('#package-upload').hide();
                $('#ingestion-upload').css('visibility', 'visible');
                $('#package-upload').val(null);
                $('#dataset-fileinfo').text(file_id);
            }
        });
    });

    $("#validate-dataset-upload").on("click", function () {
        var file_path = $('#uploaded-file-link').val().substring($('#uploaded-file-link').val().indexOf("/f/") + 3, $('#uploaded-file-link').val().length);
        var fd = new FormData();
        fd.append('file_path', file_path);
        var checkboxChecked = [];
        $(".checkbox_datasets:checked").each(function () {
            checkboxChecked.push($(this).val());
        });

        var selected = checkboxChecked.length > 0
        if (!selected) {
            window.alert("No dataset selected");
            throw new Error('No dataset selected');
        }


        fd.append('selected_datasets', checkboxChecked);
        $("#validate-dataset-upload").hide();
        $("#cancel-dataset-upload").hide();
        $.ajax({
            url: $(this).attr('action'),
            data: fd,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function (data) {
                var data_json = jQuery.parseJSON(data)
                if (data_json) {
                    if (data_json.response_error != null) {
                        displayErrorMessagesMultiple(data_json, 'error')
                    } else {
                        window.location.href = data_json.response;
                    }
                }

            },
            error: function (data) {
                onError(data);

                $("#cancel-dataset-upload").show();
            }
        })
    });


    $('#cancel-dataset-upload').on('click', function () {
        showEmptyUploadForm();
    });


    function onError(data) {
        var json_fake_dict = {};
        json_fake_dict.response_error = {};
        json_fake_dict.response_error['fatal'] = {};

        var removedHtml = $("<div/>").html(data.responseText).text();
        var errorToInsert = $($.parseHTML($($("<div/>").html(data.responseText)).text())).filter('span')[0];

        var array = [errorToInsert.innerHTML];
        json_fake_dict.response_error['fatal'].fatal = array;

        displayErrorMessages(json_fake_dict, 'fatal');
        showEmptyUploadForm();

    }


    function showEmptyUploadForm() {
        $("#zip-datasets-upload").hide();
        $("#zip-datasets-upload table tbody").html('');
        $("#upload-file-container").show();
        $("#upload-file").show();
        $("#add-dataset-upload").hide();
        $('#dataset-fileinfo').text('');
    }


    function displayErrorMessages(data_json, errorType) {
        var errors = data_json.response_error[errorType];
        if (errors != null && Object.keys(errors).length > 0) {
            $("#dialog-form-error").data('response', data_json.response);
            $("#dialog-form-error").data('errorType', errorType);
            var errorText = "";
            for (var k in errors) {
                if (errors.hasOwnProperty(k)) {
                    for (var i = 0; i < errors[k].length; i++) {
                        errorText += "<br/>";
                        if(typeof errors[k][i] === 'object'){
                            if(errors[k][i].name){
                                errorText += errors[k][i].name;
                            }else{
                                errorText += errors[k][i].title;
                            }
                        }else{
                            errorText += errors[k][i];
                        }
                    }
                }

            }

            if(!errorText) {
                errorText = 'Unknown error';
            }

            var dialogContent = $("#dialog-error-content");
            dialogContent.html(errorText);

            errorDialog.dialog("open");
        } else {
            window.location.href = data_json.response;
        }
    }


    function displayErrorMessagesMultiple(data_json, errorType) {
        var errors = data_json.response_error;
        if (errors != null && Object.keys(errors).length > 0) {
            $("#dialog-form-error").data('response', data_json.response);
            $("#dialog-form-error").data('errorType', errorType);
            var errorText = "";
            for (var k in errors.errors) {
                if (errors.errors.hasOwnProperty(k)) {
                    errorText += "<br/>";
                    errorText += k + ":";

                    var errorTyped = errors.errors[k][errorType]
                    for (var l in errorTyped) {
                        for (var i = 0; i < errorTyped[l].length; i++) {
                            errorText += "<br/>";
                            if(typeof errorTyped[l][i] === 'object' && errorTyped[l] && errorTyped[l][i]){
                                if(errorTyped[l][i].name){
                                    errorText += errorTyped[l][i].name;
                                }else{
                                    errorText += errorTyped[l][i].title;
                                }
                            }else if (errorTyped[l]){
                                errorText += errorTyped[l][i];
                            }
                        }
                    }
                }

            }

            if(!errorText) {
                errorText = 'Unknown error';
            }

            var dialogContent = $("#dialog-error-content");
            dialogContent.html(errorText);

            errorDialog.dialog("open");
        } else {
            window.location.href = data_json.response;
        }
    }


    var errorDialog = $("#dialog-form-error").dialog({
        autoOpen: false,
        height: 'auto',
        width: 'auto',
        modal: true,
        closeOnEscape: false,
        buttons: [
            {
                "text": "OK",
                "priority": "primary",
                "class": 'btn btn-primary btn-dataset-action',
                "click": function () {
                    if ($("#dialog-form-error").data('errorType') == 'error') {
                        window.location.href = $("#dialog-form-error").data('response');
                    }
                    errorDialog.dialog("close");
                }
            }
        ], open: function (event, ui) {
            $(".ui-dialog-titlebar-close", ui.dialog | ui).hide();
        }
    });

});

function decode(text) {
    var encoded = text;
    return decodeURIComponent(encoded.replace(/\+/g, " "));
}