# gg-project-master
Golden Globe Project Master


Before running:
pip install -r requirements.txt
python3 -m spacy download en_core_web_sm
python3 -m spacy download en_core_web_md


To run:
First, if you are trying to run the code on the 2015 set of tweets, then you should add the gg2015.json file to the folder of the project. 

Then, run the following in the terminal:

python3 gg_api.py <year> 
(gives human-readable code for 2013, 2015 and year specified)

python3 autograder.py <year>
(will give the autograder response for given year)



