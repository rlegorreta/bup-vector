import os
import logging
from app import neo4jdb


# Open AI user prompt for all classes
def generateUserPrompt(question, context):
    return f"""
    The question is {question}
    Answer the question by using the provided information:
    {context}
    """


# This class is in charge to get the right answer from the openai chat with respect to the relationship
# between Persons.
#
class VectorsPersonPerson:
    def __init__(self, neo4j: neo4jdb.Neo4jDB):
        self.neo4j = neo4j
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.system_prompt = """
        You are an assistant that helps to generate text to form nice and human understandable answers based.
        The latest prompt contains the information, and you need to generate a human readable response based on the given information.
        Make the answer sound as a response to the question. Do not mention that you based the result on the given information.
        Do not add any additional information that is not explicitly provided in the latest prompt.
        I repeat, do not add any information that is not explicitly given.
        """

    # This is the 'context' that we define. It is used for two purpose
    # (a) Generate the embedding text (using open AI) in the 'Persona' nodes.
    # (b) Display the information.
    # note: We can use different context but for simplicity of the POC we use the same context.
    def displayContext(self):
        res = self.neo4j.run_query("""
        MATCH (p:Persona)
        MATCH (p)-[r:RELACION]-(t)
        WITH p, type(r) as type, COALESCE(r.tipo, "") as type_types, collect(t.nombre +" "+ t.apellidoPaterno +" "+ t.apellidoMaterno) as names
        WITH p, type +"<"+ type_types +">"+ ": " + reduce(s="", n IN names | s + n + ", ") as types
        WITH p, collect(types) as contexts
        WITH p, "Persona: "+ p.nombre +" "+ p.apellidoPaterno +" "+ p.apellidoMaterno +"\n    " +
                " Nació: " + p.fechaNacimiento +" " + p.estadoCivil + " género: " + p.genero + "\n" +  
                reduce(s="", c in contexts | s + substring(c, 0, size(c)-2) +"\n") as context
        RETURN context LIMIT 1
        """)['context'][0]

        return res

    def generateTextEmbedding(self):
        res = self.neo4j.run_query("""
        CALL apoc.periodic.iterate(
        'MATCH (p:Persona) RETURN id(p) AS id',
        'MATCH (p:Persona)
         WHERE id(p) = id
         MATCH (p)-[r:RELACION]-(t)
         WITH p, type(r) as type, COALESCE(r.tipo, "") as type_types, collect(t.nombre +" "+ t.apellidoPaterno +" "+ t.apellidoMaterno) as names
         WITH p, type + "<" + type_types + ">" + ": " + reduce(s="", n IN names | s + n + ", ") as types
         WITH p, collect(types) as contexts
         WITH p, "Persona: "+ p.nombre +" "+ p.apellidoPaterno +" "+ p.apellidoMaterno +"\n    " +
                " Nació: " + p.fechaNacimiento +" " + p.estadoCivil + " género: " + p.genero + "\n" +     
                 reduce(s="", c in contexts | s + substring(c, 0, size(c)-2) +"\n") as context
         CALL apoc.ml.openai.embedding([context], $apiKey) YIELD embedding
         SET p.embedding = embedding',
         {batchSize:1, retries:3, params: {apiKey: $apiKey}})
        """, {'apiKey': self.openai_api_key})['errorMessages'][0]

        return res

    # Before asking LLM to generate answers, we define and intelligent search tool that will provide relevant
    # information based on the vector similarity search. We embed the user input and use the cosine similarity
    # to identify relevant nodes. With graph, we can decide the type of information to retrieve an provide as
    # context. For this POC we return the same context information that was used to generate text embeddings along
    # with similar Persona information
    def retrieveContext(self, question, k=3):
        data = self.neo4j.run_query("""
        // retrieve the embedding query of the question
        CALL apoc.ml.openai.embedding([$question], $apiKey) YIELD embedding
        // match relevant Persons
        MATCH (p:Persona)
        WITH p, gds.similarity.cosine(embedding, p.embedding) AS score
        ORDER BY score DESC
        // limit the number of relevant persons
        LIMIT toInteger($k)
        // retrieve Graph context
        MATCH (p)--()--(p1:Persona)
        WITH p,p1, count(*) AS count
        ORDER BY count DESC
        WITH p, apoc.text.join(collect(p1.nombre +" "+ p1.apellidoPaterno +" "+ p1.apellidoMaterno)[..3], ", ") AS similarPersons
        MATCH (p)-[r:RELACION]-(t)
        WITH p, similarPersons, type(r) as type, COALESCE(r.tipo, "") as type_types, collect(t.nombre +" "+ t.apellidoPaterno +" "+ t.apellidoMaterno) as names
        WITH p, similarPersons, type +"<"+ type_types +">"+": " + reduce(s="", n IN names | s + n + ", ") as types
        WITH p, similarPersons, collect(types) as contexts
        WITH p, "Persona: "+ p.nombre +" "+ p.apellidoPaterno +" "+ p.apellidoMaterno +"\n    " +
                " Nació: " + p.fechaNacimiento +" " + p.estadoCivil + " género: " + p.genero + "\n" +    
                reduce(s="", c in contexts | s + substring(c, 0, size(c)-2) +"\n") +
                "Personas similares:" + similarPersons AS context
        RETURN context
        """,
                                    {'question': question, 'k': k, 'apiKey': self.openai_api_key},
                                    )

        return data["context"].to_list()

    # Finally we can define the function that takes a user question and returns an answer
    def generateAnswer(self, question):
        # Retrieve the context
        context = self.retrieveContext(question)
        # Print context
        logging.info("Context")
        for c in context:
            logging.info(c)
        logging.info("-----------------")
        # Generate the answer
        response = self.neo4j.run_query("""
        CALL apoc.ml.openai.chat([{role:'system', content: $system},{role:'user', content:$user}], $apiKey) YIELD value
        RETURN value.choices[0].message.content AS answer
        """, {'system': self.system_prompt,
              'user': generateUserPrompt(question, context),
              'apiKey': self.openai_api_key, }, )

        return response['answer'][0]
