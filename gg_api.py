'''Version 0.35'''
import json
from collections import Counter
import re
import pprint
import spacy
import operator
sp = spacy.load('en_core_web_sm')

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best motion picture - comedy or musical', 'best performance by an actress in a motion picture - comedy or musical', 'best performance by an actor in a motion picture - comedy or musical', 'best animated feature film', 'best foreign language film', 'best performance by an actress in a supporting role in a motion picture', 'best performance by an actor in a supporting role in a motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best television series - comedy or musical', 'best performance by an actress in a television series - comedy or musical', 'best performance by an actor in a television series - comedy or musical', 'best mini-series or motion picture made for television', 'best performance by an actress in a mini-series or motion picture made for television', 'best performance by an actor in a mini-series or motion picture made for television', 'best performance by an actress in a supporting role in a series, mini-series or motion picture made for television', 'best performance by an actor in a supporting role in a series, mini-series or motion picture made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']

def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    tweet_arr = read_data(year)
    Dict = {}
    for tweet in tweet_arr:
        if re.search('(next year|Next year|last year|Last year)', tweet) is None:
            if re.search('(host|hosts|hosting|hosted)', tweet) is not None:
                t = sp(tweet)
                for person in t.ents:
                    if person.label_ == "PERSON":
                        if person.text not in ["Golden Globes", "goldenglobes", "GoldenGlobes", "Golden globes", "golden globes"]:
                            poss_host = person.text.lower()
                            if poss_host not in Dict:
                                Dict[poss_host] = 1
                            else:
                                Dict[poss_host] += 1
    sorted_dict = sorted([[value,key] for (key,value) in Dict.items()])[-5:] #this line changes dictionary into array format and orders into ascending order
    final_hosts = sorted_dict.copy()
    for i in sorted_dict[:-1]:
        try:
            i[1].index(" ")
        except ValueError:
            first_name_count = i[0]
            final_hosts.remove(i)
            for j in sorted_dict[1:]:
                try:
                    space = j[1].index(" ")
                    if j[1][:space] == i[1]:
                        j[0] += first_name_count
                except ValueError:
                    pass
    if final_hosts[-2][0] / final_hosts[-1][0] < 0.5:
        hosts = [final_hosts[-1][1]]
    else:
        hosts = [final_hosts[-1][1], final_hosts[-2][1]]

    return hosts

def get_awards(year):
    '''Awards is a list of strings. Do NOT change the name
    of this function or what it returns.'''
    # Your code here
    return awards

def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    # Your code here
    return nominees

def get_winner(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    return winners

def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''
    #how to let TV stand for television?
    #in host-> one dict w/ possible hosts and count
    #for you-> for each award create a dict with list of possible presenters and counts
    #Line 7942 in 2020 json-> Jason Momoa, Zoë Kravitz
    # Your code here
        					#if word == "motion" or "picture":
    						#split_award.remove(word)
    GlobalDict = {} #for award corresponding to presenters
    tweet_arr = read_data(year)
    #tweet_arr = ["fashion and fitness top story: @oscardelarenta: 'golden girl. Sandra Bullock lights up the night presenting best motion picture, drama at the 77th annual #goldenglobes in a custom ochre silk moiré faille gown. photograp… https://t.co/ewdirnwuxw, see more https://t.co/2bef4kyiud"]
    #'best television series - musical or comedy', 
    my_test_awards = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']
    television_syn = ["television", "tv", "tv series", "television series"]
    motion_picture = ["motion", "picture,", "movie", "film", "Motion", "Picture", "Movie", "Film"]
    presenters = {}
    remove = ["or", "-", "by", "an", "in", "a"]
    #Dict = {}
    with open("myfile2.txt", "w", encoding='utf-8') as f: 
	    for award in my_test_awards:
	    	Dict = {}
	    	for tweet in tweet_arr: #tweet in tweet_arr
	    		#check any (tv, television series) before all
	    		#tweet = tweet.lower()
	    		split_award = award.split() #check for this array if television is in this array-> then add other words 
	    		for word in remove:
		    		try:
		    			split_award.remove(word)
		    		except ValueError:
		    			pass
	    		#print(split_award)
	    		extra_split = []
	    		for word in split_award:
	    			extra_split.append(word[0].upper()+word[1:])
	    		if re.search('(next year|last year|representation)', tweet) is None:
	    			if re.search('(present|presented|gave the award|introduce|give|read)', tweet) is not None:
	    				#print(tweet)
	    				f.write(tweet)
	    				f.write("\n")
	    				#for word in split_award:
	    					#if word == "television":
    					if "television" in award:
    						split_award.remove("television")
    						if any([kw in tweet for kw in television_syn]):
    							#print(tweet) #it's good here!
    							if all([kw in tweet for kw in split_award]) or all([kw in tweet for kw in extra_split]): #includes television
    								#print(tweet) 
    								t = sp(tweet)
    								for person in t.ents:
    									if person.label_ == "PERSON":
    										if person.text not in ["Golden Globes", "goldenglobes", "GoldenGlobes", "Golden globes", "golden globes"]:
    											poss_host = person.text.lower()
    											if poss_host not in Dict:
    												Dict[poss_host] = 1
    											else:
    												Dict[poss_host] += 1
	    				#for word in split_award:
	    					#if word == "motion" or word == "picture":
    					if "motion picture" in award:
    						split_award.remove("motion")
    						split_award.remove("picture")
    						if any([kw in tweet for kw in motion_picture]):
    							#sprint(tweet) #it's good here!
    							#print("hello")
    							#print(split_award)
    							if all([kw in tweet for kw in split_award]) or all([kw in tweet for kw in extra_split]): #includes television
    								print(tweet) 
    								t = sp(tweet)
    								print(t)
    								for person in t.ents:
    									print(person)
    									if person.label_ == "PERSON":
    										if person.text not in ["Golden Globes", "goldenglobes", "GoldenGlobes", "Golden globes", "golden globes"]:
    											poss_host = person.text.lower()
    											if poss_host not in Dict:
    												Dict[poss_host] = 1
    											else:
    												Dict[poss_host] += 1

	    		sorted_dict = sorted([key for (key,value) in Dict.items()])[-2:]
	    		if award == "best television series - musical or comedy":
	    			print(Dict)
    		#print(Dict)

    	
    #then insert this into 
    #then run this thing for each award 
    		GlobalDict[award]= sorted_dict
    		presenters = GlobalDict
    f.close()

    #with presenters, it'll probbably (and it did) pick up all the names-> presenters and presentees
    #for "presented to"-> get the index and exclude all the other words"

    return GlobalDict
    

    #Map of the problem-> 1. go through list of awards using for loop 2. then get tweets with keywords for presenters 3. then match award name or 80% of the award names or replace movie with film, etc 3. and then use POS tagger to get proper nouns with names and then see what's most common
    # for a in 

    #return presenters

def pre_ceremony():
    '''This function loads/fetches/processes any data your program
    will use, and stores that data in your DB or in a json, csv, or
    plain text file. It is the first thing the TA will run when grading.
    Do NOT change the name of this function or what it returns.'''
    # Your code here
    print("Pre-ceremony processing complete.")
    return

def read_data(year):
    file = 'gg' + str(year) + '.json'
    try:
        with open(file, 'r') as f:
            tweets = json.load(f)
        tweet_arr = [tweet['text'] for tweet in tweets]
    except ValueError:
        with open(file, "rb") as f:
            tweets = [json.loads(line) for line in f]
            tweet_arr = [tweet['text'] for tweet in tweets]
    return tweet_arr


def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    pprint.pprint(get_presenters(2020))
    return

if __name__ == '__main__':
    main()
