#    Copyright (C) <2018>  <Publications Office of the European Union>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
#    contact: <https://publications.europa.eu/en/web/about-us/contact>

import re
import glob
import json

def create_validation_structure_for_file(source_file_path):
    '''
    Created the list of structural rules based on the datatype in the code. 
    
    :param source_file_path: 
    :return: 
    '''
    validation_structural_rules = {}
    with open(source_file_path) as f:

        content = f.readlines()
        for line in content:
            member_name =""
            is_structural_definition = re.search("# *type", line)
            if is_structural_definition:
                serach_object = re.search( r'self.(.*?)[\ =]', line)
                if serach_object:
                    member_name = serach_object.group(1)
                    member_name.replace(" ","")
                    type_resource = {'type':'uri','class':''}
                    if 'ResourceValue' in line:
                        type_resource = {'type':'literal','class':''}
                    validation_structural_rules[member_name] = type_resource
    return validation_structural_rules

list_source_files = glob.glob('../schemas/dcatapop*_schema.py')
global_validation_structural_rules ={}
for source_file_path in list_source_files:
    validation_structural_rules = create_validation_structure_for_file(source_file_path)
    if validation_structural_rules:
        global_validation_structural_rules.update(validation_structural_rules)

validation_structural_rules_file = "validation_structure.json"
f = open (validation_structural_rules_file,'w+')
json.dump(global_validation_structural_rules,f)

pass

