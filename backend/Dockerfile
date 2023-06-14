# use python container image
FROM python:3.8

# set the working directory of the image filesystem 
WORKDIR /app

# copy current directory to the working directory 
COPY . . 

# Install the python dependencies
RUN pip install -r requirements.txt
RUN pip install uwsgi

ENV DATABASE_URL='sqlite:///documents.db'
ENV OPENAI_API_KEY=API_KEY
ENV OPENAI_ORGANIZATION=org-3WL1stoahVKNtlth6bdytR9b
ENV PINECONE_API_KEY=73c332ac-3cdb-4cd4-bc07-d8ec7e5fa0b3
ENV YOUR_ENV=us-west4-gcp-free

# start the uWSGI
CMD ["uwsgi", "app.ini"]
