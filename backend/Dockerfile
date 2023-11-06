# use python container image
FROM python:3.8

# set the working directory of the image filesystem 
WORKDIR /app

# copy current directory to the working directory 
COPY . . 

# Install the python dependencies
RUN pip install -r requirements.txt
RUN pip install uwsgi
RUN python3 -m load_dotenv load

ENV DATABASE_URL='sqlite:///site.db'
ENV OPENAI_API_KEY='insert_key'
ENV OPENAI_ORGANIZATION='insert_key'
ENV PINECONE_API_KEY='insert_key'
ENV YOUR_ENV='insert_key'

# start the uWSGI
CMD ["uwsgi", "app.ini"]
