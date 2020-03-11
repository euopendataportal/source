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

/**
 * Created by ecodp on 5/25/16.
 */
$(function () {
    //$('div.ecodp_tabs').tabs().addClass('ui-tabs-vertical ui-helper-clearfix');
    //$(".submenu:visible").slideUp();

    $(".image-calendar").datepicker({
        dateFormat: 'yy-mm-dd'
    });

    $('div.div_toggle').hide();
    $('#main_tabs').collapsible({accordion: true, contentOpen: 0});

    //Tabs for Resources
    $(".resource-tab").tabs();



    $("a.toggelable").on("click", function (e) {
        var ref = $(this).attr('href');
        $('div.div_toggle').hide();
        $(ref).show();
    });

    $("ul.topnav").on("click", "li", function (e) {
        e.stopPropagation();
        $(".submenu:visible", $(this).siblings()).slideUp("fast");
        $(".submenu", this).slideDown();

    });

    function add_translations_inputs_and_values(new_lang, id, classes, placeholder, data_module, isTextarea, value) {

        add_translations_inputs(new_lang, id, classes, placeholder, data_module, isTextarea);

        $("#" + id + "-" + new_lang).val(value);
        $("#" + id + "-" + new_lang).hide();
    }

    $('#action-selector').on('change', function (event) {
        var selected = $(this).val();
        if ('manage_file_upload' == selected) {
            $('#manage_file_upload').show();
        } else if ('default' != selected) {
            $('#' + selected).click();
        }
    });


    $('#add-resource-upload').on('click', function (event) {
        var new_hidden = $('<input>').attr({
            type: 'hidden',
            name: "upload",
        })
        new_hidden.val("Upload");
        new_hidden.appendTo($('#ingestion-package-edit'));
    });

    $('#ingestion_add_rdf').on('click', function (event) {
        var new_hidden = $('<input>').attr({
            type: 'hidden',
            name: "add_rdf",
        })
        new_hidden.val("Add RDF");
        new_hidden.appendTo($('#ingestion-package-edit'));
    });

    $('#ingestion_add_delete').on('click', function (event) {
        var new_hidden = $('<input>').attr({
            type: 'hidden',
            name: "add_delete",
        })
        new_hidden.val("Add Delete");
        new_hidden.appendTo($('#ingestion-package-edit'));
    });

    $('#ingestion_add_file').on('click', function (event) {

        var new_hidden = $('<input>').attr({
            type: 'hidden',
            name: "validate",
        })
        new_hidden.val("Validate Changes");
        new_hidden.appendTo($('#ingestion-package-edit'));
    });

    $('#ingestion_validate').on('click', function (event) {
        var new_hidden = $('<input>').attr({
            type: 'hidden',
            name: "validate",
        })
        new_hidden.val("Validate Changes");
        // new_hidden.appendTo($('#ingestion-package-edit'));
    });

    $('#save_package').on('click', function (event) {
        $('#field-private-false').prop("checked", true);
        var new_hidden = $('<input>').attr({
            type: 'hidden',
            name: "save",
        })
        new_hidden.val("Save Changes");
        new_hidden.appendTo($('#ingestion-package-edit'));
    });

    $('#save_locally').on('click', function (event) {
        $('#field-private-true').prop("checked", true);
        var new_hidden = $('<input>').attr({
            type: 'hidden',
            name: "save_locally",
        })
        new_hidden.val("Save locally");
        //new_hidden.appendTo($('#ingestion-package-edit'));
    });

    $('#start').on('click', function (event) {
        $('#field-private-true').prop("checked", true);
        var new_hidden = $('<input>').attr({
            type: 'hidden',
            name: "start",
        })
        new_hidden.val("Start");
        new_hidden.appendTo($('#ingestion-package-edit'));
    });

});




