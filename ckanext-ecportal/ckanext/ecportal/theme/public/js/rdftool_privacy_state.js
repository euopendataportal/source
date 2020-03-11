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

$('body').click(function () {
    if (typeof unblockUI != 'undefined' && $.isFunction(unblockUI)) {
        $.unblockUI();
    }
});

$("#save-privacy-state").on("click", function () {

    var fd = new FormData();
    var selected = $("input[name='privacy-state']:checked").val()
    if(selected == undefined){
        $.blockUI({message:"Select a value !"})
        return false
    }
    fd.append('privacy-state', selected)
    fd.append('selected_datasets', $("#datasets_ids").val());
    fd.append('action', "save");
    $.ajax({
        url: $(this).attr('action'),
        data: fd,
        processData: false,
        contentType: false,
        type: 'POST',
        success: function (data) {
            if (typeof data != 'string')
                data = JSON.stringify(data);

            try {
                data = JSON.parse(data);
                if (data.response_type == 'url') {
                    window.location.href = data.body;
                }
            } catch (e) {
            }
        }
        ,
        error: function (data) {
            if($.inArray(data.status, [404,500]) == 0){
                $.blockUI({message: data.statusText});
            } else {
                $.blockUI({message: data.responseText});
            }
        }
    })
});

$('#cancel-privacy-state').on('click', function () {

    var fd = new FormData();
    fd.append('selected_datasets', $("#datasets_ids").val());
    fd.append('action', "cancel");
    $.ajax({
        url: $(this).attr('action'),
        data: fd,
        processData: false,
        contentType: false,
        type: 'POST',
        success: function (data) {
            if (typeof data != 'string')
                data = JSON.stringify(data);

            try {
                data = JSON.parse(data);
                if (data.response_type == 'url') {
                    window.location.href = data.body;
                }
            } catch (e) {
            }
        },
        error: function (data) {
            $.blockUI({message: data.responseText});
        }
    })
});