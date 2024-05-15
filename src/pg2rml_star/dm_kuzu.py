__author__ = "Julián Arenas-Guerrero"
__credits__ = ["Julián Arenas-Guerrero"]
__copyright__ = "Copyright © 2024 Julián Arenas-Guerrero"

__license__ = "Apache-2.0"
__maintainer__ = "Julián Arenas-Guerrero"
__email__ = "julian.arenas.guerrero@upm.es"


import sys
import kuzu

from urllib.parse import quote
from ruamel.yaml import YAML
from .constants import PANDAS_TO_XSD_DATATYPES, KUZU_INTERNAL_FIELDS


def bootstrap_kuzu(kuzu_object, output_path=None):
    dm = {
        'prefixes': {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            'ns': 'http://example.com/ns#'
        },
        'mappings': {}
    }

    db = kuzu_object if type(kuzu_object) is kuzu.Database else kuzu.Database(kuzu_object, buffer_pool_size=1024**3)
    conn = kuzu.Connection(db)

    # find nodes
    results_nodes = conn.execute('MATCH (a) RETURN DISTINCT LABEL(a) AS node_label')
    nodes = []
    while results_nodes.has_next():
        nodes += results_nodes.get_next()

    for node in nodes:
        # ------ NODE TRIPLES MAP

        # get the properties of the node
        results_node_properties = conn.execute(f'MATCH (x:{node}) RETURN x LIMIT 1')
        node_properties = [property for property in results_node_properties.get_next()[0].keys() if not property in KUZU_INTERNAL_FIELDS]

        dm['mappings'][node] = {}

        tm_query = f'MATCH (x:{node}) RETURN DISTINCT OFFSET(ID(x)) AS x_{node}_id'
        for property in node_properties:
            tm_query += f', x.{property} AS {property}'
        dm['mappings'][node]['sources'] = {
            'query': tm_query,
            'referenceFormulation': 'cypher'
        }

        dm['mappings'][node]['subject'] = f'ns:{quote(node)}/$(x_{node}_id)'

        dm['mappings'][node]['predicateobjects'] = []
        dm['mappings'][node]['predicateobjects'].append({
            'predicates': 'rdf:type',
            'objects': {
                'value': f'ns:{node}',
                'type': 'iri'
            }
        })

        for property in node_properties:
            pom = {
                'predicates': f'ns:{quote(property)}',
                'objects': {
                    'value': f'$({property})'
                }
            }

            # infer and add datatype
            property_datatype = conn.execute(f'MATCH (x:{node}) RETURN DISTINCT x.{property} AS {property} LIMIT 1000').get_as_df().dtypes.iloc[0]
            if str(property_datatype) in PANDAS_TO_XSD_DATATYPES:
                pom['objects']['datatype'] = PANDAS_TO_XSD_DATATYPES[str(property_datatype)]
            dm['mappings'][node]['predicateobjects'].append(pom)

        # ------ TRIPLES MAPS FOR NODE RELATIONS
        try:
            results_node_relations = conn.execute(f'MATCH (x:{node})-[f]->(y) RETURN DISTINCT LABEL(f) AS LABELR, LABEL(y) AS LABELN')
            while results_node_relations.has_next():
                rel = results_node_relations.get_next()
                tm_query = f'MATCH (x:{node})-[r:{rel[0]}]->(y:{rel[1]}) RETURN DISTINCT OFFSET(ID(x)) AS x_{node}_id, OFFSET(ID(y)) AS y_{rel[1]}_id'

                results_node_relations_properties = conn.execute(f'MATCH (x:{node})-[r:{rel[0]}]->(y:{rel[1]}) RETURN r LIMIT 1')
                while results_node_relations_properties.has_next():
                    node_relations_properties = [property for property in results_node_relations_properties.get_next()[0].keys() if not property in KUZU_INTERNAL_FIELDS]
                    for property in node_relations_properties:
                        tm_query += f', r.{property} AS {property}'

                dm['mappings'][f'{node}_{rel[0]}_{rel[1]}'] = {
                    'sources': {
                        'query': tm_query,
                        'referenceFormulation': 'cypher'
                    },
                    'subject': f'ns:{quote(node)}/$(x_{node}_id)',
                    'predicateobjects': [{
                        'predicates': f'ns:{rel[0]}',
                        'objects': {
                            'value': f'ns:{quote(rel[1])}/$(y_{rel[1]}_id)',
                            'type': 'iri'
                        }
                    }]
                }

                # ------ TRIPLES MAPS FOR NODE RELATIONS PROPERTIES
                if node_relations_properties:
                    dm['mappings'][f'{node}_{rel[0]}_{rel[1]}_quoted'] = {
                        'sources': {
                            'query': tm_query,
                            'referenceFormulation': 'cypher'
                        },
                        'subject': {
                            'quoted': f'{node}_{rel[0]}_{rel[1]}'
                        },
                        'predicateobjects': []
                    }

                    for property in node_relations_properties:
                        pom = {
                            'predicates': f'ns:{quote(property)}',
                            'objects': {
                                'value': f'$({property})'
                            }
                        }

                        # infer and add datatype
                        property_datatype = conn.execute(f'{tm_query} LIMIT 1000').get_as_df()[property].dtypes
                        if str(property_datatype) in PANDAS_TO_XSD_DATATYPES:
                            pom['objects']['datatype'] = PANDAS_TO_XSD_DATATYPES[str(property_datatype)]

                        dm['mappings'][f'{node}_{rel[0]}_{rel[1]}_quoted']['predicateobjects'].append(pom)
        except:
            pass

    yaml = YAML()
    if output_path:
        with open(output_path, "w") as f:
            yaml.dump(dm, f)
    else:
        yaml.dump(dm, sys.stdout)
