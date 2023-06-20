import os
from typing import Any
from dotenv import load_dotenv

load_dotenv()

from datasets import load_dataset

from getpass import getpass
from langchain.embeddings.openai import OpenAIEmbeddings
import pinecone

from tqdm.auto import tqdm
from uuid import uuid4

from langchain.vectorstores import Pinecone

from langchain.chat_models import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from langchain.chains import RetrievalQA

from langchain.agents import Tool
from langchain.agents import initialize_agent

OPENAI_API_KEY=os.getenv('OPENAI_API_KEY')

PINE_API_KEY = os.getenv('PINECONE_API_KEY')
YOUR_ENV = os.getenv('YOUR_ENV')


from langchain.chains import RetrievalQAWithSourcesChain



from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.text_splitter import CharacterTextSplitter

import tiktoken

from .database import remove_document

from .database import add_document


class QaTool:
    def __init__(self,chunk_size=400, chunk_overlap = 20, chain_type = "stuff") -> None:
        tiktoken.encoding_for_model('gpt-4')
        self.tokenizer = tiktoken.get_encoding('cl100k_base')
        self.namespace = None
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=self.tiktoken_len,
            separators=["\n\n", "\n", " ", ""]  
        )

        self.chain_type = chain_type

        self.embed = OpenAIEmbeddings(model='text-embedding-ada-002',openai_api_key=OPENAI_API_KEY)
        pinecone.init(api_key=PINE_API_KEY,environment=YOUR_ENV)

        self.index_name='chatpdf-langchain-retrieval-agent'
        self.text_field = 'text'

        self.index = pinecone.Index(self.index_name)
        self.vectorstore = None


        self.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name='gpt-4',
            temperature=0.0
        )

    def tiktoken_len(self,text):
        tokens = self.tokenizer.encode(
            text,
            disallowed_special=()
        )
        return len(tokens)


    def set_namespace(self, namespace):
        self.namespace = namespace
        self.vectorstore = Pinecone(
            self.index, self.embed.embed_query, self.text_field, self.namespace
        )

    def set_chunks(self, chunk_size, chunk_overlap):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=self.tiktoken_len,
            separators=["\n\n", "\n", " ", ""]  
        )

    def set_llm(self, llm='gpt-4', temperature=0.0):
        self.llm = ChatOpenAI(
            openai_api_key=OPENAI_API_KEY,
            model_name=llm,
            temperature=temperature
        )

    

    def loading_data_to_pinecone(self, data):
        #=============Warning to change if several indexes
        if self.index_name not in pinecone.list_indexes():
            #we create a new index
            pinecone.create_index(
                name=self.index_name,
                metric='dotproduct',
                dimension=1536
            )

        index = pinecone.GRPCIndex(self.index_name) #we are connected to the pinecone index


        #INDEXING
        batch_limit = 100 #pinecone doesn't allow more than 100 vectors simultaneous upserting

        texts =[]
        metadatas =[]

        for i, record in tqdm(data.iterrows(), total=len(data)):        
            #first get metadata fields for this record
            metadata = {
                'id': record['Id'],
                'title': record['Title'],
                'author': record['Author']
            }

            # now we create chunks from the record text
            record_texts = self.text_splitter.split_text(record['Summary'])

            # create individual metadata dicts for each chunk
            record_metadatas = [{
                "chunk": j, "text": text, **metadata
            } for j, text in enumerate(record_texts)]
            # append these to current batches
            for record_text, record_metadata in zip(record_texts, record_metadatas):
                texts.append(record_text)
                metadatas.append(record_metadata)
                # if we have reached the batch_limit we can add texts
                if len(texts) >= batch_limit:
                    ids = [str(uuid4()) for _ in range(len(texts))]
                    embeds = self.embed.embed_documents(texts)
                    index.upsert(vectors=zip(ids,embeds,metadatas))
                    texts = []
                    metadatas = []

        if len(texts) > 0:
            ids = [str(uuid4()) for _ in range(len(texts))]
            embeds = self.embed.embed_documents(texts)
            index.upsert(vectors=zip(ids,embeds,metadatas),namespace=self.namespace)

    def delete_all(self):
        self.index.delete(delete_all='true', namespace=self.namespace)
    
    def erase_doc(self, document_id):
        remove_document(document_id=document_id)
        self.index.delete(ids=[document_id], namespace=self.namespace)


    def __call__(self, query, top_closest) -> Any:
        qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type=self.chain_type,
            retriever=self.vectorstore.as_retriever(search_kwargs = {"k":top_closest}),
            return_source_documents=True
        )
        return qa({"query": query})

