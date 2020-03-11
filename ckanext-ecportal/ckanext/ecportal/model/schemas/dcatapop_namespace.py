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

from rdflib import Graph


class NameSpaceDcatApOp:
    """
        A kind of enumeration of the used namespaces in DcatApOP
    """
    schema = "http://schema.org/"
    adms = "http://www.w3.org/ns/adms#"
    spdx = "http://spdx.org/rdf/terms#"
    dcatap = "http://data.europa.eu/88u/ontology/dcatap#"
    ns = "http://www.w3.org/2003/06/sw-vocab-status/ns#"
    owl = "http://www.w3.org/2002/07/owl#"
    powderDASHs = "http://www.w3.org/2007/05/powder-s#"
    xsd = "http://www.w3.org/2001/XMLSchema#"
    voaf = "http://purl.org/vocommons/voaf#"
    rdfs = "http://www.w3.org/2000/01/rdf-schema#"
    rdf = "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    dcatapop = "http://data.europa.eu/88u/ontology/dcatapop#"
    xml = "http://www.w3.org/XML/1998/namespace"
    dcterms = "http://purl.org/dc/terms/"
    dcat = "http://www.w3.org/ns/dcat#"
    vann = "http://purl.org/vocab/vann/"
    wot = "http://xmlns.com/wot/0.1/"
    foaf = "http://xmlns.com/foaf/0.1/"
    dc = "http://purl.org/dc/elements/1.1/"
    revision = "http://data.europa.eu/88u/revision#"
    vcard = "http://www.w3.org/2006/vcard/ns#"
    skos = "http://www.w3.org/2004/02/skos/core#"
    dqv = "http://www.w3.org/ns/dqv#"
    stat = "http://data.europa.eu/xyz/statdcat-ap/"
    at = "http://publications.europa.eu/ontology/authority/"

    _namespace_dict = {
        'owl': 'http://www.w3.org/2002/07/owl#',
        'powder-s': 'http://www.w3.org/2007/05/powder-s#',
        'dcat': 'http://www.w3.org/ns/dcat#',
        'xml': 'http://www.w3.org/XML/1998/namespace',
        'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
        'wot': 'http://xmlns.com/wot/0.1/',
        'ns': 'http://www.w3.org/2003/06/sw-vocab-status/ns#',
        'schema': 'http://schema.org/',
        'foaf': 'http://xmlns.com/foaf/0.1/',
        'dcatap': 'http://data.europa.eu/88u/ontology/dcatap#',
        'dcatapop': 'http://data.europa.eu/88u/ontology/dcatapop#',
        'dc': 'http://purl.org/dc/elements/1.1/',
        'vann': 'http://purl.org/vocab/vann/',
        'spdx': 'http://spdx.org/rdf/terms#',
        'dcterms': 'http://purl.org/dc/terms/',
        'adms': 'http://www.w3.org/ns/adms#',
        'voaf': 'http://purl.org/vocommons/voaf#',
        'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
        'xsd': 'http://www.w3.org/2001/XMLSchema#',
        'revision': "http://data.europa.eu/88u/revision#",
        'vcard': "http://www.w3.org/2006/vcard/ns#",
        'skos': 'http://www.w3.org/2004/02/skos/core#',
        'dqv':"http://www.w3.org/ns/dqv#",
        'stat':"http://data.europa.eu/xyz/statdcat-ap/",
        'at': "http://publications.europa.eu/ontology/authority/"
    }
    _ns = {}

    _replace_member_parameter = [
        ('-', 'DASH'),
        ('.', 'DOT')
    ]

    def __init__(self):
        """
            create the inverted dict of prefix/namespace,
            To be used when getting the resource from TS for performance purpose only.
        """


    def get_namespace(self, prefix):
        """
        Gete the namespace of the prefix
        :param str prefix: 
        :return str: 
        """
        try:
            for namespace, pre in self._namespace_dict.iteritems():
                if pre == prefix:
                    return namespace
            return None
        except BaseException as e:
            return None

    def get_prefix(self, ns):
        try:
            return getattr(self, ns, None)
        except BaseException as e:
            return None

    def get_member_name(self, uri):
        '''
        :param str uri:
        :return:
        '''
        try:
            for prefix, namespace in self._namespace_dict.iteritems():
                if namespace in uri:
                    # We remove namespace of URI to get the memeber
                    member = uri[len(namespace):]
                    member_name = "{0}_{1}".format(member, prefix)
                    return self.convert_character_to_text(member_name)

        except BaseException as e:
            return None

    def generate_uri_from_member_name(self, member_name):
        '''
        :param str member_name:
        :return:
        '''
        ns = member_name.partition("_")[2]
        local = member_name.partition("_")[0]
        local_name = self.convert_text_to_character(local)
        prefix = getattr(self, ns)
        return "{0}{1}".format(prefix, local_name)

    def replace_characters_occurences(self, member_name, from_character_to_text=True):
        if (member_name):
            for tup in self._replace_member_parameter:
                if (from_character_to_text):
                    member_name = member_name.replace(tup[0], tup[1])
                else:
                    member_name = member_name.replace(tup[1], tup[0])
        return member_name

    def convert_character_to_text(self, member_name):
        return self.replace_characters_occurences(member_name, True)

    def convert_text_to_character(self, member_name):
        return self.replace_characters_occurences(member_name, False)

    def bind_graph_with_namesspace(self, graph=None):
        """
        Build graph by binding the raw namespace to the used ones.
        :param Graph graph:
        :return: Graph
        """
        try:
            gr = graph
            if graph is None:
                gr = Graph()
            for prefix, namespace in self._namespace_dict.iteritems():
                gr.bind(prefix, namespace, True)
            return gr

        except BaseException as e:
            return None


NAMESPACE_DCATAPOP = NameSpaceDcatApOp()


# print NAMESPACE_DCATAPOP.get_member_name("http://www.w3.org/1999/02/22-rdf-syntax-ns#type")
