# How to Setup

git clone https://github.com/citiususc/Linguakit.git
cd Linguakit

sed -i "s/header '/response_header '/g" api/lib/linguakit_api.pm

cd ..

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Two different ways to run questions

## Method 1 

cd Method1

* Get the knowledge_base.txt \\
python3 data_generator.py

* Get more meaningful "quads" \\
python3 convert_to_quads.py

* Make questions \\
python3 question_generator.py

## Method 2

cd Method2

* Get the sentences \\
python3 sentence_extractor.py

* Generate questions \\
python3 sentence_quiz_generator.py