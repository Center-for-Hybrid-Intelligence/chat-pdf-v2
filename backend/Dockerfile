# use python container image
FROM python:3.8

# set the working directory of the image filesystem 
WORKDIR /app

# copy current directory to the working directory 
COPY . . 

# Install the python dependencies
RUN pip install -r requirements.txt
RUN pip install uwsgi

ENV DATABASE_URL='sqlite:///site.db'
ENV OPENAI_API_KEY=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
ENV OPENAI_ORGANIZATION=org-3WL1stoahVKNtlth6bdytR9b
ENV PINECONE_API_KEY=e469bfb4-68de-4520-85eb-4c295b95b446
ENV YOUR_ENV=us-west4-gcp-free

# start the uWSGI
CMD ["uwsgi", "app.ini"]
