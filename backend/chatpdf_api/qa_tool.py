import os
from typing import Any
from dotenv import load_dotenv

load_dotenv()
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone

from tqdm.auto import tqdm
from uuid import uuid4

from langchain.vectorstores import Pinecone

from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

PINE_API_KEY = os.getenv('PINECONE_API_KEY')
YOUR_ENV = os.getenv('YOUR_ENV')

from langchain.text_splitter import RecursiveCharacterTextSplitter

import tiktoken
from .database import remove_document

from .database import add_document

pinecone.init(api_key=PINE_API_KEY, environment=YOUR_ENV)

class QaTool:
    def __init__(self, chunk_size=400, chunk_overlap=20, chain_type="stuff") -> None:
        self.chunk_overlap = None
        self.chunk_size = None
        self.tokenizer_name = 'cl100k_base'
        self.namespace = None
        self.chain_type = chain_type
        self.embedding_model = 'text-embedding-ada-002'
        self.llm_model = 'gpt-4'
        self.model_temperature = 0.0

        self.index_name = 'chatpdf-langchain-retrieval-agent'
        if self.index_name not in pinecone.list_indexes():
            # we create a new index
            pinecone.create_index(
                name=self.index_name,
                metric='dotproduct',
                dimension=1536
            )
        self.text_field = 'text'

    def tiktoken_len(self, text):
        tiktoken.encoding_for_model(self.llm_model)
        tokenizer = tiktoken.get_encoding(self.tokenizer_name)
        tokens = tokenizer.encode(
            text,
            disallowed_special=()
        )
        return len(tokens)

    def set_namespace(self, namespace):
        self.namespace = namespace

    def set_chunks(self, chunk_size, chunk_overlap):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def set_llm(self, llm='gpt-4', temperature=0.0):
        self.llm_model = llm
        self.model_temperature = temperature

    def loading_data_to_pinecone(self, data):
        # =============Warning to change if several indexes
        index = pinecone.GRPCIndex(self.index_name)  # we are connected to the pinecone index

        # INDEXING
        batch_limit = 100  # pinecone doesn't allow more than 100 vectors simultaneous upserting

        texts = []
        metadatas = []
        embed = OpenAIEmbeddings(
            model=self.embedding_model,
            openai_api_key=OPENAI_API_KEY)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self.tiktoken_len,
            separators=["\n\n", "\n", " ", ""]
        )
        print("Loading embeddings to Pinecone")
        for i, record in (data.iterrows()):
            # first get metadata fields for this record
            metadata = {
                'id': record['Id'],
                'title': record['Title'],
                'author': record['Author']
            }

            # now we create chunks from the record text
            record_texts = text_splitter.split_text(record['Summary'])

            # create individual metadata dicts for each chunk
            record_metadatas = [{
                "chunk": j, "text": text, **metadata
            } for j, text in enumerate(record_texts)]
            # append these to current batches
            if self.namespace is None:
                raise ValueError("Namespace not set")

            for record_text, record_metadata in zip(record_texts, record_metadatas):
                texts.append(record_text)
                metadatas.append(record_metadata)
                # if we have reached the batch_limit we can add texts
                if len(texts) >= batch_limit:
                    ids = [str(uuid4()) for _ in range(len(texts))]
                    embeds = embed.embed_documents(texts)
                    index.upsert(vectors=zip(ids, embeds, metadatas), namespace=self.namespace)
                    texts = []
                    metadatas = []

        if len(texts) > 0:
            ids = [str(uuid4()) for _ in range(len(texts))]
            embeds = embed.embed_documents(texts)

            index.upsert(vectors=zip(ids, embeds, metadatas), namespace=self.namespace)

    def delete_all(self):
        index = pinecone.GRPCIndex(self.index_name)  # we are connected to the pinecone index
        index.delete(delete_all=True, namespace=self.namespace)

    def erase_doc(self, document_id):
        remove_document(document_id=document_id)
        index = pinecone.GRPCIndex(self.index_name)  # we are connected to the pinecone index
        index.delete(ids=[document_id], namespace=self.namespace)

    def __call__(self, query, top_closest, filter=None) -> Any:
        print("Loading embeddings")
        embed = OpenAIEmbeddings(
            model=self.embedding_model,
            openai_api_key=OPENAI_API_KEY)
        print("Loading vectorstore")
        index = pinecone.Index(self.index_name)
        vectorstore = Pinecone(
            index, embed.embed_query, self.text_field, self.namespace
        )
        print("Loading LLM")
        llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name='gpt-4',
            temperature=0.0
        )
        print("Loading QA")
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type=self.chain_type,
            retriever=vectorstore.as_retriever(search_kwargs={"k": top_closest, "filter": filter }),
            return_source_documents=True,
            verbose=True
        )
        return qa({"query": query})

    def __repr__(self) -> str:
        return f"QaTool(chunk_size={self.chunk_size}, chunk_overlap={self.chunk_overlap}, chain_type={self.chain_type}), index_name={self.index_name}, namespace={self.namespace})"
