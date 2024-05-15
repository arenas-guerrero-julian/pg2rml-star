# PG2RML-star

**PG2RML-star** is an implementation of the direct mapping from property graphs to [RDF-star](https://w3c.github.io/rdf-star/cg-spec/2021-12-17.html). It bootstraps [RML](https://kg-construct.github.io/rml-resources/portal/) mappings from property graph databases that can then be customized by users. These mappings can be provided to RML systems such as [Morph-KGC](https://github.com/morph-kgc/morph-kgc/) to generate the RDF-star knowledge graph. To facilitate mapping customization by users, PG2RML-star creates the mappings in [YARRRML](https://rml.io/yarrrml/spec/) syntax, a user-friendly serialization of RML. PG2RML-star currently supports the following GDBMSs:
- [Neo4j](https://neo4j.com/)
- [Kùzu](https://github.com/kuzudb/kuzu)

## Getting Started :rocket:

**[PyPi](https://pypi.org/project/pg2rml_star/)** is the fastest way to install PG2RML-star:
```bash
pip install pg2rml_star
```

We recommend to use **[virtual environments](https://docs.python.org/3/library/venv.html#)**.

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

## License :unlock:

`pg2rml_star` is available under the **[Apache License 2.0](https://github.com/morph-kgc/morph-kgc/blob/main/LICENSE)**.

## Author & Contact :mailbox_with_mail:

- **[Julián Arenas-Guerrero](https://github.com/arenas-guerrero-julian/) - [julian.arenas.guerrero@upm.es](mailto:julian.arenas.guerrero@upm.es)**

*[Universidad Politécnica de Madrid](https://www.upm.es/internacional)*.
