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

class LanguagesConstants:
    def __init__(self):
        pass

    LANGUAGE_CODE_FR = "fr"

    LANGUAGE_CODE_EN = "en"

    LANGUAGE_CODE_HR = 'hr'

    LANGUAGE_CODE_SV = 'sv'

    LANGUAGE_CODE_SL = 'sl'

    LANGUAGE_CODE_SK = 'sk'

    LANGUAGE_CODE_RO = 'ro'

    LANGUAGE_CODE_PT = 'pt'

    LANGUAGE_CODE_MT = 'mt'

    LANGUAGE_CODE_HU = 'hu'

    LANGUAGE_CODE_EL = 'el'

    LANGUAGE_CODE_FI = 'fi'

    LANGUAGE_CODE_ET = 'et'

    LANGUAGE_CODE_NL = 'nl'

    LANGUAGE_CODE_DA = 'da'

    LANGUAGE_CODE_CS = 'cs'

    LANGUAGE_CODE_LT = 'lt'

    LANGUAGE_CODE_BG = 'bg'

    LANGUAGE_CODE_LV = 'lv'

    LANGUAGE_CODE_GA = 'ga'

    LANGUAGE_CODE_PL = 'pl'

    LANGUAGE_CODE_ES = 'es'

    LANGUAGE_CODE_IT = 'it'

    LANGUAGE_CODE_DE = 'de'

    LANGUAGES = [LANGUAGE_CODE_EN, LANGUAGE_CODE_FR, LANGUAGE_CODE_DE, LANGUAGE_CODE_IT, LANGUAGE_CODE_ES,
                 LANGUAGE_CODE_PL, LANGUAGE_CODE_GA, LANGUAGE_CODE_LV, LANGUAGE_CODE_BG, LANGUAGE_CODE_LT,
                 LANGUAGE_CODE_CS, LANGUAGE_CODE_DA, LANGUAGE_CODE_NL, LANGUAGE_CODE_ET, LANGUAGE_CODE_FI,
                 LANGUAGE_CODE_EL, LANGUAGE_CODE_HU, LANGUAGE_CODE_MT, LANGUAGE_CODE_PT, LANGUAGE_CODE_RO,
                 LANGUAGE_CODE_SK, LANGUAGE_CODE_SL, LANGUAGE_CODE_SV, LANGUAGE_CODE_HR]
    @classmethod
    def get_languages_as_list(self):
        languages = []
        for language, value in self.__dict__.iteritems():
            if "_CODE_" in language:
                languages.append(unicode(value))
        return languages

