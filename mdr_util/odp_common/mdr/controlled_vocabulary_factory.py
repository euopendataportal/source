from odp_common.mdr.controlled_vocabulary import ControlledVocabularyUtil, CorporateBodiesUtil

class _Singleton(type):
    """ This is a Singleton metaclass. All classes affected by this metaclass
        have the property that only one instance is created for each set of arguments
        passed to the class constructor."""

    def __init__(cls, name, bases, dict):
        super(_Singleton, cls).__init__(cls, bases, dict)
        cls._instanceDict = {}

    def __call__(cls, *args, **kwargs):
        argdict = {'args': args}
        argdict.update(kwargs)
        argset = frozenset(argdict)
        if argset not in cls._instanceDict:
            cls._instanceDict[argset] = super(_Singleton, cls).__call__(*args, **kwargs)
        return cls._instanceDict[argset]



class ControlledVocabularyFactory(object):
    '''
    Fleigweight object to load a controlled_vocabulary_util once.
    Provides operations with multiple mdr involved.
    '''
    __metaclass__ = _Singleton
    DOI_URIS = {'notation-type':'http://publications.europa.eu/resource/authority/notation-type/DOI',
     'datacite': 'http://purl.org/spar/datacite/doi'}

    LANGUAGE = 'http://publications.europa.eu/resource/authority/language'
    DATASE_STATUS = 'http://publications.europa.eu/resource/authority/dataset-status'
    COUNTRY = 'http://publications.europa.eu/resource/authority/country'
    FREQUENCY = 'http://publications.europa.eu/resource/authority/frequency'
    LICENSE = 'http://publications.europa.eu/resource/authority/licence'
    DATASET_TYPE = 'http://publications.europa.eu/resource/authority/dataset-type'
    DISTRIBUTION_TYPE = 'http://publications.europa.eu/resource/authority/distribution-type'
    DOCUMENTATION_TYPE = 'http://publications.europa.eu/resource/authority/documentation-type'
    DATA_THEME = 'http://publications.europa.eu/resource/authority/data-theme'
    EUROVOC = 'http://eurovoc.europa.eu'
    ADAMS = 'http://purl.org/adms'
    CORPORATE_BODY = 'http://publications.europa.eu/resource/authority/corporate-body'
    FILE_TYPE = 'http://publications.europa.eu/resource/authority/file-type'
    NOTATION_TYPE = 'http://publications.europa.eu/resource/authority/notation-type'
    DATACITE_NOTATION = 'http://purl.org/spar/datacite'
    TIMEPERIODS = 'http://publications.europa.eu/resource/authority/timeperiod'
    ACCESS_RIGHTS = 'http://publications.europa.eu/resource/authority/access-right'
    PLACE = 'http://publications.europa.eu/resource/authority/place'
    ATU = 'http://publications.europa.eu/resource/authority/atu'
    ATU_TYPE = 'http://publications.europa.eu/resource/authority/atu-type'
    CONTINENTS = 'http://publications.europa.eu/resource/authority/continent'

    vocab_theme = DATA_THEME
    res_format = FILE_TYPE
    vocab_concepts_eurovoc = EUROVOC
    vocab_geographical_coverage = COUNTRY
    vocab_language = LANGUAGE

    _mdr_cache = None  #type dict[str, ControlledVocabularyUtil]


    def get_controlled_vocabulary_util(self, mdr_graph_name):
        '''

        :param str mdr_graph_name:
        :return: ControlledVocabularyUtil
        '''
        if isinstance(mdr_graph_name, list):
            raise AttributeError('Passed parameter must be String, please handle list yourself {0}'.format(mdr_graph_name))

        if not self._mdr_cache:
            self._mdr_cache = {}

        if mdr_graph_name in self._mdr_cache:
            return self._mdr_cache.get(mdr_graph_name)

        elif self.CORPORATE_BODY != mdr_graph_name:
            new_mdr = ControlledVocabularyUtil(mdr_graph_name)
            self._mdr_cache[mdr_graph_name] = new_mdr
            return new_mdr
        else:
            new_mdr = CorporateBodiesUtil(mdr_graph_name)
            self._mdr_cache[mdr_graph_name] = new_mdr
            return new_mdr

    def find_mdr_item_for_text_label(self, term):

        for graph in self.__MANAGED_CONTROLLED_VOCABULARIES:
            mdr = self.get_controlled_vocabulary_util(graph)

            for uri in mdr.get_all_uris():

                if term in mdr.get_all_translations(uri):
                    return mdr

        return None

    def get_translation_from_uri(self, mdr_item_uri, language):
        graph = mdr_item_uri.rsplit('/', 1)[0]

        mdr = self.get_controlled_vocabulary_util(graph)

        result = mdr.get_translation_for_language(mdr_item_uri,language)
        return result




    def get_all_descriptions_from_list_of_mdr(self, graph_name_list):

        result = [] # type

        return result

    def get_all_vocabulary_utils(self):
        result = {}
        for mdr in self.__MANAGED_CONTROLLED_VOCABULARIES:

            result[mdr] = self.get_controlled_vocabulary_util(mdr)

        return result


    __MANAGED_CONTROLLED_VOCABULARIES = ['http://publications.europa.eu/resource/authority/language',
        'http://publications.europa.eu/resource/authority/dataset-status',
        'http://publications.europa.eu/resource/authority/country',
        'http://publications.europa.eu/resource/authority/frequency',
        'http://publications.europa.eu/resource/authority/licence',
        'http://publications.europa.eu/resource/authority/dataset-type',
        'http://publications.europa.eu/resource/authority/distribution-type',
        'http://publications.europa.eu/resource/authority/documentation-type',
        'http://publications.europa.eu/resource/authority/data-theme',
        'http://eurovoc.europa.eu',
        'http://purl.org/adms',
        'http://publications.europa.eu/resource/authority/corporate-body',
        'http://publications.europa.eu/resource/authority/file-type',
        'http://publications.europa.eu/resource/authority/notation-type',
        'http://publications.europa.eu/resource/authority/timeperiod',
        'http://publications.europa.eu/resource/authority/access-right',
        'http://publications.europa.eu/resource/authority/place',
        'http://publications.europa.eu/resource/authority/atu',
        'http://publications.europa.eu/resource/authority/atu-type',
        'http://publications.europa.eu/resource/authority/continent']
