############ IMPORTS ############
import numpy as np
from flask_cors import CORS
from flask import g, Flask, request, session
from .database import db, normalize_session_id, add_session, retrieve_session, delete_session, update_session, exists_namespace, retrieve_namespace, retrieve_documents, remove_document, remove_document_from_namespace, add_document_to_namespace
from .readpdf import read_from_encode
from .qa_tool import QaTool # Import tool from qa_tool.py
import json
import os
from dotenv import load_dotenv
import openai

########## SET ENVIRONMENT VARIABLES ##########
load_dotenv()

########## RUN LOCALLY ##########
from sqlalchemy import create_engine
engine = create_engine('sqlite:///site.db')

# check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

########## INITIALIZE FLASK ##########
app = Flask(__name__)
CORS(app, origins=['http://localhost:3053', 'http://localhost:8080', 'https://127.0.0.1:8080', r'^https://hybridintelligence.eu$', r'^https://www.hybridintelligence.eu$'])

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL") # "sqlite:///site.db" in .env file
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# initialize the app with Flask-SQLAlchemy
db.init_app(app)
with app.app_context():
    db.create_all()


app.config["SESSION_PERMANENT"] = False # If the session is not permanent, the session will be deleted when the browser is closed.
app.config["SESSION_TYPE"] = "sqlalchemy" # The session is stored in the database.

app.secret_key = "pietervandeawiff0000" # IS THIS NEEDED?

@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Auth-Token, Session'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
    response.headers['Access-Control-Allow-Origin'] = request.origin # '*'

    return response

#################### ROUTES ####################

########## INITIALIZE QATool ##########
@app.before_request
def initialize_qa_tool():
    if request.method == 'OPTIONS':
        return None
    session_id = request.cookies.get('sessionID')
    qa_tool = None
    if session_id is not None:
        print('32 ' + session_id)
        qa_tool = retrieve_session(session_id)
    if qa_tool is None:
        print("Creating new session")
        qa_tool = QaTool()
        session_id = normalize_session_id(session_id)
        add_session(session_id, qa_tool)
    session['session_id'] = session_id
    print(session)
    print(qa_tool)
    g.qa_tool = qa_tool

########### LOAD PDF ###########
@app.route('/api/load-pdf/', methods=['POST']) # First endpoint. This is where the pdf is loaded.
def load_pdf():
    qa_tool = g.qa_tool # Get the qa_tool from the global context
    print("Loading pdf")

    # Parse the request
    author = request.form.get('author')
    file_id = request.form.get('documentId')
    namespace_name = request.form.get('namespace')
    title = request.form.get('name')
    file = request.files['file']
    settings = request.form.get('settings')
    print(settings)

    settings = json.loads(settings) # Parse the settings
    chunk_size = int(settings["chunk_size"]) # Get the chunk size from the settings
    chunk_overlap = int(settings['chunk_overlap']) # Get the chunk overlap from the settings
    print(f'namespace: {namespace_name}')
    print(f"documentId: {request.form.get('documentId')}")
    print(f"author: {request.form.get('author')}")

    if not (file_id or file): # Check if the file id or the file is provided
        # Check for an already existing namespace
        if namespace_name is None:
            return "Please provide a namespace", 401
        if not exists_namespace(namespace_name):
            return "Please provide a file or a document id", 401
        else:
            session_id = retrieve_namespace(namespace_name)
            qa_tool = retrieve_session(session_id)
            update_session(session['session_id'], qa_tool)
            g.qa_tool = qa_tool
            return "Successfully retrieved session", 200

    # If the session id is used with a new namespace, throw an error asking to refresh the page
    if qa_tool.namespace is not None and qa_tool.namespace != namespace_name:
        print(qa_tool.namespace, namespace_name)
        return "You already created a namespace in the session, please refresh the page", 401

    # If the namespace is already used, retrieve the qa_tool from the database
    if qa_tool.namespace is None and exists_namespace(namespace_name):
        print("Found existing namespace, retrieving session")
        session_id = retrieve_namespace(namespace_name)
        qa_tool = retrieve_session(session_id)
        update_session(session['session_id'], qa_tool)
    #     Retrieve the files that are already in the namespace
        documents = retrieve_documents(namespace_name)

    # Update the qa_tool
    qa_tool.set_chunks(chunk_size, chunk_overlap)
    if qa_tool.namespace is None:
        qa_tool.set_namespace(namespace_name)
    update_session(session['session_id'], qa_tool)

    # Read the file and load it to pinecone
    file_df, identifier = read_from_encode(file, author, file_id, namespace_name, title, session['session_id'])
    file_id = identifier
    # Add the file to the namespace
    added = add_document_to_namespace(file_id, namespace_name, session['session_id'])
    if added: # If the file was added to the namespace, load it to pinecone
        try:
            qa_tool.loading_data_to_pinecone(file_df) # SEE FUNCTION IN qa_tool.py. This function loads the document to pinecone.
        except Exception as e:
            remove_document_from_namespace(file_id, namespace_name)
            print(e)
            return "Error loading data to pinecone", 401
    # Update the session
    update_session(session['session_id'], qa_tool)
    print(qa_tool)
    g.qa_tool = qa_tool
    return f"Successfully loaded {file_id} to pinecone", 200

########## ASK QUERY ##########
@app.route('/api/ask-query/', methods=['POST'])
def ask_query():
    qa_tool = g.qa_tool
    print(qa_tool)
    system_prompt = ''
    # Check that every file in the namespace is loaded to pinecone
    namespace_name = qa_tool.namespace
    documents = retrieve_documents(namespace_name)
    print(documents)
    for document in documents:
        if not document.document_id in qa_tool.loaded_documents: # If the document is not loaded to pinecone already??
    #       Load the document to pinecone
            file_df, identifier = read_from_encode(document.document_file, document.author, document.document_id, namespace_name, document.title, session['session_id'])
            try:
                qa_tool.loading_data_to_pinecone(file_df) # SEE FUNCTION in qa_tool.py. This function loads the document to pinecone.
            except Exception as e:
                return "Error loading data to pinecone", 401
            
            # NOTE: The data is only loaded to pinecone once. If the data is already loaded, it will not be loaded again.

    # Update the session
    update_session(session['session_id'], qa_tool, system_prompt)
    print(qa_tool)
    g.qa_tool = qa_tool

    data = request.get_json() # Get the query from the frontend. Could this be turned into a chatbot?
    if data['system_prompt']:
        system_prompt = data['system_prompt']
    print(system_prompt)
    settings = data['settings'] # Get the settings from the frontend
    llm_model = settings['llm_model'] # Get the llm model from the settings (gpt-3.5-turbo or gpt-4)
    llm_temperature = float(settings['llm_temperature']) # Get the llm temperature from the settings
    qa_tool.set_llm(llm_model, llm_temperature) # Set the llm model and temperature in the qa_tool
    top_closest = request.form.get('sources_number', 5) # Get the number of sources from the frontend
    try:
        print("Querying...")
        print(data['query']) # Simply the query string
        result = qa_tool(query=data['query'], top_closest=top_closest, system_prompt=system_prompt) ##### OBS: Calling the __call__ function in qa_tool.py, query is the question and top_closest is the number of sources.
        #print(result)
        print(f"GPT model used: {qa_tool.llm_model}")
        #qa_tool now returns a list of tuples: one for each document in the database
        #in the shape of (document_title, document_author, result)
        #result is exactly the same as before with 'result' and 'source_document' but now document wise.
    except openai.error.InvalidRequestError as e:
        print((f"Invalid request error: {e}"))
        error_message = str(e)
        return error_message, 401  # Invalid request, might have reached maximum tokens

    # OBS: This section is closely related to the dialogue flow in the gptPublic tool.
    response = []
    for res in result:
        # content = []
        document = res[2]
        # print(res[0])
        # print(document)
        # for doc in document['source_documents']:
        #     content.append((doc.page_content.replace('\n', "").replace('\t', ""), doc.metadata['title']))
        # response.append({"result": document['result'], "source_documents": content})
        response.append({"result": document})
    print(response)

    update_session(session['session_id'], qa_tool)
    g.qa_tool = qa_tool
    return response, 200


########## DELETE DOCUMENT ##########
@app.route('/api/erase-all/', methods=['DELETE'])
def erase_all():
    qa_tool = g.qa_tool
    print(qa_tool)
    qa_tool.delete_all()
    qa_tool.namespace = None

    del session['session_id']
    # Delete qa_tool from g
    del g.qa_tool

    return "Successfully deleted all data", 200


########## TEST ##########
@app.route('/api/hello/', methods=['GET'])
def hello():
    return "Hello world", 200


########## GET FILES ##########
@app.route('/api/get-files/', methods=['GET'])
def get_files():
    print("Getting files")
    qa_tool = g.qa_tool
    print(f'namespace: {qa_tool.namespace}')
    documents = retrieve_documents(qa_tool.namespace)
    result = []
    for document in documents:
        result.append({"title": document.document_title,"author": document.document_author})
    return result


@app.route('/api/set-system-prompt/', methods=['POST'])
def set_system_prompt():
    print('setting system prompt')
    system_prompt = request.form.get('system_prompt')
    print(system_prompt)
    update_session(session['session_id'], g.qa_tool, system_prompt)
    return 'Successfully replaced system prompt', 200
