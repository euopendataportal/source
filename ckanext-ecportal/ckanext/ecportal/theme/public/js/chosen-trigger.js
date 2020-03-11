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

var config = {
	'.chzn-select': {width:'94%'},
	'.chzn-select-half': {width:'24.5em'},
	'.chosen-select-deselect'  : {width:'94%', allow_single_deselect:true},
	'.chosen-select-half' : {width: '26em', allow_single_deselect: true}
}
for (var selector in config) {
	$(selector).chosen(config[selector]);
}