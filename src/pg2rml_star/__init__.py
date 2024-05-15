__author__ = "Julián Arenas-Guerrero"
__credits__ = ["Julián Arenas-Guerrero"]
__copyright__ = "Copyright © 2024 Julián Arenas-Guerrero"

__license__ = "Apache-2.0"
__maintainer__ = "Julián Arenas-Guerrero"
__email__ = "julian.arenas.guerrero@upm.es"


def bootstrap_mappings(database_access, output_path=None):
    if type(database_access) is str and '://' in database_access:
        # NEO4J
        from .dm_neo4j import bootstrap_neo4j

        # bolt://localhost:7687@neo4j:neo4jjulian/neo4j
        database = database_access.split('/')[-1]
        db_url = '/'.join(database_access.split('/')[:-1])
        db_url, user_password = db_url.split('@')
        user, password = user_password.split(':')

        bootstrap_neo4j(db_url, user, password, database, output_path)
    else:
        # KUZU
        from .dm_kuzu import bootstrap_kuzu

        bootstrap_kuzu(database_access, output_path)
