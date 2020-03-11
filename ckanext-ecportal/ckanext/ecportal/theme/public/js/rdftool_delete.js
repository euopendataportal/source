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
    $('body').click(function () {
        $.unblockUI();
    });

    $("#confirm-delete").on("click", function () {

        var fd = new FormData();
        fd.append('selected_datasets', $("#datasets_ids").val());
        fd.append('action', "delete");
        $.ajax({
            url: $(this).attr('action'),
            data: fd,
            processData: false,
            contentType: false,
            type: 'POST',
            success: function (data) {
                if (typeof data != 'string')
                    data = JSON.stringify(data);
                //delete the cookie for the selected datasets
                Cookies.remove('selected_datasets');

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

    $('#cancel-delete').on('click', function () {

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

    $("#delete-dataset-table").tablesorter({headers: {5: {sorter: false}}});
});