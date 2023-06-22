from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.types import TypeDecorator, LargeBinary
import dill
db = SQLAlchemy()


class DillObjectType(TypeDecorator):
    impl = LargeBinary

    def process_bind_param(self, value, dialect):
        if value is not None:
            return dill.dumps(value)
        return None

    def process_result_value(self, value, dialect):
        if value is not None:
            return dill.loads(value)
        return None


class Namespace(db.Model):
    session_id = db.Column(db.String, db.ForeignKey('session.session_id'), nullable=False, primary_key=True)
    namespace_name = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    def __repr__(self):
        return f'<Namespace {self.namespace_name}>'


class Document(db.Model):
    document_id = db.Column(db.String, primary_key=True)
    document_title = db.Column(db.Text, nullable=True)
    document_author = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    document_file = db.Column(db.Text, nullable=True, unique=True)

class DocumentNamespace(db.Model):
    document_id = db.Column(db.String, db.ForeignKey('document.document_id'), nullable=False, primary_key=True)
    namespace_name = db.Column(db.String, db.ForeignKey('namespace.namespace_name'), nullable=False, primary_key=True)

    def __repr__(self):
        return f'<Prompt {self.document_id}, created at {self.created_at}>'


class Session(db.Model):
    session_id = db.Column(db.String, primary_key=True, nullable=False)
    qa_tool = db.Column(DillObjectType)

    def __repr__(self):
        return f'<Session {self.session_id}>'


def add_document(document_id, document_title, document_author, document_file, namespace_name, session_id):
    # Check if the namespace exists
    namespace = Namespace.query.filter_by(namespace_name=namespace_name, session_id=session_id).first()
    # If the namespace does not exist, create it
    if namespace is None:
        print("Creating a namespace")
        db.session.add(namespace := Namespace(namespace_name=namespace_name, session_id=session_id))
        db.session.commit()

    # Add the document to the database
    has_same_id, has_same_file = exists_document(document_id, document_file)
    if not has_same_id and not has_same_file:
        db.session.add(Document(document_id=document_id,
                                document_title=document_title,
                                document_author=document_author,
                                document_file=document_file))
        db.session.commit()
    else:
        print("Document already exists in the database")
        print(f"ID : {has_same_id}, content: {has_same_file}")
    if has_same_file:
        return Document.query.filter_by(document_file=document_file).first().document_id
def add_document_to_namespace(document_id, namespace_name, session_id):
    # Add the document to the namespace
    namespace = Namespace.query.filter_by(namespace_name=namespace_name, session_id=session_id).first()
    if not is_document_in_namespace(document_id, namespace_name):
        print("Adding document to the namespace")
        db.session.add(DocumentNamespace(document_id=document_id, namespace_name=namespace.namespace_name))
        db.session.commit()
        return True
    else:
        return False

def remove_document(document_id):
    Document.query.filter_by(document_id=document_id).delete()
    DocumentNamespace.query.filter_by(document_id=document_id).delete()
    db.session.commit()


def get_documents():
    documents = Document.query.all()
    result = []
    for document in documents:
        result.append((document.document_title, document.document_author))
    return result


def add_session(session_id, qa_tool):
    session = Session(session_id=session_id, qa_tool=qa_tool)
    db.session.add(session)
    db.session.commit()


def retrieve_session(session_id):
    session = Session.query.filter_by(session_id=session_id).first()
    if session is None:
        return None
    return session.qa_tool


def delete_session(session_id):
    Session.query.filter_by(session_id=session_id).delete()
    db.session.commit()

def update_session(session_id, qa_tool):
    session = Session.query.filter_by(session_id=session_id).first()
    session.qa_tool = qa_tool
    db.session.commit()

def exists_namespace(namespace_name):
    return Namespace.query.filter_by(namespace_name=namespace_name).first() is not None

def retrieve_namespace(namespace_name):
    # Get the most recent namespace with the given name
    return Namespace.query.filter_by(namespace_name=namespace_name).order_by(Namespace.created_at.desc()).first().session_id
def retrieve_documents(namespace_name):
    documents = Document.query.join(DocumentNamespace).filter_by(namespace_name=namespace_name).all()
    result = []
    for document in documents:
        result.append((document.document_title, document.document_author))
    return result

def exists_document(document_id, document_file):
    has_same_id = Document.query.filter_by(document_id=document_id).first() is not None
    has_same_file = Document.query.filter_by(document_file=document_file).first() is not None
    return has_same_id, has_same_file

def is_document_in_namespace(document_id, namespace_name):
    return DocumentNamespace.query.filter_by(document_id=document_id, namespace_name=namespace_name).first() is not None

def remove_document_from_namespace(document_id, namespace_name):
    DocumentNamespace.query.filter_by(document_id=document_id, namespace_name=namespace_name).delete()
    db.session.commit()