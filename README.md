# PG2RML-star

**PG2RML-star** bootstraps [RML-star](https://kg-construct.github.io/rml-resources/portal/) mappings from property graph databases that can then be customized by users with domain vocabularies. The mappings can then be used with an RML system such as [Morph-KGC](https://github.com/morph-kgc/morph-kgc/) to generate the RDF-star knowledge graph. To facilitate mapping customization by users, PG2RML-star creates the mappings in [YARRRML](https://rml.io/yarrrml/spec/) syntax, a user-friendly serialization of RML. PG2RML-star currently supports the following property graph databases:
- [Neo4j](https://neo4j.com/)
- [Kùzu](https://github.com/kuzudb/kuzu)

## Getting Started :rocket:

### Install

```bash
pip install git+https://github.com/arenas-guerrero-julian/pg2rml-star.git
```

### Command line

```commandline
usage: python3 -m pg2rml_star [-h] [-o OUTPUT_FILE_PATH] [-v] database_url_path

positional arguments:
  database_url_path     Neo4j url or path to Kuzu database

options:
  -h, --help            show this help message and exit
  -o OUTPUT_FILE_PATH, --output_file_path OUTPUT_FILE_PATH
                        File path to wire the output mappings (if not provided mappings will be redirected to stdout)
```

**Neo4j** example (modify the database URL accordingly):

```
python3 -m pg2rml_star neo4j://localhost:port@my_username:my_password/my_database
```

**Kùzu** example:

```
python3 -m pg2rml_star path/to/my_kuzu_database
```

### Library

```python
import pg2rml_star

# Neo4j

# redirect output mappings to stdout
pg2rml_star.bootstrap_mappings('neo4j://localhost:port@my_username:my_password/my_database')

# redirect output mappings to file
pg2rml_star.bootstrap_mappings('neo4j://localhost:port@my_username:my_password/my_database', 'mappings.yml')

# Kùzu

# if the Kùzu database is persisted on disk
pg2rml_star.bootstrap_mappings('path/to/my_kuzu_database')

# if the Kùzu database is loaded
import kuzu
db = kuzu.Database('./test')
pg2rml_star.bootstrap_mappings(db)
```

## Author & Contact :mailbox_with_mail:

- **[Julián Arenas-Guerrero](https://github.com/arenas-guerrero-julian/) - [julian.arenas.guerrero@upm.es](mailto:julian.arenas.guerrero@upm.es)**

*[Universidad Politécnica de Madrid](https://www.upm.es/internacional)*.
