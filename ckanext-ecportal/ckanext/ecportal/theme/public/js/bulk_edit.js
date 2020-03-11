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
 * Created by ecodp on 7/29/16.
 */
$('select, input').not(".regular-checkbox").change(function () {
    var parent = $(this).closest(".controls");
    var check_box = parent.find('.regular-checkbox');
    var number = 100 + Math.floor(Math.random() * 100);
    if (check_box.length == 0) {
        //clone
        check_box = $('.clonable_checkbox').first().clone();
        check_box.find('.regular-checkbox').prop("id", 'checkbox-bulk_' + number);
        check_box.find('label').prop("for", 'checkbox-bulk_' + number);
        check_box.find('.regular-checkbox').prop("checked", true);
        check_box.insertAfter(parent.find('.searchHelp-green'));
    } else {
        check_box.prop("checked", true);
    }
});

$('textarea').change(function () {
    var parent = $(this).closest(".controls");
    var check_box = parent.find('.regular-checkbox');
    var number = 1 + Math.floor(Math.random() * 100);
    if (check_box.length == 0) {
        //clone
        check_box = $('.clonable_checkbox').first().clone();
        check_box.find('.regular-checkbox').prop("id", 'checkbox-bulk_' + number);
        check_box.find('label').prop("for", 'checkbox-bulk_' + number);
        check_box.find('.regular-checkbox').prop("checked", true);
        check_box.insertAfter(parent.find('.searchHelp-green'));
    } else {
        check_box.prop("checked", true);
    }
});

$('#bulk_validate').on('click', function (event) {
    remove_unchecked_input_fields();
    var new_hidden = $('<input>').attr({
        type: 'hidden',
        name: "validate",
    })
    new_hidden.val("Validate Changes");
    new_hidden.appendTo($('#dataset-edit'));
});

$('#bulk_save_published').on('click', function (event) {
    remove_unchecked_input_fields();
    $('#field-private-false').prop("checked", true);
    var new_hidden = $('<input>').attr({
        type: 'hidden',
        name: "save",
    })
    new_hidden.val("Save Changes");
    new_hidden.appendTo($('#dataset-edit'));
});

$('#bulk_save_draft').on('click', function (event) {
    remove_unchecked_input_fields();
    $('#field-private-true').prop("checked", true);
    var new_hidden = $('<input>').attr({
        type: 'hidden',
        name: "save",
    })
    new_hidden.val("Save Changes");
    new_hidden.appendTo($('#dataset-edit'));
});

$('#bulk_cancel').on('click', function (event) {
    var url = $(this).attr('action');
    window.location.href = url;
});

function remove_unchecked_input_fields() {
    $(".regular-checkbox:not(:checked)").each(function () {
        //var unchecked_field = $(this).closest(".controls").find('select, textarea, input:not(".regular-checkbox")');
        var unchecked_field = $(this).closest(".controls");
        unchecked_field.remove();
    });
}