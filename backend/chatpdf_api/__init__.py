import numpy as np
from flask_cors import CORS
from flask import Flask, jsonify, request, Response, stream_with_context
from .database import db
from .readpdf import read_from_encode
from .qa_tool import QaTool
import json

import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "https://hybridintelligence.eu/chat-pdf/*"}})

app.config['CORS_HEADERS'] = 'Content-Type'

# check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# initialize the app with Flask-SQLAlchemy
db.init_app(app)
with app.app_context():
    db.create_all()

qa_tool = QaTool()
@app.route('/api/load-pdf/', methods=['POST', 'OPTIONS'])
def load_pdf():
    author = request.form.get('author')
    file_id = request.form.get('documentId')
    namespace = request.form.get('namespace')
    title = request.form.get('name')
    file = request.files['file']
    if not (author and file_id and namespace and file):
        return "Missing file or fileInfo", 401

    if qa_tool.namespace is None:
        qa_tool.set_namespace(namespace)
    try:
        df = read_from_encode(file, author, file_id, namespace, title)
    except Exception as e:
        raise e
        return "Bad request", 402

    qa_tool.loading_data_to_pinecone(df)
    return f"Successfully loaded {file_id} to pinecone", 200

@app.route('/api/ask-query/', methods=['POST'])
def ask_query():
    data = request.get_json()
    print(data)
    top_closest = 5
    result = qa_tool(query=data['query'],top_closest=top_closest)
    print(result.keys())
    content = []
    for doc in result['source_documents']:
        content.append((doc.page_content, doc.metadata['title']))
    response = {"result": result['result'], "source_documents": content}
    return response, 200

    
@app.route('/api/erase-all/', methods=['GET'])
def erase_all():
    qa_tool.delete_all()
    qa_tool.namespace = None
    return "Successfully deleted all data", 200

@app.route('/api/hello/', methods=['GET'])
def hello():
    print("Je suis la")
    return "Hello world", 200
        


