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
    namespace_name = db.Column(db.Text, nullable=False, unique=True)


class Document(db.Model):
    document_id = db.Column(db.Integer, primary_key=True)
    document_title = db.Column(db.Text, nullable=True)
    document_author = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    document_file = db.Column(db.Text, nullable=True)
    namespace_id = db.Column(db.String, db.ForeignKey('namespace.session_id'), nullable=False)

    def __repr__(self):
        return f'<Prompt {self.document_id}, created at {self.created_at}>'


class Session(db.Model):
    session_id = db.Column(db.String, primary_key=True, nullable=False)
    qa_tool = db.Column(DillObjectType)

    def __repr__(self):
        return f'<Session {self.session_id}>'


def add_document(document_id, document_title, document_author, document_file, namespace_name, session_id):
    document_id = document_id[6:]
    namespaces = Namespace.query.filter_by(session_id=session_id).first()
    print(namespaces)
    if namespaces is None:
        db.session.add(namespace := Namespace(namespace_name=namespace_name, session_id=session_id))
        db.session.commit()
    else:
        namespace = namespaces
    try:
        db.session.add(Document(document_id=int(document_id),
                                document_title=document_title,
                                document_author=document_author,
                                document_file=document_file,
                                namespace_id=namespace.session_id))
        db.session.commit()
    except IntegrityError:
        return "Document already exists"


def remove_document(document_id):
    Document.query.filter_by(document_id=document_id).delete()


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