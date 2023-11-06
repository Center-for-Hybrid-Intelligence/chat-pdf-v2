# Chat-PDF

This repository is meant to be the summarizer of PDFs of the Center for Hybrid Intelligence. You can upload any number of PDFs, which are chunked using OpenAI's ADA model. It is then possible to query the document in order to get information out of it.

## Frontend

The frontend uses Vue Js and is composed of two views, one landing page and one query page.

## Backend

The backend is a Flask RestAPI with 3 endpoints:
/load-pdf/ to load the pdfs into the app and chunk them.
/ask-query/ to query the database and ask a question.
/erase-all/, automatically triggered when leaving the querying page. For now, the vector data is not stored anywhere.

Outside the app, UWSGI is loaded on docker and handles multiple instances for us.
The python app is situated in the chatpdf_api folder, and the files around it are here to parametrize it.

The Dockerfile manages the docker container, while the app.ini file manages the UWSGI app.

In the app.ini file, several threads and processes are allowed, and it is very easy to scale them up by just changing the configuration numbers.

## Debug environment

### Backend

Go to the backend folder 

```bash
cd backend
```

and run

in unix:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

in windows:

```bash
python -m venv venv
./venv/Scripts/Activate.ps1
pip install requirements.txt
```

Rename the file .env.template in .env and fill it with your API Keys. Do not add the file to git.

and then, to run the backend:

```python
python wsgi.py
```

copy the untracked (secret) `.env` file into `./backend` 

### Frontend

Go to the frontend folder (in a new terminal) 

```bash
cd frontend
```

and run

```bash
npm install
```

and then to run the frontend:

```bash
npm start
```

## Deployment environment

When the project is cloned on the server, change the variable names in the backend/Dockerfile with yours. Do not push them online.

To deploy the project, on the server, run the following command, in the root folder of the repository:

```bash
sudo docker-compose -f docker-compose-prod.yml -p chatpdf up --build -d
```

This will create the docker containers for the frontend and the backend and create a GPT network to link them.
On vm-7, for some reason, the network does not link internet automatically. It can be necessary to link them to the default bridge network in that case:

```bash
sudo docker network connect bridge backend-chatpdf
```

To access the logs of the containers, you can run

```bash
sudo docker logs backend-chatpdf
```

or

```bash
sudo docker logs frontend-chatpdf
```
