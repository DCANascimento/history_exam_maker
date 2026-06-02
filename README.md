git clone https://github.com/citiususc/Linguakit.git
cd Linguakit

sed -i "s/header '/response_header '/g" api/lib/linguakit_api.pm


## Dockerfile

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install core utilities, web frameworks, and dictionary unpackers
RUN apt-get update && apt-get install -y \
    perl \
    make \
    g++ \
    build-essential \
    libdancer2-perl \
    libdancer2-plugin-ajax-perl \
    libjson-perl \
    libplack-perl \
    libperlio-gzip-perl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /linguakit

# Copy files and run the native dictionary compilation
COPY . /linguakit
RUN make

EXPOSE 3000

# Continuous deployment engine hook
CMD ["plackup", "-Iapi/lib", "-p", "3000", "api/app-pt.pl"]



# ------------------------------------------------------------------------

cd ..

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# ---------------------------------------------------------------------------

## Method 1 

cd Method1

* Get the knowledge_base.txt
python3 data_generator.py

* Get more meaningful "quads"
python3 convert_to_quads.py

* Make questions
python3 question_generator.py

## Method 2

cd Method2

* Get the sentences
python3 sentence_extractor.py

* Generate questions
python3 sentence_quiz_generator.py