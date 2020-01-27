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
    sorted_dict = sorted([[value,key] for (key,value) in Dict.items()])[-5:]
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
    # Your code here
    return presenters

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
    with open(file, 'r') as f:
        tweets = json.load(f)
    tweet_arr = [tweet['text'] for tweet in tweets]
    return tweet_arr

def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    pprint.pprint(get_hosts(2013))
    return

if __name__ == '__main__':
    main()
