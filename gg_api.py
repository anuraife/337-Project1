'''Version 0.35'''
import json
from collections import Counter
import re
import pprint
import spacy
import operator
import string
import time
import requests
from lxml import html
from bs4 import BeautifulSoup
import sys

sp = spacy.load('en_core_web_sm')
nlp = spacy.load("en_core_web_md")

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
tweet_arr = []
winner_tweets = []
awards_split = []
television_syn =  ["television", "tv", "Television", "TV", ]
motion_picture = ["motion", "picture,", "movie", "film", "Motion", "Picture", "Movie", "Film", "Musical", "musical"]
cecil_award = ["Cecil B. DeMille", "Cecil", "cecil", "cecil b demille", "cecille", "Cecille", "cecil b. demille"]
winners = {}
global_poss_nominees = {}
worldMovies = []


def get_movie_titles(year):
    website_url = requests.get(
        'https://en.wikipedia.org/wiki/List_of_American_films_of_%d' % (int(year) - 1)).text
    soup = BeautifulSoup(website_url, 'lxml')
    tables = soup.findAll('table', {'class': 'wikitable sortable'})
    for table in tables:
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')[:2]
            if not tds:
                continue
            else:
                try:
                    title = [td.text.strip() for td in tds[0]]
                    worldMovies.append(title[0])
                except AttributeError:
                    try:
                        title = [td.text.strip() for td in tds[1]]
                        worldMovies.append(title[0])
                    except AttributeError:
                        pass


def most_frequent(list, num):
    occurence_count = Counter(list)
    return occurence_count.most_common(num)


def handle_awards(year):
    remove = ["or", "-", "by", "an", "in", "a", "performance"]
    if year > 2018:
        awards = OFFICIAL_AWARDS_1819
    else:
        awards = OFFICIAL_AWARDS_1315
    for award in awards:
        split_award = award.split()
        for word in remove:
            try:
                split_award.remove(word)
            except ValueError:
                pass
        if "television" in award:
            split_award.remove("television")
        if "motion picture" in award:
            split_award.remove("motion")
            split_award.remove("picture")
        awards_split.append([award, split_award])


def get_carpet(year):
    search = ["dressed", "looking", "outfit"]
    good = ["best", "amazing", "goals", "beautiful", "my favorite", "stunning", "hot", "spectacular", "vision",
            "elegant", "glamour", "glam", "pretty", "looking good", "showstopping", "dapper", "ravishing", "hot"]
    bad = ["worst", "ugly", "horrible", "repulsive", "least favorite", "outrageous", "bad", "distasteful"]
    carpet_good = {}
    carpet_bad = {}
    controversial = {}

    if not tweet_arr:
        clean_data(year)

    for tweet in tweet_arr:
        if any([word in tweet for word in search]):
            if "best" in tweet and "worst" in tweet:
                best = tweet.index("best")
                worst = tweet.index("worst")
                if best < worst:
                    tweet_arr.append(tweet[worst + 5:])
                    tweet = tweet[:worst]
                else:
                    tweet_arr.append(tweet[best + 4:])
                    tweet = tweet[:best]
            t = sp(tweet)
            for person in t.ents:
                if person.label_ == "PERSON" and len(person.text) > 5:
                    person = person.text.lower()
                    people = person.split()
                    list = []
                    while len(people) >= 2:
                        list.append(people[0] + " " + people[1])
                        people = people[2:]
                    if any([word in tweet for word in good]):
                        for person in list:
                            if person not in carpet_good:
                                carpet_good[person] = 1
                            else:
                                carpet_good[person] += 1
                    if any([word in tweet for word in bad]):
                        for person in list:
                            if person not in carpet_bad:
                                carpet_bad[person] = 1
                            else:
                                carpet_bad[person] += 1
    for key in carpet_bad.keys():
        if key in carpet_good.keys():
            if key not in controversial:
                controversial[key] = 1
            else:
                controversial[key] += 1
    best = sorted([[value, key] for (key, value) in carpet_good.items()])[-2:]
    worst = sorted([[value, key] for (key, value) in carpet_bad.items()])[-2:]
    controversial = sorted([[value, key] for (key, value) in controversial.items()])[-1]
    return {"best dressed": [b[1] for b in best], "worst dressed": [w[1] for w in worst],
            "most controversial": controversial[1]}


# def get_jokes(year):
#     content = ["was", "about"]
#     jokesters = {}
#     jokes = []
#     if not tweet_arr:
#         clean_data(year)
#     for tweet in tweet_arr:
#         if "joke" in tweet:
#             ind = tweet.index("joke")
#             for word in content:
#                 if word in tweet[ind + 4:]:
#                     ind2 = tweet[ind + 4:].index(word)
#                     cont = tweet[ind + 4:][ind2 + len(word):]
#                     t = sp(tweet)
#                     for ent in t.ents:
#                         if ent.label_ == "PERSON":
#                             if ent.text.lower() not in jokesters:
#                                 jokesters[ent.text.lower()] = [cont]
#                             else:
#                                 jokesters[ent.text.lower()].append(cont)
#     funniest = ""
#     most_jokes = 0
#     for jokester in jokesters.keys():
#         if len(jokesters[jokester]) > 6:
#             best_joke = most_frequent(jokesters[jokester], 1)
#             jokes.append(jokester + "'s best joke was " + best_joke[0][0])
#             if len(jokesters[jokester]) > most_jokes:
#                 funniest = jokester
#                 most_jokes = len(jokesters[jokester])
#
#     return jokes, funniest


def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    Dict = {}
    search = ["host", "hosts", "hosting", "hosted"]
    no_good = ["next year", "Next year", "last year", "Last year"]
    if not tweet_arr:
        clean_data(year)
    for tweet in tweet_arr:
        if all([word not in tweet for word in no_good]):
            if any([word in tweet for word in search]):
                t = sp(tweet)
                for person in t.ents:
                    if person.label_ == "PERSON":
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
    awards = []
    search_words = ['wins', 'won', 'winning', "accepts", "accepted"]
    search = ['wins', 'won', 'winning', 'awarded to', 'goes to', 'went to', 'nominated for', "accepts", "accepted",
              "taking", "took"]
    search_words2 = ["awarded", "goes", "went", "took", "taking", "going"]
    remove_words = ["prize", "category", "honor", "for", "is", "etc", "the", "at", "of", "over", "from"
                                                                                                 "year", "so", "far",
                    "goes", "to", "night", "evening", "live", "updates", "oscars",
                    "baftas", "bafta", "emmy", "trophy", "oscar", "hopefully", "and", "sag", "prestigious",
                    "our", "coveted", "from", "with"]
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
    if not tweet_arr:
        clean_data(year)

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
        tweet = tweet.lower()
        if "best" in tweet or "award" in tweet:
            if any([word in tweet for word in search]):
                for t in sp.pipe(tweet, disable=["ner"]):
                    chunks = [chunk for chunk in t.noun_chunks]
                    for i, chunk in enumerate(chunks):
                        if "best" in chunk.text or "award" in chunk.text:
                            if (chunk.root.head.text in search_words and chunk.root.dep_ == "dobj") \
                                    or (chunk.root.head.text in search_words2 and chunk.root.dep_ == "nsubj") \
                                    or (chunk.root.head.text == "for" and chunk.root.dep_ == "pobj"):
                                award = helper(chunk.text, chunks[i + 1:], t)
                                winner_tweets.append(tweet)
                                if award:
                                    awards.append(award)

    for award in awards:
        if award:
            if len(award.split()) > 3 and not any([word in award for word in exclude_words]):
                for pair in replacements:
                    award = award.replace(pair[0], pair[1])
                award_words = award.split()
                for word in remove_words + search_words + search_words2:
                    if word in award_words:
                        award_words.remove(word)
                if len(award_words) > 3:
                    final.append(" ".join(award_words))

    banned = []
    approved = ["or", "by", "in", "a", "an"]
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
                award = " ".join(award_words)
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

    for key in [key for key in ret.keys() if len(ret[key]) > 3]:
        award = most_frequent(ret[key], 1)[0][0]
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

    return ret2


def get_nominees(year):
    '''Nominees is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change
    the name of this function or what it returns.'''
    search = ["beating", "beats out", "beating", "beats", "beat out", "beat", "nominated", "nominee", "compete",
              "competing", "up for"]
    poss_nominees = {}
    nominees = {}
    if not awards_split:
        handle_awards(year)

    if not tweet_arr:
        clean_data(year)

    if not worldMovies:
        get_movie_titles(year)

    def helper(award, tweet):
        if "actor" in award or "actress" in award or "director" in award or "cecil" in award:
            t = sp(tweet)
            for ent in t.ents:
                if ent.label_ == "PERSON" and ent.text not in cecil_award:
                    if award not in poss_nominees:
                        poss_nominees[award] = [ent.text.lower()]
                    else:
                        person_name = ent.text.lower().split()
                        broken = False
                        prev_people = [person.split() for person in poss_nominees[award]]
                        for person in prev_people:
                            if all([word in person for word in person_name]):
                                poss_nominees[award].append(" ".join(person))
                                broken = True
                                break
                        if not broken:
                            poss_nominees[award].append(ent.text.lower())
        elif "motion picture" in award:
            for movie in worldMovies:
                if re.search(movie, tweet):
                    if award not in poss_nominees:
                        poss_nominees[award] = [movie.lower()]
                    else:
                        poss_nominees[award].append(movie.lower())
        else:
            t = sp(tweet)
            for ent in t.ents:
                if ent.label_ == "GPE" or ent.label_ == "WORK_OF_ART":
                    if award not in poss_nominees:
                        poss_nominees[award] = [ent.text.lower()]
                    else:
                        poss_nominees[award].append(ent.text.lower())

    for tweet in tweet_arr:
        if any([word in tweet for word in search]):
            for award in awards_split:
                if "television" in award and "motion picture" in award[0]:
                    if any([word in tweet for word in television_syn]) and any(
                            [word in tweet for word in motion_picture]):
                        if all([word in tweet.lower() for word in award[1]]):
                            helper(award[0], tweet)
                elif "television" in award[0]:
                    if any([word in tweet for word in television_syn]):
                        if all([word in tweet.lower() for word in award[1]]):
                            helper(award[0], tweet)
                elif "motion picture" in award[0]:
                    if any([word in tweet for word in motion_picture]):
                        if all([word in tweet.lower() for word in award[1]]):
                            helper(award[0], tweet)
                elif "cecil" in award[0]:
                    if any([kw in tweet.lower() for kw in cecil_award]):
                        helper(award[0], tweet)

    for award in poss_nominees.keys():
        nominees[award] = [freq[0] for freq in most_frequent(poss_nominees[award], 4)]

    if global_poss_nominees:
        for award in global_poss_nominees.keys():
            if award not in nominees:
                nominees[award] = global_poss_nominees[award]
            elif len(nominees[award]) < 4:
                global_poss_nominees[award].reverse()
                for nom in global_poss_nominees[award]:
                    if nom not in nominees[award] and len(nominees[award]) < 4:
                        nominees[award].append(nom)

    if winners:
        for award in winners.keys():
            if award in nominees:
                if winners[award] in nominees[award]:
                    nominees[award].remove(winners[award])

    return nominees


def get_winners(year):
    '''Winners is a dictionary with the hard coded award
    names as keys, and each entry containing a single string.
    Do NOT change the name of this function or what it returns.'''
    poss_winners = {}
    search = ['wins', 'won', 'winning', 'awarded to', 'goes to', 'went to', 'nominated for', "accepts", "accepted",
              "taking", "took", 'gets', 'takes', 'got', 'congratulations', 'congrats', 'nominee', 'up for', 'going to',
              'win', 'thanks', 'winner', 'going']

    if not winner_tweets:
        if not tweet_arr:
            clean_data(year)
        for tweet in tweet_arr:
            if any([word in tweet for word in search]):
                winner_tweets.append(tweet)

    if not awards_split:
        handle_awards(year)

    if not worldMovies:
        get_movie_titles(year)

    def helper(award, tweet):
        if "actor" in award or "actress" in award or "director" in award or "cecil" in award:
            t = sp(tweet)
            for ent in t.ents:
                if ent.label_ == "PERSON" and ent.text not in cecil_award:
                    if award not in poss_winners:
                        poss_winners[award] = [ent.text.lower()]
                    else:
                        person_name = ent.text.lower().split()
                        if len(person_name) < 2:
                            broken = False
                            prev_people = [person.split() for person in poss_winners[award]]
                            for person in prev_people:
                                if all([word in person for word in person_name]):
                                    poss_winners[award].append(" ".join(person))
                                    broken = True
                                    break
                            if not broken:
                                poss_winners[award].append(ent.text.lower())
                        else:
                            poss_winners[award].append(ent.text.lower())
        elif "motion picture" in award:
            for movie in worldMovies:
                if re.search(movie, tweet):
                    if award not in poss_winners:
                        poss_winners[award] = [movie.lower()]
                    else:
                        poss_winners[award].append(movie.lower())
        else:
            t = sp(tweet)
            for ent in t.ents:
                if ent.label_ == "GPE" or ent.label_ == "WORK_OF_ART":
                    if award not in poss_winners:
                        poss_winners[award] = [ent.text.lower()]
                    else:
                        poss_winners[award].append(ent.text.lower())

    for tweet in winner_tweets:
        for award in awards_split:
            if "television" in award and "motion picture" in award[0]:
                if any([word in tweet for word in television_syn]) and any([word in tweet for word in motion_picture]):
                    if all([word in tweet.lower() for word in award[1]]):
                        helper(award[0], tweet)
            elif "television" in award[0]:
                if any([word in tweet for word in television_syn]):
                    if all([word in tweet.lower() for word in award[1]]):
                        helper(award[0], tweet)
            elif "motion picture" in award[0]:
                if any([word in tweet for word in motion_picture]):
                    if all([word in tweet.lower() for word in award[1]]):
                        helper(award[0], tweet)
            elif "cecil" in award[0]:
                if any([kw in tweet.lower() for kw in cecil_award]):
                    helper(award[0], tweet)

    for award in poss_winners.keys():
        winners[award] = most_frequent(poss_winners[award], 1)[0][0]
        global_poss_nominees[award] = [freq[0] for freq in most_frequent(poss_winners[award], 4)]

    return winners


def get_presenters(year):
    '''Presenters is a dictionary with the hard coded award
    names as keys, and each entry a list of strings. Do NOT change the
    name of this function or what it returns.'''

    presenters = {}
    no_good = ["next year", "Next year", "Last year", "last year", "representation", "represent", "represented"]
    search = ["present", "presented", "gave the award", "introduce", "give", "read",  "presenting",
              "giving the award", "handing the award", "introducing"]
    tv_syn = ["television", "tv", "TV" "tv series", "TV series", "television series"]

    if not tweet_arr:
        clean_data(year)

    if not awards_split:
        handle_awards(year)

    def helper(award, tweet):
        t = sp(tweet)
        for person in t.ents:
            if person.label_ == "PERSON" and person.text not in cecil_award:
                poss_host = person.text.lower()
                if poss_host not in Dict:
                    Dict[poss_host] = 1
                else:
                    Dict[poss_host] += 1
        sorted_dict = sorted([[value, key] for (key, value) in Dict.items()])[-2:]
        presenters[award] = [person[1] for person in sorted_dict]

    for award in awards_split:
        Dict = {}
        for tweet in tweet_arr:  # tweet in tweet_arr
            if "best" in awards_split[1]:
                awards_split[1].remove("best")
            if all([word not in tweet for word in no_good]) and ("best" in tweet or "Best" in tweet):
                if any([word in tweet for word in search]):
                    if "television" in award[0] and "motion picture" in award[0]:
                        if any([word in tweet for word in tv_syn]) and any(
                                [word in tweet for word in motion_picture]):
                            if all([word in tweet.lower() for word in award[1]]):
                                helper(award[0], tweet)
                    elif "television" in award[0]:
                        if any([kw in tweet for kw in tv_syn]):
                            if all([kw in tweet.lower() for kw in award[1]]):
                                helper(award[0], tweet)
                    elif "motion picture" in award[0]:
                        if any([kw in tweet for kw in motion_picture]):
                            if all([kw in tweet.lower() for kw in award[1]]):
                                helper(award[0], tweet)
                    elif "cecil" in award[0]:
                        if any([kw in tweet.lower() for kw in cecil_award]):
                            helper(award[0], tweet.lower())

    for award in winners.keys():
        if award in presenters.keys():
            if winners[award] in presenters[award]:
                presenters[award].remove(winners[award])

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
    try:
        with open(file, 'r') as f:
            tweets = json.load(f)
        tweet = [tweet['text'] for tweet in tweets]
    except ValueError:
        with open(file, "rb") as f:
            tweets = [json.loads(line) for line in f]
        tweet = [tweet['text'] for tweet in tweets]
    return tweet


def clean_data(year):
    tweets = read_data(year)
    stop_words = ['golden', 'globes', 'Golden', 'Globes', 'globe', 'Globe', 'gg', 'gg%s' % year, '%s' % year,
                  'he', 'she', 'goldenglobes%s' % year, 'goldenglobeawards', 'goldenglobeawards%s' % year,
                  'GoldenGlobeAwards', 'goldenglobes', 'goldenglobe', 'GoldenGlobes', 'GoldenGlobe', 'Goldenglobes',
                  'Goldenglobe', 'GoldenGlobes%s' % year, 'Goldenglobes%s' % year, 'GoldenGlobeAwards%s' % year,
                  'bartantdaily', 'huffposttv', 'tvguide', 'tvguidemagazine', 'abc', 'fandango', 'cnnshowbiz',
                  'filmdotcom', 'globalgrind', 'huffpostceleb', 'okmagazine', 'televisionary', 'jamaicannews', '‘', '’',
                  "globes'", "globe's", "hbo", "hbo's"]
    for tweet in tweets:
        tokens = tweet.split()
        table = str.maketrans('', '', string.punctuation)
        stripped = [w.translate(table) for w in tokens]
        words = [w for w in stripped if w not in stop_words and re.match(r'http\S+', w) is None]
        s = " "
        tweet_arr.append(s.join(words))
    return


def json_data(year):
    json_return = {}
    clean_data(year)
    handle_awards(year)
    get_awards(year)
    hosts = get_hosts(year)
    json_return['Host'] = hosts
    winners = get_winners(year)
    nominees = get_nominees(year)
    presenters = get_presenters(year)
    for award in awards_split:
        award_dict = {}
        award_dict['Presenters'] = presenters[award]
        award_dict['Nominees'] = nominees[award]
        award_dict['Winner'] = winners[award]
        json_return[award[0]] = award_dict
    return json_return


def human_readable(yr):
    for year in [2013, 2015, yr]:
        json_format = json_data(year)
        print('Host: ' + json_format['Host'])
        for award in awards_split:
            award_results = json_format[award[0]]
            print('Award: ' + award[0])
            print('Presenters: ' + award_results['Presenters'])
            print('Nominees: ' + award_results['Nominees'])
            print('Winner: ' + award_results['Winner'])
        dressed = get_carpet(year)
        print('Best dressed: ' + dressed['best dressed'])
        print('Worst dressed: ' + dressed['worst dressed'])
        print('Most controversial: ' + dressed['most controversial'])


def main():
    '''This function calls your program. Typing "python gg_api.py"
    will run this function. Or, in the interpreter, import gg_api
    and then run gg_api.main(). This is the second thing the TA will
    run when grading. Do NOT change the name of this function or
    what it returns.'''
    return human_readable(sys.argv)


if __name__ == '__main__':
    main()
