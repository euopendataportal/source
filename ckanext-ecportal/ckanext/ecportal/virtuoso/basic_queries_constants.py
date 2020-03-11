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

from ckanext.ecportal.model.common_constants import DCATAPOP_PRIVATE_GRAPH_NAME, DCATAPOP_PUBLIC_GRAPH_NAME
from ckanext.ecportal.virtuoso.predicates_constants import AUTHORITY_CODE_PREDICATE, IN_SCHEME_PREDICATE
from ckanext.ecportal.virtuoso.graph_names_constants import GRAPH_CORPORATE_BODY

SELECT_ALL_DCATAPOP_PUBLIC = "SELECT * FROM <dcatapop-PUBLIC> WHERE {?S ?p ?o}"

SELECT_ALL_DCATAPOP_PRIVATE = "SELECT * FROM <dcatapop-private> WHERE {?S ?p ?o}"

DROP_PUBLIC_GRAPH = " drop silent graph <" + DCATAPOP_PUBLIC_GRAPH_NAME + "> "

CREATE_PUBLIC_GRAPH = " create silent graph <" + DCATAPOP_PUBLIC_GRAPH_NAME + "> "

RECREATE_PUBLIC_GRAPH = DROP_PUBLIC_GRAPH + CREATE_PUBLIC_GRAPH

DROP_PRIVATE_GRAPH = " drop silent graph <" + DCATAPOP_PRIVATE_GRAPH_NAME + "> "

CREATE_PRIVATE_GRAPH = "create silent graph <" + DCATAPOP_PRIVATE_GRAPH_NAME + ">"

RECREATE_PRIVATE_GRAPH = DROP_PRIVATE_GRAPH + CREATE_PRIVATE_GRAPH

RESET_TRIPLE_STORES = RECREATE_PUBLIC_GRAPH + RECREATE_PRIVATE_GRAPH

SHOW_TABLES = "SELECT * FROM pg_catalog.pg_tables"

SELECT_ALL_AUTHORITY_CODE = "select ?s ?o from <" + GRAPH_CORPORATE_BODY + "> where {?s <" + IN_SCHEME_PREDICATE + "> <" + GRAPH_CORPORATE_BODY + ">. ?s\
<" + AUTHORITY_CODE_PREDICATE + "> ?o}"

SELECT_ALL_WITH_GRAPH_NAME = "SELECT * WHERE { graph ?g { ?s ?p ?o } }"