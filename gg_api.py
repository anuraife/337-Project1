'''Version 0.35'''
import json
from collections import Counter
import re
import pprint
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.corpus import words
import spacy
import operator
import string
import time

sp = spacy.load('en_core_web_sm')
nlp = spacy.load("en_core_web_md")
# nltk.download('punkt')
# nltk.download('words')

OFFICIAL_AWARDS_1315 = ['cecil b. demille award', 'best motion picture - drama',
                        'best performance by an actress in a motion picture - drama',
                        'best performance by an actor in a motion picture - drama',
                        'best motion picture - comedy or musical',
                        'best performance by an actress in a motion picture - comedy or musical',
                        'best performance by an actor in a motion picture - comedy or musical',
                        'best animated feature film', 'best foreign language film',
                        'best performance by an actress in a supporting role in a motion picture',
                        'best performance by an actor in a supporting role in a motion picture',
                        'best director - motion picture', 'best screenplay - motion picture',
                        'best original score - motion picture', 'best original song - motion picture',
                        'best television series - drama',
                        'best performance by an actress in a television series - drama',
                        'best performance by an actor in a television series - drama',
                        'best television series - comedy or musical',
                        'best performance by an actress in a television series - comedy or musical',
                        'best performance by an actor in a television series - comedy or musical',
                        'best mini-series or motion picture made for television',
                        'best performance by an actress in a mini-series or motion picture made for television',
                        'best performance by an actor in a mini-series or motion picture made for television',
                        'best performance by an actress in a supporting role in a series, mini-series or motion '
                        'picture made for television',
                        'best performance by an actor in a supporting role in a series, mini-series or motion picture '
                        'made for television']
OFFICIAL_AWARDS_1819 = ['best motion picture - drama', 'best motion picture - musical or comedy',
                        'best performance by an actress in a motion picture - drama',
                        'best performance by an actor in a motion picture - drama',
                        'best performance by an actress in a motion picture - musical or comedy',
                        'best performance by an actor in a motion picture - musical or comedy',
                        'best performance by an actress in a supporting role in any motion picture',
                        'best performance by an actor in a supporting role in any motion picture',
                        'best director - motion picture', 'best screenplay - motion picture',
                        'best motion picture - animated', 'best motion picture - foreign language',
                        'best original score - motion picture', 'best original song - motion picture',
                        'best television series - drama', 'best television series - musical or comedy',
                        'best television limited series or motion picture made for television',
                        'best performance by an actress in a limited series or a motion picture made for television',
                        'best performance by an actor in a limited series or a motion picture made for television',
                        'best performance by an actress in a television series - drama',
                        'best performance by an actor in a television series - drama',
                        'best performance by an actress in a television series - musical or comedy',
                        'best performance by an actor in a television series - musical or comedy',
                        'best performance by an actress in a supporting role in a series, limited series or motion '
                        'picture made for television',
                        'best performance by an actor in a supporting role in a series, limited series or motion '
                        'picture made for television',
                        'cecil b. demille award']


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
                        if person.text not in ["Golden Globes", "goldenglobes", "GoldenGlobes", "Golden globes",
                                               "golden globes", "golden globes %s" % str(year),
                                               "gg%s" % str(year), "goldenglobes%s" % str(year),
                                               "Golden Globes %s" % str(year), "GoldenGlobes%s" % str(year)]:
                            poss_host = person.text.lower()
                            if poss_host not in Dict:
                                Dict[poss_host] = 1
                            else:
                                Dict[poss_host] += 1
    sorted_dict = sorted([[value, key] for (key, value) in Dict.items()])[-5:]
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
    """Awards is a list of strings. Do NOT change the name
    of this function or what it returns."""
    first = time.time()
    tweet_arr = clean_data(year)
    awards = []
    search_words = ['wins', 'won', 'winning', "accepts", "accepted"]
    search = ['wins', 'won', 'winning', 'awarded to', 'goes to', 'went to', 'nominated for', "accepts", "accepted",
              "taking", "took"]
    search_words2 = ["awarded", "goes", "went", "took", "taking", "going"]
    remove_words = ["prize", "category", "honor", "for", "is", "etc", "the", "at", "of", "over", "from"
                    "year", "so", "far", "goes", "to", "night", "evening", "live", "updates", "oscars",
                    "baftas", "bafta", "emmy", "trophy", "oscar", "hopefully", "and", "sag"]
    final = []
    ret = {}
    ret2 = []
    replacements = [["movie", "motion picture"], ["feature film", "motion picture"],
                    ["film", "motion picture"], ["tv show", "television series"],
                    ["tv series", "television series"], ["tv", "television"], ["mp", "motion picture"],
                    ["dramatic", "drama"], ["featured actor", "supporting actor"],
                    ["featured actress", "supporting actress"]]
    exclude_words = ["hair", "outfit", "speech", "quote", "dressed", "tweet", "use", "accessory", "punchline",
                     "joke", "fingers", "jewelry", "earrings", "necklace", "rings", "scene",
                     "acting", "brows", "commercial", "face", "mustache", "beard", "dress", "arms", "tie", "photo",
                     "red carpet", "story", "recipient", "braid", "tan", "appearance", "line", "seen", "hypocrisy",
                     "friend"]

    def helper(chunk_text, chunk_list, tweet):
        if chunk_list:
            for chunk in chunk_list:
                if chunk.root.head.text in ["in", "by"] and chunk.root.dep_ == "pobj":
                    chunk_text = chunk_text + " " + chunk.root.head.text + " " + chunk.text
                else:
                    return helper2(chunk_text, tweet)
        else:
            return helper2(chunk_text, tweet)

    def helper2(award, tweet):
        last_word = award.split()[-1]
        tokens = [token for token in tweet]
        tokens2 = [str(token) for token in tweet]
        try:
            ind = tokens2.index(last_word)
            if tokens[ind + 1:]:
                for token in tokens[ind + 1:]:
                    if (token.head.text in search_words + search_words2 or token.head.text in award) \
                            and token.text not in award:
                        award += " " + token.text
                        return helper2(award, tweet)
                    else:
                        return award
            else:
                return award
        except ValueError:
            pass

    for tweet in tweet_arr:
        if "best" in tweet or "award" in tweet:
            if any([word in tweet for word in search]):
                tweet = sp(tweet)
                chunks = [chunk for chunk in tweet.noun_chunks]
                for i, chunk in enumerate(chunks):
                    if "best" in chunk.text or "award" in chunk.text:
                        if (chunk.root.head.text in search_words and chunk.root.dep_ == "dobj") \
                                or (chunk.root.head.text in search_words2 and chunk.root.dep_ == "nsubj") \
                                or (chunk.root.head.text == "for" and chunk.root.dep_ == "pobj"):
                            award = helper(chunk.text, chunks[i + 1:], tweet)
                            if award:
                                awards.append(award)
    # with open("myfile.txt", "w", encoding='utf-8') as f:
    for award in awards:
        if award:
            if len(award.split()) > 3 and not any([word in award for word in exclude_words]):
                for pair in replacements:
                    award = award.replace(pair[0], pair[1])
                award_words = award.split()
                for word in remove_words + search:
                    if word in award_words:
                        award_words.remove(word)
                if len(award_words) > 3:
                    final.append(" ".join(award_words))
                    # f.write(award)
                    # f.write("\n")
    # f.close()
    banned = []
    approved = ["or", "by", "in", "a", "an"]
    #with open("myfile2.txt", "w", encoding="utf-8") as f:
    for award in final:
        broken = False
        if re.search('(^best|award$)', award):
            if re.search('^best', award):
                award = award.replace("award", "")
                a = nlp(award[4:])
                mov = [token for token in nlp("movie")][0]
                tv = [token for token in nlp("television")][0]
                for token in a:
                    if token.text not in banned + approved:
                        if token.similarity(mov) < 0.2 or token.similarity(tv) < 0.2:
                            banned.append(token.text)
                        else:
                            approved.append(token.text)
                award_words = award.split()
                for word in banned:
                    if word in award_words:
                        award_words.remove(word)
                award = " ". join(award_words)
            award_words = award.split()
            if len(award_words) > 3:
                for award2 in ret:
                    award2_words = award2.split()
                    if all([word in award2_words for word in award_words]):
                        ret[award2].append(award)
                        broken = True
                        break
                    if all([word in award_words for word in award2_words]):
                        ret[award] = ret[award2] + [award]
                        del ret[award2]
                        broken = True
                        break
                if not broken:
                    ret[award] = [award]

    def most_frequent(list):
        occurence_count = Counter(list)
        return occurence_count.most_common(1)[0][0]

    for key in [key for key in ret.keys() if len(ret[key]) > 3]:
        award = most_frequent(ret[key])
        if award not in ret2:
            award_words = award.split()
            broken = False
            for award2 in ret2:
                award2_words = award2.split()
                if all([word in award2_words for word in award_words]):
                    broken = True
                    break
                elif all([word in award_words for word in award2_words]):
                    ret2.remove(award2)
                    ret2.append(award)
                    broken = True
                    break
            if not broken:
                ret2.append(award)

    return ret


def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''

    return


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


def get_carpet(year):
    tweets = clean_data(year)
    search = ["carpet", "dressed", "looking", "outfit"]
    good = ["best", "amazing", "goals", "beautiful", "my favorite"]
    bad = ["worst", "ugly", "horrible", "repulsive", "least favorite"]
    carpet_good = {}
    carpet_bad = {}
    controversial = {}
    for tweet in tweets:
        if any([word in tweet for word in search]):
            if "best" in tweet and "worst" in tweet:
                best = tweet.index("best")
                worst = tweet.index("worst")
                if best < worst:
                    tweets.append(tweet[worst:])
                    tweet = tweet[:worst]
                else:
                    tweets.append(tweet[best:])
                    tweet = tweet[:best]
            t = sp(tweet)
            for person in t.ents:
                if person.label_ == "PERSON":
                    if any([word in tweet for word in good]):
                        if person.text.lower() not in carpet_good:
                            carpet_good[person.text.lower()] = 1
                        else:
                            carpet_good[person.text.lower()] += 1
                    if any([word in tweet for word in bad]):
                        if person.text not in carpet_bad:
                            carpet_bad[person.text.lower()] = 1
                        else:
                            carpet_bad[person.text.lower()] += 1
    for key in carpet_bad.keys():
        if key in carpet_good.keys():
            if key not in controversial:
                controversial[key] = 1
            else:
                controversial[key] += 1
    best = sorted([[value, key] for (key, value) in carpet_good.items()])[-1]
    worst = sorted([[value, key] for (key, value) in carpet_bad.items()])[-1]
    controversial = sorted([[value, key] for (key, value) in controversial.items()])[-1]
    return {"best dressed": best[1], "worst dressed": worst[1], "most controversial": controversial[1]}


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


def clean_data(year):
    tweet_arr = read_data(year)
    stop_words = ['golden', 'globes', 'Golden', 'Globes', 'globe', 'Globe', 'gg', 'gg%s' % year, '%s' % year,
                  'he', 'she', 'goldenglobes%s' % year, 'goldenglobeawards', 'goldenglobeawards%s' % year,
                  'GoldenGlobeAwards', 'goldenglobes', 'goldenglobe', 'GoldenGlobes', 'GoldenGlobe', 'Goldenglobes',
                  'Goldenglobe', 'GoldenGlobes%s' % year, 'Goldenglobes%s' % year, 'GoldenGlobeAwards%s' % year,
                  'bartantdaily', 'huffposttv', 'tvguide', 'tvguidemagazine', 'abc', 'fandango', 'cnnshowbiz',
                  'filmdotcom', 'globalgrind', 'huffpostceleb', 'okmagazine', 'televisionary', 'jamaicannews', '‘', '’',
                  "globes'", "globe's"]
    tweets = []
    for tweet in tweet_arr:
        tokens = tweet.split()
        tokens = [w.lower() for w in tokens]
        table = str.maketrans('', '', string.punctuation)
        stripped = [w.translate(table) for w in tokens]
        words = [w for w in stripped if not w in stop_words and re.match(r'http\S+', w) is None]
        s = " "
        tweets.append(s.join(words))
    return tweets


def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    pprint.pprint(get_carpet(2020))
    # tweet = nlp('actress television motion picture miniseries lincoln')
    # mov = [token for token in nlp("movie")][0]
    # tv = [token for token in nlp("television")][0]
    # for token in tweet:
    #     print(token.similarity(mov), token.similarity(tv))
    # award = "hello my name is"
    # award.replace("hello", "")
    # print(award)
    return


if __name__ == '__main__':
    main()
