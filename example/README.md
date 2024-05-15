# Example with Kùzu

### Running the example

First, install PG2RML-star:

```bash
pip install git+https://github.com/arenas-guerrero-julian/pg2rml-star.git
```

Then, run the following Python script to (i) create a [Kùzu](https://github.com/kuzudb/kuzu) database, (ii) load the data from the CSV files in this directory of the repository, and (iii) bootstrap the [RML-star](https://w3id.org/rml/star/spec) mappings.

```python
import kuzu
import pg2rml_star

# create database and connection
db = kuzu.Database('demo.db')
conn = kuzu.Connection(db)

# create schema
conn.execute("CREATE NODE TABLE User(name STRING, age INT64, PRIMARY KEY (name))")
conn.execute("CREATE NODE TABLE City(name STRING, population INT64, PRIMARY KEY (name))")
conn.execute("CREATE REL TABLE Follows(FROM User TO User, since INT64)")
conn.execute("CREATE REL TABLE LivesIn(FROM User TO City)")

# import from CSV
conn.execute('COPY User FROM "user.csv";')
conn.execute('COPY City FROM "city.csv";')
conn.execute('COPY Follows FROM "follows.csv";')
conn.execute('COPY LivesIn FROM "lives_in.csv";')

pg2rml_star.bootstrap_mappings(db)
```

### Bootstrapped RML-star mappings 

```yaml
prefixes:
  rdf: http://www.w3.org/1999/02/22-rdf-syntax-ns#
  xsd: http://www.w3.org/2001/XMLSchema#
  ex: http://example.com/ns#
mappings:
  User:
    sources:
      query: MATCH (x:User) RETURN DISTINCT OFFSET(ID(x)) AS x_User_id, x.name AS
        name, x.age AS age
      referenceFormulation: cypher
    subject: ex:User/$(x_User_id)
    predicateobjects:
    - predicates: rdf:type
      objects:
        value: ex:User
        type: iri
    - predicates: ex:name
      objects:
        value: $(name)
    - predicates: ex:age
      objects:
        value: $(age)
        datatype: xsd:integer
  User_Follows_User:
    sources:
      query: MATCH (x:User)-[r:Follows]->(y:User) RETURN DISTINCT OFFSET(ID(x)) AS
        x_User_id, OFFSET(ID(y)) AS y_User_id, r.since AS since
      referenceFormulation: cypher
    subject: ex:User/$(x_User_id)
    predicateobjects:
    - predicates: ex:Follows
      objects:
        value: ex:User/$(y_User_id)
        type: iri
  User_Follows_User_quoted:
    sources:
      query: MATCH (x:User)-[r:Follows]->(y:User) RETURN DISTINCT OFFSET(ID(x)) AS
        x_User_id, OFFSET(ID(y)) AS y_User_id, r.since AS since
      referenceFormulation: cypher
    subject:
      quoted: User_Follows_User
    predicateobjects:
    - predicates: ex:since
      objects:
        value: $(since)
        datatype: xsd:integer
  User_LivesIn_City:
    sources:
      query: MATCH (x:User)-[r:LivesIn]->(y:City) RETURN DISTINCT OFFSET(ID(x)) AS
        x_User_id, OFFSET(ID(y)) AS y_City_id
      referenceFormulation: cypher
    subject: ex:User/$(x_User_id)
    predicateobjects:
    - predicates: ex:LivesIn
      objects:
        value: ex:City/$(y_City_id)
        type: iri
  City:
    sources:
      query: MATCH (x:City) RETURN DISTINCT OFFSET(ID(x)) AS x_City_id, x.name AS
        name, x.population AS population
      referenceFormulation: cypher
    subject: ex:City/$(x_City_id)
    predicateobjects:
    - predicates: rdf:type
      objects:
        value: ex:City
        type: iri
    - predicates: ex:name
      objects:
        value: $(name)
    - predicates: ex:population
      objects:
        value: $(population)
        datatype: xsd:integer
```
