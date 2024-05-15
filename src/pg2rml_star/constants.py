__author__ = "Julián Arenas-Guerrero"
__credits__ = ["Julián Arenas-Guerrero"]
__copyright__ = "Copyright © 2024 Julián Arenas-Guerrero"

__license__ = "Apache-2.0"
__maintainer__ = "Julián Arenas-Guerrero"
__email__ = "julian.arenas.guerrero@upm.es"


PANDAS_TO_XSD_DATATYPES = {
    'int64': 'xsd:integer',
    'float64': 'xsd:double',
    'bool': 'xsd:boolean',
    'datetime64': 'xsd:dateTime'
}


KUZU_INTERNAL_FIELDS = ['_id', '_label', '_dst', '_src']
