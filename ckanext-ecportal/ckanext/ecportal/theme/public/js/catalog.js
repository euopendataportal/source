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
        $(".chzn-select2").select2({width: '94%', placeholder: "Select Some Options"});

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


        $("#release_date").datepicker({
            dateFormat: 'yy-mm-dd'
        });
        $("#modified_date").datepicker({
            dateFormat: 'yy-mm-dd'
        });


        $("#catalog_select-28-countries").on('click', function () {
         var selectedCountries = $("#catalog_geographical_coverage").val() || [];
        for (var i in europeanCountries) {
            if (!~$.inArray(europeanCountries[i], selectedCountries)) {
                selectedCountries.push(europeanCountries[i]);
            }
        }


        $("#catalog_geographical_coverage").val(selectedCountries);
        $("#catalog_geographical_coverage").trigger('change');
    });

    $("#catalog_select-27-countries").on('click', function () {
        var selectedCountries = $("#catalog_geographical_coverage").val() || [];
        var croatia = 'http://publications.europa.eu/resource/authority/country/HRV';
        // european countries - croatia
        var european = europeanCountries.slice();
        european.splice(european.indexOf(croatia), 1);
        for (var i in european) {
            if (!~$.inArray(european[i], selectedCountries)) {
                selectedCountries.push(european[i]);
            }
        }

        $("#catalog_geographical_coverage").val(selectedCountries);
        $("#catalog_geographical_coverage").trigger("change");
    });

    $("#catalog_clear-geographical-coverage").on('click', function () {
        $("#catalog_geographical_coverage").val([]);
        $("#catalog_geographical_coverage").trigger("change");
    });


    $(".assign-doi-line-button").on('click', function(e){
        var action = $(this).data("action");
        var publisher = $("#owner_org").val();
        var uri = $(this).data("uri") || undefined;
        if(action && publisher){
            $.post($(this).data("action"), {"publisher" : publisher, "uri": uri} ,function(data){
                $("#doi").val(data);
                $(".assign-doi-line-button").data("action", null).removeAttr('data-action').prop("disabled", true);
            });
        }

    });

});