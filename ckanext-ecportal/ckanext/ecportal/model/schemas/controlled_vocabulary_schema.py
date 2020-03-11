from ckanext.ecportal.model.schemas.generic_schema import SchemaGeneric, ResourceValue
from ckanext.ecportal.model.schemas import NAMESPACE_DCATAPOP


class ConceptSchemaSkos(SchemaGeneric):
    type_rdf = NAMESPACE_DCATAPOP.skos + 'Concept'

    def __init__(self, uri, graph_name):
        super(ConceptSchemaSkos, self).__init__(uri, graph_name)

        self.type_rdf['0'] = SchemaGeneric(self.type_rdf, graph_name)
        self.identifier_dc = {} # type: dict[str,ResourceValue] #Literal
        self.prefLabel_skos = {} # type: dict[str,ResourceValue] #Literal
        self.altLabel_skos = {} # type: dict[str,ResourceValue] #Literal
        self.inScheme_skos = {} # type: dict[str,ResourceValue] #Literal
        self.authorityDASHcode_at = {} # type: dict[str,ResourceValue] #Literal
        self.opDASHcode_at = {} # type: dict[str,ResourceValue] #Literal
        self.opDASHcode_atold = {} # type: dict[str,ResourceValue] #Literal
        self.startDOTuse_at = {} # type: dict[str,ResourceValue] #Literal
        self.deprecated_at = {} # type: dict[str,ResourceValue] #Literal


class ConceptSchemeSchemaSkos(SchemaGeneric):
    type_rdf = NAMESPACE_DCATAPOP.skos + 'ConceptScheme'

    def __init__(self, uri, graph_name):
        super(ConceptSchemeSchemaSkos, self).__init__(uri, graph_name)

        self.type_rdf['0'] = SchemaGeneric(self.type_rdf, graph_name)
        self.label_rdfs = {} # type: dict[str,ResourceValue] #Literal
        self.versionInfo_owl = {} # type: dict[str,ResourceValue] #Literal
        self.prefLabel_at = {} # type: dict[str,ResourceValue] #Literal
        self.tableDOTid_at = {} # type: dict[str,ResourceValue] #Literal
        self.tableDOTversionDOTnumber_at = {} # type: dict[str,ResourceValue] #Literal


class CorporateBody(ConceptSchemaSkos):

    def __init__(self, uri, graph_name):
        super(CorporateBody, self).__init__(uri, graph_name)

        self.narrower_skos = {} # type: dict[str,SchemaGeneric]
        self.broader_skos = {} # type: dict[str,SchemaGeneric]

