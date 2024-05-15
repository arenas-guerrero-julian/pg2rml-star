__author__ = "Julián Arenas-Guerrero"
__credits__ = ["Julián Arenas-Guerrero"]
__copyright__ = "Copyright © 2024 Julián Arenas-Guerrero"

__license__ = "Apache-2.0"
__maintainer__ = "Julián Arenas-Guerrero"
__email__ = "julian.arenas.guerrero@upm.es"


import sys
import neo4j

from urllib.parse import quote
from ruamel.yaml import YAML
from .constants import PANDAS_TO_XSD_DATATYPES


def bootstrap_neo4j(neo4j_url, user, password, database, output_path=None):
    dm = {
        'prefixes': {
            'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
            'xsd': 'http://www.w3.org/2001/XMLSchema#',
            'ex': 'http://example.com/ns#'
        },
        'mappings': {}
    }

    driver = neo4j.GraphDatabase.driver(neo4j_url, auth=(user, password))

    results_nodes, _, _ = driver.execute_query("MATCH (n) RETURN DISTINCT LABELS(n) AS node_labels", database=database, routing=neo4j.RoutingControl.READ)
    nodes = [result['node_labels'] for result in results_nodes]

    for node in nodes:
        # ------ NODE TRIPLES MAP

        # a node may have multiple labels
        node_label = '_'.join(node)

        # get the properties of the node
        results_node_properties, _, _ = driver.execute_query(f"MATCH (n:{':'.join(node)}) RETURN PROPERTIES(n) AS properties LIMIT 1", database=database, routing=neo4j.RoutingControl.READ)
        node_properties = list(results_node_properties[0]['properties'].keys())

        dm['mappings'][node_label] = {}

        tm_query = f"MATCH (x:{':'.join(node)}) RETURN DISTINCT ID(x) AS x_{node_label}_id"

        for property in node_properties:
            tm_query += f', x.{property} AS {property}'

        dm['mappings'][node_label]['sources'] = {
            'query': tm_query,
            'referenceFormulation': 'cypher'
        }

        dm['mappings'][node_label]['subject'] = f'ex:{quote(node_label)}/$(x_{node_label}_id)'

        dm['mappings'][node_label]['predicateobjects'] = []
        for n in node:
            dm['mappings'][node_label]['predicateobjects'].append({
                'predicates': 'rdf:type',
                'objects': {
                    'value': f'ex:{n}',
                    'type': 'iri'
                }
            })

        for property in node_properties:
            pom = {
                'predicates': f'ex:{quote(property)}',
                'objects': {
                    'value': f'$({property})'
                }
            }

            # infer and add datatype
            property_datatype_df = driver.execute_query(f"MATCH (x:{':'.join(node)}) RETURN DISTINCT x.{property} AS {property} LIMIT 1000", database=database, result_transformer_=neo4j.Result.to_df)
            property_datatype = property_datatype_df[property].dtypes
            if str(property_datatype) in PANDAS_TO_XSD_DATATYPES:
                pom['objects']['datatype'] = PANDAS_TO_XSD_DATATYPES[str(property_datatype)]
            dm['mappings'][node_label]['predicateobjects'].append(pom)

            # ------ TRIPLES MAPS FOR NODE RELATIONS
            results_node_relations, _, _ = driver.execute_query(f"MATCH (x:{':'.join(node)})-[f]->(y) RETURN DISTINCT TYPE(f) AS LABELR, LABELS(y) AS LABELSN", database=database, routing=neo4j.RoutingControl.READ)

            for results_node_relation in results_node_relations:
                rel = results_node_relation['LABELR']
                rel_node = results_node_relation['LABELSN']

                tm_query = f"MATCH (x:{':'.join(node)})-[r:{rel}]->(y:{':'.join(rel_node)}) RETURN DISTINCT ID(x) AS x_{'_'.join(node)}_id, ID(y) AS y_{'_'.join(rel_node)}_id"

                results_node_relations_properties, _, _ = driver.execute_query(f"MATCH (x:{':'.join(node)})-[r:{rel}]->(y:{':'.join(rel_node)}) RETURN PROPERTIES(r) AS PROPERTIESR LIMIT 1", database=database, routing=neo4j.RoutingControl.READ)
                node_relations_properties = list(results_node_relations_properties[0]['PROPERTIESR'].keys())
                for property in node_relations_properties:
                    tm_query += f', r.{property} AS {property}'

                dm['mappings'][f"{node_label}_{rel}_{'_'.join(rel_node)}"] = {
                    'sources': {
                        'query': tm_query,
                        'referenceFormulation': 'cypher'
                    },
                    'subject': f"ex:{quote(node_label)}/$(x_{'_'.join(node)}_id)",
                    'predicateobjects': [{
                        'predicates': f'ex:{rel}',
                        'objects': {
                            'value': f"ex:{quote('_'.join(rel_node))}/$(y_{'_'.join(rel_node)}_id)",
                            'type': 'iri'
                        }
                    }]
                }

                # ------ TRIPLES MAPS FOR NODE RELATIONS PROPERTIES
                if node_relations_properties:
                    dm['mappings'][f"{node_label}_{rel}_{'_'.join(rel_node)}_quoted"] = {
                        'sources': {
                            'query': tm_query,
                            'referenceFormulation': 'cypher'
                        },
                        'subject': {
                            'quoted': f"{node_label}_{rel}_{'_'.join(rel_node)}"
                        },
                        'predicateobjects': []
                    }

                    for property in node_relations_properties:
                        pom = {
                            'predicates': f'ex:{quote(property)}',
                            'objects': {
                                'value': f'$({property})'
                            }
                        }

                        # infer and add datatype
                        property_datatype_df = driver.execute_query(f"{tm_query} LIMIT 1000", database=database, result_transformer_=neo4j.Result.to_df)
                        property_datatype = property_datatype_df[property].dtypes
                        if str(property_datatype) in PANDAS_TO_XSD_DATATYPES:
                            pom['objects']['datatype'] = PANDAS_TO_XSD_DATATYPES[str(property_datatype)]
                        dm['mappings'][f"{node_label}_{rel}_{'_'.join(rel_node)}_quoted"]['predicateobjects'].append(pom)

    yaml = YAML()
    if output_path:
        with open(output_path, "w") as f:
            yaml.dump(dm, f)
    else:
        yaml.dump(dm, sys.stdout)
