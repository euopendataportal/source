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

/* used in:
 /dashboard/datasets

 */
$(function () {

    var selected_datasets = Cookies.getJSON('selected_datasets');
    if (selected_datasets) {
        $(".regular-checkbox").each(function () {
            var link = $(this).closest("li").find("a:first");
            var href = link.attr("href");
            var id = href.substring(href.lastIndexOf("/") + 1);
            if ($.inArray(id, selected_datasets) != -1) {
                $(this).prop('checked', true);
            }
        });
        $('#dashboard_selected_count').text(selected_datasets.length);

    }


    var dialog = $("#dialog-form").dialog({
        autoOpen: false,
        height: 180,
        width: 260,
        modal: true,
        dialogClass: "ckan-content-wraper",
        closeOnEscape: false,
        buttons: [
            {
                "text": "Export",
                "priority": "primary",
                "class": 'btn btn-primary',
                "click": function () {
                    var ids = collect_selected_datasets();
                    $("#export_selected_datasets").val(ids);
                    $("#form-export").submit();
                    dialog.dialog("close");
                }
            },
            {
                "text": "Cancel",
                "priority": "primary",
                "class": 'btn btn-primary',
                "click": function () {
                    dialog.dialog("close");
                }
            }
        ], open: function (event, ui) {
            $(".ui-dialog-titlebar-close", ui.dialog | ui).hide();
        }
    });


    //Remove jQuery UI class on buttons

    //Delete datasets
    $("#delete-datasets").on("click", function (event) {
        event.preventDefault();
        check_dataset_selected()
        var ids = collect_selected_datasets();
        $("#delete-selected-datasets").val(ids);
        $("#form-delete").submit();
    });

    //Export datasets
    $("#export-datasets").on("click", function () {
        check_dataset_selected();
        dialog.dialog("open");
    });

    //Change Privacy State
    $("#change-privacy-state").on("click", function () {
        check_dataset_selected();
        var ids = collect_selected_datasets();
        $("#privacy-state-selected-datasets").val(ids);
        $("#form-privacy-state").submit();
    });

    $("#create-ingestion").on("click", function (event) {
        event.preventDefault();
        var ids = collect_selected_datasets();
        if (ids.length > 0) {

            //$("#incliude_selected_datasets").val(ids);
            //$("#form-create-ingestion-package").submit();
            var fd = new FormData();
            fd.append('ids', ids);
            $.ajax({
                url: $(this).attr('action'),
                data: fd,
                processData: false,
                contentType: false,
                type: 'POST',
                success: function (data) {
                    var obj = jQuery.parseJSON(data);
                    $('#dynamictable').children().remove();
                    $('#dynamictable').append('<table class="dynamic_table"></table>');
                    var index = 0;
                    var table = $('#dynamictable').children();
                    table.append('<tr><th id="title">Title</th><th id="name">Name</th><th id="url">URI</th><th id="publisher">Published by</th><th id="state">Status</th></tr>');
                    obj.forEach(function (entry) {
                        table.append('<tr><td headers="title"><input type="text"  name="dataset__' + index + '__title" value="' + entry.title + '" readonly /></td>' +
                            '<td headers="name"><input type="text"  name="dataset__' + index + '__name" value="' + entry.name + '" readonly />' +
                            '<td headers="uri"><input type="text"  name="dataset__' + index + '__url" value="' + entry.url + '" readonly />' +
                            '<td headers="publisher"><input type="text"  name="dataset__' + index + '__publisher" value="' + entry.publisher + '" readonly />' +
                            '<td headers="state"><input type="text"  name="dataset__' + index + '__state" value="' + entry.state + '" readonly />' +
                            '</tr>');
                        index += 1;
                    });
                    $('#create-ingestion-dialog').dialog({
                        //autoOpen: false,
                        height: 400,
                        width: 1150,
                        modal: true,
                        dialogClass: "ckan-content-wraper",
                        buttons: [{
                            "text": "Cancel",
                            "priority": "primary",
                            "class": 'btn btn-primary',
                            "click": function () {
                                $('#create-ingestion-dialog').dialog("close");
                            }
                        }],
                        close: function () {
                            //$('#form-create-ingestion-package').reset();
                            $('.ui-state-error').removeClass("ui-state-error");
                            // allFields.removeClass("ui-state-error");
                            $('#form-create-ingestion-package').hide();

                        }
                    });
                    $('#form-create-ingestion-package').show();
                },
                error: function (data) {
                    $.alert({theme: 'bootstrap',
                        type: 'orange',
                        title: 'Forbidden',
                        content: data.responseText,
                    container: 'body'});
                }
            })

        } else {
            window.alert("No dataset selected");
        }
    });

    //Edit of a single dataset OR bulk edit of multiple ones
    $("#edit-dataset").on("click", function (event) {
        event.preventDefault();
        check_dataset_selected()

        var ids = collect_selected_datasets();
        if (ids.length == 1) {
            window.location.href = get_edit_path_for_selected_dataset()
        } else {
            //bulk edit
            form = $("<form></form>");
            form.attr("action", $("#edit-dataset").data('bulk_action'));
            form.attr("method", "post");
            var new_input = $('<input>').attr({
                type: 'hidden',
                name: "ids"
            });
            new_input.val(ids);
            new_input.appendTo(form);
            //FF will not submit a form without adding it to the dom
            $( "body" ).append(form);
            form.submit();

        }
    });

    //Assign datasets DOI
    $("#assign-doi-datasets").on("click", function (event) {
        event.preventDefault();
        check_dataset_selected();
        var ids = collect_selected_datasets();
        $("#assign-doi-selected-datasets").val(ids);
        $("#form-assign-doi").submit();
    });

    function collect_selected_datasets() {
        var ids = Cookies.getJSON('selected_datasets');
       if (!ids) {
           ids = [];
       }
        return ids;
    }

    export_message_display();


    $("#format").on('change', function () {
        export_message_display();
    });


    $("#incliude_selected_datasets").on("click", function (event) {
        var pageURL = $(location).attr("href");
        var new_hidden = $('<input>').attr({
            type: 'hidden',
            name: "current_url",
        })
        new_hidden.val(pageURL);
        new_hidden.appendTo($('#form-create-ingestion-package'));
        $('#create-ingestion-dialog').dialog("close");
    });


    function get_edit_path_for_selected_dataset() {
        return $(".regular-checkbox:checked").attr('data-path-to-edit')
    }

    function check_dataset_selected() {
        var selected = Cookies.getJSON('selected_datasets');
        if (!selected) {
            window.alert("No dataset selected");
            throw new Error('No dataset selected');
        }
    }

    function export_message_display() {
        if ($("#format").val() == 'rdf') {
            $("#format_message").hide();
        } else {
            $("#format_message").show();
        }
    }

    $(".regular-checkbox").on("change", function (event) {
        var link = $(this).closest("li").find("a:first");
        var href = link.attr("href");
        var id = href.substring(href.lastIndexOf("/") + 1);
        var element = $(this);
        var change = false;
        var selected_datasets = Cookies.getJSON('selected_datasets');
        if (!selected_datasets) {
            selected_datasets = [];
        } else if (selected_datasets.length == 20) {
            $('#modal-trigger').click();
            // var message = $('#dashboard_selected').data('limit');
             element.prop('checked', false);
            // $('<div id="dialog-confirm" ><p><span class="ui-icon ui-icon-alert" style="float:left; margin:12px 12px 20px 0;"></span>' + message + '</p> </div>').dialog({
            //     resizable: false,
            //     height: "auto",
            //     width: 400,
            //     modal: true,
            //     buttons: {
            //         OK: function () {
            //             $(this).dialog("close");
            //         }
            //     }
            // });
        }
        if ($(this).is(":checked")) {
            selected_datasets.push(id);
            Cookies.set('selected_datasets', selected_datasets);
            change = true
        } else {
            var selected_datasets = $.grep(selected_datasets, function (value) {
                return value != id;
            });
            Cookies.set('selected_datasets', selected_datasets);
        }
        $('#dashboard_selected_count').text(selected_datasets.length);

        /*
         var data = {
         id: id,
         change: change
         }


         var path = window.location.pathname.split('/dashboard');
         var url = path[0] + '/api/action/change_selected_datasets';

         $.ajax({
         url: url,
         type: 'post',
         dataType: 'json',
         success: function (data) {
         if (!$.isArray(data.result)) {
         $('#dashboard_selected_count').text(data.result);
         } else {
         element.prop('checked', false);
         $('<div id="dialog-confirm" ><p><span class="ui-icon ui-icon-alert" style="float:left; margin:12px 12px 20px 0;"></span>' + data.result[1] + '</p> </div>').dialog({
         resizable: false,
         height: "auto",
         width: 400,
         modal: true,
         buttons: {
         OK: function () {
         $(this).dialog("close");
         }
         }
         });
         }
         },
         data: JSON.stringify(data)
         });*/
    });

    $('.remove-selected').on('click', function (event) {
        Cookies.remove('selected_datasets');
        $('#dashboard_selected_count').text('0');
        $(".regular-checkbox:checked").each(function () {
            $(this).prop('checked', false);
        });
        /*        var path = window.location.pathname.split('/dashboard');
         var url = path[0] + '/api/action/unselect_all_dataset';
         $.ajax({
         url: url,
         type: 'post',
         dataType: 'json',
         success: function (data) {
         $('#dashboard_selected_count').text(data.result);
         $(".regular-checkbox:checked").each(function () {
         $(this).prop('checked', false);
         });
         },
         data: JSON.stringify({change: true})
         });*/

    });

        function sortby_dropdown() {
        $('select[name="sort"]').on('change', function () {
            $('input[name="sort"]').val($(this).val());
            $('.page-search form').trigger('submit');
        });
    }

    sortby_dropdown();

});