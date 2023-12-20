import os
import logging
from dotenv import load_dotenv
from neo4jdb import Neo4jDB
from vectorciacia import VectorsCiaCia
from vectorpersonperson import VectorsPersonPerson
from vectorciaperson import VectorsCiaPerson
from vectorpersoncia import VectorsPersonCia

# =========================================================================
# Global variables & initialization for the environment variables
load_dotenv()  # note: this line must be commented when we want to dockerize it


# ============================================================================================================
# Main body
# ============================================================================================================
if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    logging.info(f'Start application:{os.getenv("APP_NAME")} version:{os.getenv("VERSION")}')
    neo4jdb = Neo4jDB()

    if logging.getLogger().level == logging.DEBUG:
        vectorCiaCia = VectorsCiaCia(neo4jdb)
        logging.info("===================================")
        logging.info(f'Contexto utilizado para Compañías<->Compañías:\n{(vectorCiaCia.displayContext())}\n')
        logging.info("==============================")
        logging.info(
            f'Se genera el text embebido de acuerdo al contexto en los nodos de "Compania":{vectorCiaCia.generateTextEmbedding()}')
        logging.info("==============================\n  P R E G U N T A S")
        logging.info("==============================")
        ask = "¿Qué compañías tienen relación con la compañía ACME SA de CV?"
        logging.info(f'{ask}\n------------------------------')
        logging.info(vectorCiaCia.generateAnswer(ask))
        logging.info("==============================")
        ask = "¿Cuales son las compañías subsidiarias de ACME SA de CV?"
        logging.info(f'{ask}\n------------------------------')
        logging.info(vectorCiaCia.generateAnswer(ask))
        logging.info("==============================")
        ask = "¿Quién es similar a la compañía ACME SA de CV?"
        logging.info(f'{ask}\n------------------------------')
        logging.info(vectorCiaCia.generateAnswer(ask))
        logging.info("==============================")
        ask = "¿Qué compañías pertenecen al negocio de Financieras?"
        logging.info(f'{ask}\n------------------------------')
        logging.info(vectorCiaCia.generateAnswer(ask))

    if logging.getLogger().level == logging.DEBUG:
        vectorPersonPerson = VectorsPersonPerson(neo4jdb)
        logging.info("===================================")
        logging.info(f'Contexto utilizado para Personas<->Personas:\n{(vectorPersonPerson.displayContext())}\n')
        logging.info("==============================")
        logging.info(
            f'Se genera el text embebido de acuerdo al contexto en los nodos de "Persona":{vectorPersonPerson.generateTextEmbedding()}')
        logging.info("==============================\n  P R E G U N T A S")
        logging.info("==============================")
        ask = "¿Quién tiene relación con Jesus Torres Beckmann?"
        logging.info(f'{ask}\n------------------------------')
        logging.info(vectorPersonPerson.generateAnswer(ask))
        logging.info("==============================")
        ask = "¿Quién trabaja en ACME SA de CV?"
        logging.info(f'{ask}\n------------------------------')
        logging.info(vectorPersonPerson.generateAnswer(ask))
        logging.info("==============================")
        ask = "¿Que persona es similar a Diego Balli Armella?"
        logging.info(f'{ask}\n------------------------------')
        logging.info(vectorPersonPerson.generateAnswer(ask))
        logging.info("==============================")
        ask = "¿Quienes son solteros?"
        logging.info(f'{ask}\n------------------------------')
        logging.info(vectorPersonPerson.generateAnswer(ask))

    if logging.getLogger().level == logging.DEBUG:
        vectorCiaPerson = VectorsCiaPerson(neo4jdb)
        logging.info("===================================")
        logging.info(f'Contexto utilizado para Compañías<->Personas:\n{(vectorCiaPerson.displayContext())}\n')
        logging.info("==============================")
        logging.info(
            f'Se genera el text embebido Personas de acuerdo al contexto en los nodos de "Companias":{vectorCiaPerson.generateTextEmbedding()}')
        logging.info("==============================\n  P R E G U N T A S")
        logging.info("==============================")
        ask = "¿En que compañía trabaja la persona Patrico Garcia Cano?"
        logging.info(f'{ask}\n------------------------------')
        logging.info(vectorCiaPerson.generateAnswer(ask))
        logging.info("==============================")
        ask = "¿Que compañía tiene como contador a la persona Juan Perez Hernández?"
        logging.info(f'{ask}\n------------------------------')
        logging.info(vectorCiaPerson.generateAnswer(ask))
        logging.info("==============================")
        ask = "¿Que compañías son similares, por su personas a ACME SA de CV?"
        logging.info(f'{ask}\n------------------------------')
        logging.info(vectorCiaPerson.generateAnswer(ask))
        logging.info("==============================")

    if logging.getLogger().level == logging.INFO:
        vectorPersonCia = VectorsPersonCia(neo4jdb)
        logging.info("===================================")
        logging.info(f'Contexto utilizado para Personas<->Compañías:\n{(vectorPersonCia.displayContext())}\n')
        logging.info("==============================")
        logging.info(
            f'Se genera el text embebido Compañías de acuerdo al contexto en los nodos de "Personas":{vectorPersonCia.generateTextEmbedding()}')
        logging.info("==============================\n  P R E G U N T A S")
        logging.info("==============================")
        ask = "¿Que persona es el director de la compañía ACME SA de CV?"
        logging.info(f'{ask}\n------------------------------')
        logging.info(vectorPersonCia.generateAnswer(ask))
        logging.info("==============================")
        ask = "¿Que persona es el contador de la compañía ACME SA de CV?"
        logging.info(f'{ask}\n------------------------------')
        logging.info(vectorPersonCia.generateAnswer(ask))
        logging.info("==============================")
        ask = "¿Que personas son similares, por su compañía a Diego Balli Armella?"
        logging.info(f'{ask}\n------------------------------')
        logging.info(vectorPersonCia.generateAnswer(ask))
        logging.info("==============================")

    logging.info('The bup-vector has finished')
