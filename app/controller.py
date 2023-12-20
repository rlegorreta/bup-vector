from app import app
from flask import request, jsonify, render_template
from app import neo4jdb
from app import vectorpersoncia
from app import vectorpersonperson
from app import vectorciaperson
from app import vectorciacia


@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/api/v1/bupvector/generate', methods=['GET'])
def api_generate_person_cia_embedded():
    neo4jdb_ = neo4jdb.Neo4jDB()
    vectors_person_cia = vectorpersoncia.VectorsPersonCia(neo4jdb_)
    vectors_person_cia.generateTextEmbedding()
    vectors_person_person = vectorpersonperson.VectorsPersonPerson(neo4jdb_)
    vectors_person_person.generateTextEmbedding()
    vectors_cia_person = vectorciaperson.VectorsCiaPerson(neo4jdb_)
    vectors_cia_person.generateTextEmbedding()
    vectors_cia_cia = vectorciacia.VectorsCiaCia(neo4jdb_)

    return vectors_cia_cia.generateTextEmbedding()


@app.route('/api/v1/bupvector/vectorpersoncia/ask', methods=['GET'])
def api_ask_person_cia():
    params = request.args
    question = params.get('question')
    if question is not None:
        neo4jdb_ = neo4jdb.Neo4jDB()
        vectors = vectorpersoncia.VectorsPersonCia(neo4jdb_)
        return vectors.generateAnswer(question)

    return 'no question found'


@app.route('/api/v1/bupvector/vectorpersonperson/ask', methods=['GET'])
def api_ask_person_person():
    params = request.args
    question = params.get('question')
    if question is not None:
        neo4jdb_ = neo4jdb.Neo4jDB()
        vectors = vectorpersonperson.VectorsPersonPerson(neo4jdb_)
        return vectors.generateAnswer(question)

    return 'no question found'


@app.route('/api/v1/bupvector/vectorciaperson/ask', methods=['GET'])
def api_ask_cia_person():
    params = request.args
    question = params.get('question')
    if question is not None:
        neo4jdb_ = neo4jdb.Neo4jDB()
        vectors = vectorciaperson.VectorsCiaPerson(neo4jdb_)
        return vectors.generateAnswer(question)

    return 'no question found'


@app.route('/api/v1/bupvector/vectorciacia/ask', methods=['GET'])
def api_ask_cia_cia():
    params = request.args
    question = params.get('question')
    if question is not None:
        neo4jdb_ = neo4jdb.Neo4jDB()
        vectors = vectorciacia.VectorsCiaCia(neo4jdb_)
        return vectors.generateAnswer(question)

    return 'no question found'
