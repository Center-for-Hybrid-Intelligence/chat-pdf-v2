from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text, func

db = SQLAlchemy()

class Namespace(db.Model):
    namespace_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    namespace_name = db.Column(db.Text, nullable=False, unique=True)

class Document(db.Model):
    document_id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True),
                            server_default=func.now())
    document_file = db.Column(db.Text, nullable=True)
    namespace_id = db.Column(db.Integer, db.ForeignKey('namespace.namespace_id'), nullable=False)
    
    def __repr__(self):
        return f'<Prompt {self.document_id}, created at {self.created_at}>'
    
def add_document(document_id, document_file, namespace_name):
    namespaces = Namespace.query.filter_by(namespace_name = namespace_name).first()
    if namespaces is None:
        db.session.add(namespace := Namespace(namespace_name = namespace_name))
        db.session.commit()
    else:
        namespace = namespaces
    db.session.add(Document(document_id=document_id, document_file=document_file, namespace_id=namespace.namespace_id))
    db.session.commit()

def remove_document(document_id):
    Document.query.filter_by(document_id = document_id).delete()
