# -*- coding: utf-8 -*-
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

from lxml import etree
import traceback
import logging

log = logging.getLogger(__file__)


class DCATAPOPToDataCiteMapper:

    def __init__(self, submission_doi_sender_email, submission_doi_from_company, submission_doi_to_company):
        self._submission_doi_sender_email = submission_doi_sender_email
        self._submission_doi_from_company = submission_doi_from_company
        self._submission_doi_to_company = submission_doi_to_company

    def generate_dataset_metadata(self, doi, dataset_doi_dict):
        """
        Generate metadata XML for a DCATAPOP dataset.
        :param str doi: - The DOI of the dataset.
        :param dict doit_dict: - The doi dict of the dataset
        :return str: the DataCite metadata XML.
        """
        try:
            doi_ressource_xml_str = self.generate_resource_node(doi, dataset_doi_dict)
            doi_identifier = doi
            doi_registration_message_dict = {
                "from_company": self._submission_doi_from_company,
                "from_mail": self._submission_doi_sender_email,
                "to_company": self._submission_doi_to_company,
                "sent_date": dataset_doi_dict.get('current_date'),
                "doi_website_link": dataset_doi_dict.get('url')
            }
            doi_ressource_node_xml = etree.fromstring(doi_ressource_xml_str)
            doi_final_xml_str = self.generate_final_doi_xml(doi_identifier, doi_registration_message_dict, doi_ressource_node_xml)

            return doi_final_xml_str
        except BaseException as e:
            # log.error("generate_dataset_metadata failed for *** \n{0} ".format(self(str(dataset_doi_dict))))
            log.error(traceback.print_exc(e))

    def generate_catalog_metadata(self, doi, catalog_dict):
        """
        Generate metadata XML for a DCATAPOP catalog.
        :param str doi: - The DOI of the catalog.
        :param dict catalog_dict: - The catalog DOI dict.
        :return the DataCite metadata XML.
        """
        try:
            doi_xml_str = self.generate_resource_node(doi, catalog_dict, False)

            return doi_xml_str
        except BaseException as e:
            log.error(traceback.print_exc(e))


    def generate_final_doi_xml(self, doi_identifier, doi_registration_message_dict, resource_node):
        '''
        Build the final xml of the doi by combining the resource node and the specific part of the document
        :param str doi_str:
        :param dict doi_registration_message_dict:
        :param resource_node etree
        :return str:
        '''

        doi_str = doi_identifier
        attr_qname = etree.QName("http://www.w3.org/2001/XMLSchema-instance", "schemaLocation")
        nsmap = {None: "http://ra.publications.europa.eu/schema/doidata/1.0", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

        doi_registration_message_xml = etree.Element("DOIRegistrationMessage",
                                                     {
                                                         attr_qname: "http://ra.publications.europa.eu/schema/doidata/1.0 http://ra.publications.europa.eu/schema/OP/DOIMetadata/1.0/OP_DOIMetadata_1.0.xsd"},
                                                     nsmap=nsmap
                                                     )

        # Build Header section
        header_xml = etree.Element("Header")
        from_company_xml = etree.Element("FromCompany")
        from_company_xml.text = doi_registration_message_dict.get("from_company")

        from_mail_xml = etree.Element("FromEmail")
        from_mail_xml.text = doi_registration_message_dict.get("from_mail")

        to_company_xml = etree.Element("ToCompany")
        to_company_xml.text = doi_registration_message_dict.get(("to_company"))

        sent_date_xml = etree.Element("SentDate")
        sent_date_xml.text = doi_registration_message_dict.get("sent_date")

        header_xml.append(from_company_xml)
        header_xml.append(from_mail_xml)
        header_xml.append(to_company_xml)
        header_xml.append(sent_date_xml)

        doi_registration_message_xml.append(header_xml)

        doi_data_xml = etree.Element("DOIData")
        doi_xml = etree.Element("DOI")
        doi_xml.text = doi_str
        doi_website_link_xml = etree.Element("DOIWebsiteLink")
        doi_website_link_xml.text = doi_registration_message_dict.get("doi_website_link")
        metadata_xml = etree.Element("Metadata")
        metadata_xml.append(resource_node)

        doi_data_xml.append(doi_xml)
        doi_data_xml.append(doi_website_link_xml)
        doi_data_xml.append(metadata_xml)
        doi_data_xml.append(metadata_xml)

        doi_registration_message_xml.append(doi_data_xml)

        final_doi_xml_str = etree.tostring(doi_registration_message_xml, pretty_print=True)
        return final_doi_xml_str

    def generate_resource_node(self, doi, doi_dict, is_dataset=True):
        """
        Generate metadata XML for a DCATAPOP dataset or the catalog.
        :param str doi: - The DOI of the dataset.
        :param dict doi_dict: - The doi dict of the dataset or the catalog
        :param boolean is_dataset - The doi dict of the dataset or the catalog
        :return str: the DataCite metadata XML.
        """

        try:

            if not isinstance(doi_dict, dict):
                raise Exception("The expected parameter doi_dict is not a valid dict")

            identifier = doi
            creatorName = doi_dict.get("creator")
            titles = doi_dict.get("title")
            publisher_name = doi_dict.get("publisher")
            publicationYear = doi_dict.get("publicationYear")
            resourceType = doi_dict.get("resourceType")

            # Build the Mandatory part
            doi_resource__node_xml = etree.Element("resource", xmlns="http://datacite.org/schema/kernel-4")

            identifier_xml = etree.Element("identifier", identifierType="DOI")
            identifier_xml.text = identifier

            creator_xml = etree.Element("creator")
            creator_name_xml = etree.Element("creatorName", nameType="Organizational")
            creator_name_xml.text = creatorName
            creator_xml.append(creator_name_xml)
            creators_xml = etree.Element("creators")
            creators_xml.append(creator_xml)
            doi_resource__node_xml.append(creators_xml)

            titles_xml = etree.Element("titles")
            for title in titles:  # type: dict
                title_xml = etree.Element("title")
                title_xml.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = title.get('lang', "en")
                title_xml.text = title.get("text")
                titles_xml.append(title_xml)

            publisher_xml = etree.Element("publisher")
            publisher_xml.text = publisher_name
            doi_resource__node_xml.append(publisher_xml)

            publisher_year_xml = etree.Element("publicationYear")
            publisher_year_xml.text = publicationYear

            doi_resource__node_xml.append(identifier_xml)
            doi_resource__node_xml.append(titles_xml)
            doi_resource__node_xml.append(publisher_year_xml)

            # Resource type
            # TODO resourceTypeGeneral for Catalogs
            resourceType_xml = etree.Element("resourceType", resourceTypeGeneral="Dataset")
            resourceType_xml.text = resourceType
            doi_resource__node_xml.append(resourceType_xml)

            # Build the recommended part
            subject_subject = doi_dict.get("subject_subject")
            subject_theme = doi_dict.get("subject_theme")
            subject_keyword = doi_dict.get("subject_keyword")
            date_issued = doi_dict.get("date_issued")
            date_modified = doi_dict.get("modified_dcterms")
            relatedIdentifier_document = doi_dict.get("relatedIdentifier_document")
            relatedIdentifier_isPartOf = doi_dict.get("isPartOf")
            relatedIdentifier_hasPart = doi_dict.get("hasPart")
            relatedIdentifier_source = doi_dict.get("relatedIdentifier_source")
            relatedIdentifier_hasVersion = doi_dict.get("relatedIdentifier_hasVersion")
            relatedIdentifier_isVersionOf = doi_dict.get("relatedIdentifier_isVersionOf")
            description_list = doi_dict.get("description")

            subjects_xml = etree.Element('subjects')
            for subject in subject_subject:
                subject_xml = etree.Element("subject", subjectScheme="EuroVoc", schemeURI="http://eurovoc.europa.eu/", valueURI=subject.get("uri"))
                subject_xml.text = subject.get("text")
                subjects_xml.append(subject_xml)

            for theme in subject_theme:
                subject_theme_xml = etree.Element("subject", subjectScheme="MDR Data Themes",
                                                  schemeURI="http://publications.europa.eu/resource/authority/data-theme", valueURI=theme.get("uri"))
                subject_theme_xml.text = theme.get("text")
                subjects_xml.append(subject_theme_xml)
            for keyword in subject_keyword:
                keyword_xml = etree.Element("subject")
                keyword_xml.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = "en"
                keyword_xml.text = keyword
                subjects_xml.append(keyword_xml)
            doi_resource__node_xml.append(subjects_xml)

            dates_xml = etree.Element("dates")
            date_issued_xml = etree.Element("date", dateType="Issued")
            date_issued_xml.text = date_issued
            if date_issued:
                dates_xml.append(date_issued_xml)

            date_modified_xml = etree.Element("date", dateType="Updated")
            date_modified_xml.text = date_modified
            if date_modified:
                dates_xml.append(date_modified_xml)

            if date_modified or date_issued:
                doi_resource__node_xml.append(dates_xml)

            relatedIdentifiers_xml = etree.Element("relatedIdentifiers")
            for document in relatedIdentifier_document:
                identifier_document = document
                relatedIdentifier_document_xml = etree.Element("relatedIdentifier", relatedIdentifierType="PURL", relationType="Documents")
                relatedIdentifier_document_xml.text = identifier_document
                relatedIdentifiers_xml.append(relatedIdentifier_document_xml)

            for isPartOf in relatedIdentifier_isPartOf:
                relatedIdentifier_xml = etree.Element("relatedIdentifier", relatedIdentifierType="PURL", relationType="IsPartOf")
                relatedIdentifier_xml.text = isPartOf
                relatedIdentifiers_xml.append(relatedIdentifier_xml)

            for hasPart in relatedIdentifier_hasPart:
                relatedIdentifier_xml = etree.Element("relatedIdentifier", relatedIdentifierType="PURL", relationType="HasPart")
                relatedIdentifier_xml.text = hasPart
                relatedIdentifiers_xml.append(relatedIdentifier_xml)

            for source in relatedIdentifier_source:
                relatedIdentifier_xml = etree.Element("relatedIdentifier", relatedIdentifierType="PURL", relationType="IsDerivedFrom")
                relatedIdentifier_xml.text = source
                relatedIdentifiers_xml.append(relatedIdentifier_xml)

            for hasVersion in relatedIdentifier_hasVersion:
                relatedIdentifier_xml = etree.Element("relatedIdentifier", relatedIdentifierType="PURL", relationType="HasVersion")
                relatedIdentifier_xml.text = hasVersion
                relatedIdentifiers_xml.append(relatedIdentifier_xml)

            for isVersionOf in relatedIdentifier_isVersionOf:
                relatedIdentifier_xml = etree.Element("relatedIdentifier", relatedIdentifierType="PURL", relationType="IsVersionOf")
                relatedIdentifier_xml.text = isVersionOf
                relatedIdentifiers_xml.append(relatedIdentifier_xml)

            descriptions_xml = etree.Element("descriptions")
            for description in description_list:
                description_xml = etree.Element("description", descriptionType="Abstract")
                description_xml.attrib["{http://www.w3.org/XML/1998/namespace}lang"] = description.get("lang", "en")
                description_xml.text = description.get("text")
                descriptions_xml.append(description_xml)

            doi_resource__node_xml.append(relatedIdentifiers_xml)
            doi_resource__node_xml.append(descriptions_xml)

            # Build the optional part
            languages = doi_dict.get("language")
            for language in languages:
                language_xml = etree.Element("language")
                language_xml.text = language
                doi_resource__node_xml.append(language_xml)
                break


            if is_dataset:
                list_alternateIdentifiers = doi_dict.get("alternateIdentifier", [])
                if list_alternateIdentifiers:
                    alternateIdentifiers_xml = etree.Element("alternateIdentifiers")
                    for alternateIdentifier in list_alternateIdentifiers:  # type: dict
                        type_alternate_Identifier = alternateIdentifier.get("alternateIdentifierType", "PURL")
                        value_alternateIdentifier = alternateIdentifier.get("value","")
                        alternateIdentifier_xml = etree.Element("alternateIdentifier", alternateIdentifierType=type_alternate_Identifier)
                        alternateIdentifier_xml.text = value_alternateIdentifier
                        alternateIdentifiers_xml.append(alternateIdentifier_xml)
                    doi_resource__node_xml.append(alternateIdentifiers_xml)

                versions = doi_dict.get("version", [])
                for version in versions:
                    version_xml = etree.Element("version")
                    version_xml.text = version
                    doi_resource__node_xml.append(version_xml)
            else:
                rights_list_xml = etree.Element("rightsList")
                for right in doi_dict.get("rights"):
                    right_xml = etree.Element("rights", rightsURI=right.get('uri'))
                    right_xml.text = right.get("text")
                    rights_list_xml.append(right_xml)
                if doi_dict.get("rights"):
                    doi_resource__node_xml.append(rights_list_xml)

            doi_xml_str = etree.tostring(doi_resource__node_xml, pretty_print=True)
            return doi_xml_str

        except BaseException as e:
            log.error("Generation of DOI XML failed for dataset {0}".format(doi_dict.get("identifier")))
            log.error(traceback.print_exc(e))
            raise e

    def validate_doi_xml(self):
        '''

        :return str:
        '''
        pass  # TODO validate with schema
