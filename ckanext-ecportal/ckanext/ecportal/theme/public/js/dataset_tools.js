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



function downloadResourceCount(url, rs_uri, ds_uri) {
    $.ajax({
	  url: url,
	  type: 'POST',
		data: {'rs_uri': rs_uri,
				'ds_uri':ds_uri}
	});
}

$('.download-resource-lang').on('change', function(event){
	var download_button = $(this).parent().find('a.button-box');
	window.open($(this).val(), '_blank');
	downloadResourceCount(download_button.data('dlc'));
});
