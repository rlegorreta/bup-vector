import os
import logging
from neo4j import GraphDatabase


# ============================================================================================================
# Opens the database and executes queries
# ============================================================================================================
class Neo4jDB:

    def __init__(self):
        host = os.getenv("NEO4J_HOST")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(host, auth=(user, password))
        logging.debug("Database opened")

    def run_query(self, query, params={}):
        with self.driver.session() as session:
            result = session.run(query, params)
            return result.to_df()
