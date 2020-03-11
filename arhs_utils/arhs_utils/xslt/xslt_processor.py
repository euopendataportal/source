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


"""
XSLTProcessor
"""

import lxml.etree as ET


class XSLTProcessor:

    def __init__(self):
        pass

    def process(self, input_xml, xsl):
        """
        Generate metadata XML data for dataset rdf.
        :param str input_xml: XML input data
        :param str xsl: XSL transformation file path
        :return transformed output XML data.
        """
        dom = ET.parse(input_xml)
        xslt = ET.parse(xsl)
        transform = ET.XSLT(xslt)
        output = transform(dom)
        return output
