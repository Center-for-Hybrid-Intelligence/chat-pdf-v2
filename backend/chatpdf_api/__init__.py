from flask_cors import CORS
from flask import Flask, jsonify, request, Response, stream_with_context
from .database import db
from .readpdf import read_from_url
from .readpdf import read_from_file
from .qa_tool import QaTool

import os
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:8080"}})

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
    try:
        data = request.get_json()
        namespace = data.keys()[0]
        formdata = data[namespace]
        if qa_tool.namespace is None:
            qa_tool.set_namespace(namespace)

        df = read_from_url(formdata['url'], formdata['author'], formdata['documentId'], namespace)
        qa_tool.loading_data_to_pinecone(df)
    except Exception as e:
        print(e)
    return "très bien"

@app.route('/api/ask-query/', methods=['POST', 'OPTIONS'])
def send_query():
    try:
        data = request.get_json()
        result = qa_tool(query=data['query'],top_closest=data['topClosest'])
        return jsonify(result)
    except Exception as e:
        return jsonify(e)
    
@app.route('/api/erase-all/', methods=['POST', 'OPTIONS'])
def erase_all():
    try:
        data = request.get_json()
        qa_tool.delete_all(data['namespace'])
    except Exception as e:
        return jsonify(e)

@app.route('/api/erase-all/', methods=['POST', 'OPTIONS'])
def erase_doc():
    try:
        data = request.get_json()
        qa_tool.erase_doc(data['documentId'], data['namespace'])
    except Exception as e:
        return jsonify(e)

        


