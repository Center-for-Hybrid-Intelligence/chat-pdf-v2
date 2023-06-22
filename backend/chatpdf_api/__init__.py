import numpy as np
from flask_cors import CORS
from flask import g, Flask, request, session
from .database import db, add_session, retrieve_session, delete_session, update_session, exists_namespace, retrieve_namespace, retrieve_documents, remove_document
from .readpdf import read_from_encode
from .qa_tool import QaTool
import json

import os
from dotenv import load_dotenv

import openai

load_dotenv()

app = Flask(__name__)
CORS(app)#, resources={r"/api/*": {"origins": "https://hybridintelligence.eu"}})


# check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# initialize the app with Flask-SQLAlchemy
db.init_app(app)
with app.app_context():
    db.create_all()


app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "sqlalchemy"

app.secret_key = "pietervandeawiff0000"

@app.after_request
def add_header(response):
#     response.headers['Access-Control-Allow-Origin'] = 'https://hybridintelligence.eu'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Auth-Token'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST'
    return response

@app.before_request
def initialize_qa_tool():
    if request.method == 'OPTIONS':
        return None
    session_id = request.cookies.get('sessionID')
    print(session_id)
    qa_tool = retrieve_session(session_id)
    if qa_tool is None:
        print("Creating new session")
        qa_tool = QaTool()
        add_session(session_id, qa_tool)
    session['session_id'] = session_id
    print(session)
    print(qa_tool)
    g.qa_tool = qa_tool

@app.route('/api/load-pdf/', methods=['POST'])
def load_pdf():
    qa_tool = g.qa_tool
    print("Loading pdf")
    # Parse the request
    author = request.form.get('author')
    file_id = request.form.get('documentId')
    namespace_name = request.form.get('namespace')
    title = request.form.get('name')
    file = request.files['file']
    settings = json.loads(request.form.get('settings'))
    chunk_size = int(settings["chunk_size"])
    chunk_overlap = int(settings['chunk_overlap'])
    print(f'namespace: {namespace_name}')
    print(f"documentId: {request.form.get('documentId')}")

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

    if not (author and file_id and namespace_name and file):
        return "Missing file or fileInfo", 401

    # Update the qa_tool
    qa_tool.set_chunks(chunk_size, chunk_overlap)
    if qa_tool.namespace is None:
        qa_tool.set_namespace(namespace_name)

    # Read the file and load it to pinecone
    try:
        file_df = read_from_encode(file, author, file_id, namespace_name, title, session['session_id'])
    except ValueError:
        print("The document was already in the database")
    try:
        qa_tool.loading_data_to_pinecone(file_df)
    except Exception as e:
        remove_document(file_id)
        return "Error loading data to pinecone", 401
    # Update the session
    update_session(session['session_id'], qa_tool)
    print(qa_tool)
    g.qa_tool = qa_tool
    return f"Successfully loaded {file_id} to pinecone", 200

@app.route('/api/ask-query/', methods=['POST'])
def ask_query():
    qa_tool = g.qa_tool
    print(qa_tool)

    data = request.get_json()
    settings = data['settings']
    llm_model = settings['llm_model']
    llm_temperature = float(settings['llm_temperature'])
    qa_tool.set_llm(llm_model, llm_temperature)
    top_closest = request.form.get('sources_number', 5)
    docs = database.get_documents()
    results = []
    for doc in docs:
        try:
            print("Querying...")
            results.append(qa_tool(query=data['query'],
                                   top_closest=top_closest, 
                                   filter={"Title":{"eq": doc.document_title},
                                           "Auhtor":{"eq": doc.document_author},}))
        except openai.error.InvalidRequestError as e:
            print((f"Invalid request error: {e}"))
            error_message = str(e)
            return error_message, 401 #Invalid request, might have reached maximum tokens
    responses = []
    for result in results:
        print(result.keys())
        content = []
        for doc in result['source_documents']:
            content.append((doc.page_content.replace('\n', "").replace('\t', ""), doc.metadata['title']))
        response = {"result": result['result'], "source_documents": content}
        print(content)
        update_session(session['session_id'], qa_tool)
        g.qa_tool = qa_tool
        responses.append(response)
    final_responce = zip(docs, responses) #docs : the title and author of the document, responses : the result of the query and the source documents
    return final_responce, 200

    
@app.route('/api/erase-all/', methods=['GET'])
def erase_all():
    qa_tool = g.qa_tool
    print(qa_tool)
    qa_tool.delete_all()
    qa_tool.namespace = None

    del session['session_id']
    # Delete qa_tool from g
    del g.qa_tool

    return "Successfully deleted all data", 200

@app.route('/api/hello/', methods=['GET'])
def hello():
    return "Hello world", 200


@app.route('/api/get-files/', methods=['GET'])
def get_files():
    qa_tool = g.qa_tool
    print(qa_tool)
    files = retrieve_documents(qa_tool.namespace)
    return files, 200