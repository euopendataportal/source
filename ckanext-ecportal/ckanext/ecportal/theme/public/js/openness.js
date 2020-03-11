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
 * Created by ecodp on 7/12/16.
 */
$('#openness-select-publisher').change(function () {
    var url = $(this).val();
    window.location.href = url;
});

$(document).ready(function () {
    $('.openness-table').DataTable();

    $('.simple-table').DataTable({
        paging: false,
        searching: false,
        ordering: false
    });

    var dst = $("#distribution");
    if (dst.length != 0) {
        var tableData = $('#distribution').data('table');
        var data = {
            labels: [
                "Zero",
                "One",
                "Two",
                "Three",
                "Four",
                "Five"
            ],
            datasets: [
                {
                    data: [tableData.zero, tableData.one, tableData.two, tableData.three, tableData.four, tableData.five],
                    backgroundColor: [
                        "#FF6384",
                        "#36A2EB",
                        "#FFCE56",
                        "#1C3048",
                        "#515e8a",
                        "#03AF30"
                    ],
                    hoverBackgroundColor: [
                        "#FF6384",
                        "#36A2EB",
                        "#FFCE56",
                        "#1C3048",
                        "#515e8a",
                        "#03AF30"
                    ]
                }]
        };

        var myPieChart = new Chart(dst, {
            type: 'pie',
            data: data,
            options: {
                title: {
                    display: true,
                    text: 'Distribution of data sets in ODP'
                },
                responsive: false,
                legend: {
                    display: true,
                    labels: {
                        fontSize: 12
                    }
                }
            }
        });

        var bar = $("#common_datasets");
        var formats = $('#common_datasets').data('table');
        var bar_labels = [];
        var bar_raw_data = [];
        $.each(formats, function (key, element) {
            bar_labels.push(key);
            bar_raw_data.push(element);
        });

        var bar_data = {
            labels: bar_labels,
            datasets: [
                {
                    label: "Number of occurrence",
                    backgroundColor: "rgba(255,99,132,0.2)",
                    borderColor: "rgba(255,99,132,1)",
                    borderWidth: 1,
                    hoverBackgroundColor: "rgba(255,99,132,0.4)",
                    hoverBorderColor: "rgba(255,99,132,1)",
                    data: bar_raw_data,
                }
            ]
        }
        var myBarChart = new Chart(bar, {
            type: 'bar',
            data: bar_data,
            options: {
                title: {
                    display: true,
                    text: 'Most common data set'
                },
                responsive: true,
                legend: {
                    display: true,
                    labels: {
                        fontSize: 10
                    }
                }
            }
        });
        $('#openness-totals-table_info').hide();
    }else {
        $('#publisher-totals-table_info').hide();
    }


/*    $('#global_report_json').on('click', function () {
        var new_hidden = $('<input>').attr({
            type: 'hidden',
            name: "json",
        })
        new_hidden.val("json_js");
        new_hidden.appendTo($('#global_report_form'));
    })

       $('#global_report_csv').on('click', function () {
        var new_hidden = $('<input>').attr({
            type: 'hidden',
            name: "csv",
        })
        new_hidden.val("csv_js");
        new_hidden.appendTo($('#global_report_form'));
    })

       $('#publisher_report_csv').on('click', function () {

    })

       $('#publisher_report_csv').on('click', function () {

    })*/

});