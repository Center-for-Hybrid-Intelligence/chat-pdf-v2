import numpy as np
from flask_cors import CORS
from flask import g, Flask, request, session
from .database import db, add_session, retrieve_session, delete_session, update_dialogue, update_session, exists_namespace, retrieve_namespace, retrieve_documents, remove_document, remove_document_from_namespace, add_document_to_namespace
from .readpdf import read_from_encode
from .qa_tool import QaTool
import json
from flask import Flask, request, Response, stream_with_context

import os
from dotenv import load_dotenv

import openai

load_dotenv()

app = Flask(__name__)
CORS(app)


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
    my_session = retrieve_session(session_id)
    if my_session is None or my_session.qa_tool is None:
        print("Creating new session")
        qa_tool = QaTool()
        add_session(session_id, qa_tool)
    else:
        qa_tool = my_session.qa_tool
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
    settings = request.form.get('settings')
    print(settings)
    settings = json.loads(settings)
    chunk_size = int(settings["chunk_size"])
    chunk_overlap = int(settings['chunk_overlap'])
    print(f'namespace: {namespace_name}')
    print(f"documentId: {request.form.get('documentId')}")
    print(f"author: {request.form.get('author')}")

    if not (file_id or file):
        # Check for an already existing namespace
        if namespace_name is None:
            return "Please provide a namespace", 401
        if not exists_namespace(namespace_name):
            return "Please provide a file or a document id", 401
        else:
            session_id = retrieve_namespace(namespace_name)
            qa_tool = retrieve_session(session_id).qa_tool
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
        qa_tool = retrieve_session(session_id).qa_tool
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
    if added:
        try:
            qa_tool.loading_data_to_pinecone(file_df)
        except Exception as e:
            remove_document_from_namespace(file_id, namespace_name)
            print(e)
            return "Error loading data to pinecone", 401
    # Update the session
    update_session(session['session_id'], qa_tool)
    print(qa_tool)
    g.qa_tool = qa_tool
    return f"Successfully loaded {file_id} to pinecone", 200

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
    print("Getting files")
    qa_tool = g.qa_tool
    print(f'namespace: {qa_tool.namespace}')
    documents = retrieve_documents(qa_tool.namespace)
    result = []
    for document in documents:
        result.append({"title": document.document_title,"author": document.document_author})
    return result
    return files, 200


@app.route('/api/send-message/', methods=['POST'])
def send_message():
    session_id = request.cookies.get('sessionID')

    # Check if session exists
    qa_tool = retrieve_session(session_id).qa_tool
    if qa_tool is None:
        return "Session not found", 401

    # Read the request body
    dialogue = request.get_json()
    print(dialogue)

    # Print request origin
    print(session_id)
    # Put the dialogue in the db
    update_dialogue(session_id, dialogue)
    return Response(status=200)

@app.route('/api/stream-updates/', methods=['GET'])
def stream_updates():
    # This command is executed when the send message request is over. It queries the tool and fetches the response
    session_id = request.cookies.get('sessionID')
    print(session_id)

    dialogue = json.loads(retrieve_session(session_id).dialogue)
    qa_tool = retrieve_session(session_id).qa_tool

    # TODO Query the tool and get the response

    # I leave the generator structure to be able to stream the response. However, I do not know how to do it with
    # langchain.
    #
    # def generate():
    #     counter = 0
    #     response = ""
    #     for answer in generator.send_request(dialogue):
    #         if "content" in answer.choices[0].delta.keys():
    #             content = answer.choices[0].delta.content
    #             yield content
    #             print(content)
    #             response += content
    #             counter += 1
    #             if counter % 10 == 0:
    #                 counter = 0
    #                 # Log the response
    #                 response = ""
    #         if "finish_reason" in answer.choices[0].delta.keys():
    #             break
    #
    # return Response(stream_with_context(generate()), content_type='text/event-stream')