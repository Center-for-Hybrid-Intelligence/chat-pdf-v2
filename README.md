# Chat-PDF

This repository is meant to be the summarizer of PDFs of the Center for Hybrid Intelligence. You can upload any number of PDFs, which are chunked using OpenAI's ADA model. It is then possible to query the document in order to get information out of it.

## Frontend
The frontend uses Vue Js and is composed of two views, one landing page and one query page.

## Backend
The backend is a Flask RestAPI with 4 endpoints:
/load-pdf/ to load the pdfs into the app and chunk them.
/ask-query/ to query the database and ask a question.
/erase-all/, automatically triggered when leaving the querying page. For now, the vector data is not stored anywhere.

## How to use?
Locally, you need nodeJs and Python. 
The deployment package is specific to the architecture of the hybrid intelligence servers.
