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

list_next_level_members = {"http://www.w3.org/ns/dcat#Distribution":['rights_dcterms',
                                                                 'checksum_spdx',
                                                                 'extensionValue_dcatapop',
                                                                 'extensionLiteral_dcatapop',
                                                                 'page_foaf',
                                                                 'rights_dcterms'
                                                                 ],
                           "http://www.w3.org/ns/dcat#Dataset" : [
                                                                'provenance_dcterms',
                                                                'temporal_dcterms',
                                                                'distribution_dcat',
                                                                'page_foaf',
                                                                'extensionValue_dcatapop',
                                                                'extensionLiteral_dcatapop',
                                                                'contributor_dcterms',
                                                                'type_dcterms',
                                                                'sample_adms',
                                                                'accessRights_dcterms',
                                                                'contactPoint_dcat',
                                                                'landingPage_dcat',
                                                                'identifier_adms'
                                                            ],

                           "http://www.w3.org/2006/vcard/ns#Kind": [
                                                                'hasTelephone_vcard',
                                                                'hasAddress_vcard',
                                                                'homePage_foaf',
                                                                'hasEmail_vcard'
                                                           ],

                           "http://xmlns.com/foaf/0.1/Document": [
                                                                'extensionValue_dcatapop',
                                                                'extensionLiteral_dcatapop'
                           ],
                           "http://www.w3.org/ns/dcat#Catalog":[
                                                                'rights_dcterms',
                                                                'identifier_adms'
                           ]
                           }

