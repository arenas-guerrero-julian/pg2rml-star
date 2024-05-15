__author__ = "Julián Arenas-Guerrero"
__credits__ = ["Julián Arenas-Guerrero"]
__copyright__ = "Copyright © 2024 Julián Arenas-Guerrero"

__license__ = "Apache-2.0"
__maintainer__ = "Julián Arenas-Guerrero"
__email__ = "julian.arenas.guerrero@upm.es"


import argparse

from pg2rml_star import bootstrap_mappings


parser = argparse.ArgumentParser(
        description='A Direct Mapping from Property Graphs to RDF-star.',
        epilog="Copyright © 2024 Julián Arenas-Guerrero",
        allow_abbrev=False,
        prog='python3 -m pg2rml_star',
        argument_default=argparse.SUPPRESS
    )

parser.add_argument('database_url_path', help='Neo4j url or path to Kuzu database')
parser.add_argument('-o', '--output_file_path',
                    help='File path to wire the output mappings (if not provided mappings will be redirected to stdout)')

args = parser.parse_args()

if 'output_file_path' in args:
    bootstrap_mappings(args.database_url_path, args.output_file_path)
else:
    bootstrap_mappings(args.database_url_path)
