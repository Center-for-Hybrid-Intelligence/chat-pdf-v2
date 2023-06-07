# use python container image
FROM python:3.8

# set the working directory of the image filesystem 
WORKDIR /app

# copy current directory to the working directory 
COPY . . 

# Install the python dependencies
RUN pip install -r requirements.txt
RUN pip install uwsgi

ENV DATABASE_URL='sqlite:///requests.db'
ENV OPENAI_API_KEY=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
ENV OPENAI_ORGANIZATION=org-3WL1stoahVKNtlth6bdytR9b

# start the uWSGI
CMD ["uwsgi", "app.ini"]
