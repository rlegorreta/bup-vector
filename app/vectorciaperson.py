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
# Companies and Personas.
#
class VectorsCiaPerson:
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
    # (a) Generate the embedding text (using open AI) in the 'Compania' nodes.
    # (b) Display the information.
    # note: We can use different context but for simplicity of the POC we use the same context.
    def displayContext(self):
        res = self.neo4j.run_query("""
        MATCH (c:Compania)
        MATCH (c)-[r:TRABAJA]-(t)
        WITH c, type(r) as type, COALESCE(r.puesto, "") as position_types, collect(t.nombre +" "+ t.apellidoPaterno +" "+ t.apellidoMaterno) as names
        WITH c, type +"<"+ position_types +">"+ ": " + reduce(s="", n IN names | s + n + ", ") as types
        WITH c, collect(types) as contexts
        WITH c, "Compañía: "+ c.nombre + "\n" +
                " Negocio: " + c.negocio + "\n" +  
                reduce(s="", c in contexts | s + substring(c, 0, size(c)-2) +"\n") as context
        RETURN context LIMIT 1
        """)['context'][0]

        return res

    def generateTextEmbedding(self):
        res = self.neo4j.run_query("""
        CALL apoc.periodic.iterate(
        'MATCH (c:Compania) RETURN id(c) AS id',
        'MATCH (c:Compania)
         WHERE id(c) = id
         MATCH (c)-[r:TRABAJA]-(t)
         WITH c, type(r) as type, COALESCE(r.puesto, "") as position_types, collect(t.nombre +" "+ t.apellidoPaterno +" "+ t.apellidoMaterno) as names
         WITH c, type + "<" + position_types + ">" + ": " + reduce(s="", n IN names | s + n + ", ") as types
         WITH c, collect(types) as contexts
         WITH c, "Compañía: "+ c.nombre + "\n" +
                 " Negocio: " + c.negocio + "\n" +    
                 reduce(s="", c in contexts | s + substring(c, 0, size(c)-2) +"\n") as context
         CALL apoc.ml.openai.embedding([context], $apiKey) YIELD embedding
         SET c.embeddingPersons = embedding',
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
        // match relevant Companies
        MATCH (c:Compania)
        WHERE COALESCE(c.embeddingPersons, '') <> ''
        WITH c, gds.similarity.cosine(embedding, c.embeddingPersons) AS score
        ORDER BY score DESC
        // limit the number of relevant companies
        LIMIT toInteger($k)
        // retrieve Graph context
        MATCH (c)--()--(c1:Compania)
        WITH c,c1, count(*) AS count
        ORDER BY count DESC
        WITH c, apoc.text.join(collect(c1.nombre)[..3], ", ") AS similarCompanies
        MATCH (c)-[r:TRABAJA]-(t)
        WITH c, similarCompanies, type(r) as type, COALESCE(r.puesto, "") as position_types, collect(t.nombre +" "+ t.apellidoPaterno +" "+ t.apellidoMaterno) as names
        WITH c, similarCompanies, type +"<"+ position_types +">"+": " + reduce(s="", n IN names | s + n + ", ") as types
        WITH c, similarCompanies, collect(types) as contexts
        WITH c, "Compañía: "+ c.nombre +"\n" +
                 " Negocio: " + c.negocio + "\n" +    
                reduce(s="", c in contexts | s + substring(c, 0, size(c)-2) +"\n") +
                "Compañías similares:" + similarCompanies AS context
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
        logging.info("--------------------")
        # Generate the answer
        response = self.neo4j.run_query("""
        CALL apoc.ml.openai.chat([{role:'system', content: $system},{role:'user', content:$user}], $apiKey) YIELD value
        RETURN value.choices[0].message.content AS answer
        """, {'system': self.system_prompt,
              'user': generateUserPrompt(question, context),
              'apiKey': self.openai_api_key, }, )

        return response['answer'][0]
