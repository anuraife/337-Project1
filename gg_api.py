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
television_syn = ["television", "tv", "Television", "TV", ]
motion_picture = ["motion", "picture,", "movie", "film", "Motion", "Picture", "Movie", "Film"]
winners = {}
worldMovies = []


def get_movie_titles(year):
    website_url = requests.get('https://en.wikipedia.org/wiki/List_of_American_films_of_%d' % (int(year) - 1)).text
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
                except AttributeError:
                    title = [td.text.strip() for td in tds[1]]
            worldMovies.append(title[0])


def most_frequent(list, num):
    occurence_count = Counter(list)
    return occurence_count.most_common(num)


def handle_awards(year):
    remove = ["or", "-", "by", "an", "in", "a"]
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
        extra_split = []
        for word in split_award:
            extra_split.append(word[0].upper() + word[1:])
        awards_split.append([award, split_award, extra_split])


def get_carpet(year):
    search = ["carpet", "dressed", "looking", "outfit"]
    good = ["best", "amazing", "goals", "beautiful", "my favorite", "stunning", "hot"]
    bad = ["worst", "ugly", "horrible", "repulsive", "least favorite"]
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
                    tweet_arr.append(tweet[worst+5:])
                    tweet = tweet[:worst]
                else:
                    tweet_arr.append(tweet[best+4:])
                    tweet = tweet[:best]
            t = sp(tweet)
            for person in t.ents:
                if person.label_ == "PERSON" and len(person.text) > 5:
                    print(tweet, person.text)
                    person = person.text.lower()
                    people = person.split()
                    list = []
                    while len(people) > 2:
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
    print(carpet_good, carpet_bad, controversial)
    best = sorted([[value, key] for (key, value) in carpet_good.items()])[-3:]
    worst = sorted([[value, key] for (key, value) in carpet_bad.items()])[-3:]
    controversial = sorted([[value, key] for (key, value) in controversial.items()])[-1]
    return {"best dressed": [b[1] for b in best], "worst dressed": [w[1] for w in worst], "most controversial": controversial[1]}


def get_jokes(year):
    search = ["joke", "jokes", "joking", "joked", "punchline", "hilarious", "funny", "funniest"]
    with open("jokes.txt", "w", encoding="utf-8") as f:
        for tweet in tweet_arr:
            if any([word in tweet for word in search]):
                t = sp(tweet)
                f.write(tweet)
                for chunk in t.noun_chunks:
                    f.write("\n")
                    f.write("text ")
                    f.write(chunk.text)
                    f.write("root ")
                    f.write(chunk.root.head.text)
                    f.write("dep ")
                    f.write(chunk.root.dep_)
                    f.write("\n")
    f.close()


def get_hosts(year):
    '''Hosts is a list of one or more strings. Do NOT change the name
    of this function or what it returns.'''
    Dict = {}
    if not tweet_arr:
        clean_data(year)
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
    """Awards is a list of strings. Do NOT change the name
    of this function or what it returns."""
    first = time.time()
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
    # with open("myfile.txt", "w", encoding='utf-8') as f:
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
                    # f.write(award)
                    # f.write("\n")
    # f.close()
    banned = []
    approved = ["or", "by", "in", "a", "an"]
    # with open("myfile2.txt", "w", encoding="utf-8") as f:
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
              "competing"]
    search_words = ["beating", "beats out", "beats", "beat out", "beat", "compete", "competing"]
    poss_nominees = {}
    nominees = {}
    if not awards_split:
        handle_awards(year)

    if not tweet_arr:
        clean_data(year)

    if not worldMovies:
        get_movie_titles(year)

    # def clean_tweet(tweet, award):
    #     tweet = tweet.split()
    #     t = [word for word in tweet.lower() if re.match(r'http\S+', word) is None
    #          and (re.match(r'[A-Z]', word[0]) or word in [",", "and"]) and word not in remove
    #          and word not in award]
    #     return " ".join(t)
    #
    # def helper2(poss_nominee):
    #     all_nominees = poss_nominee.split(",")
    #     last_split = all_nominees[-1].split("and")
    #     if len(last_split) > 1:
    #         all_nominees.remove(all_nominees[-1])
    #         for nom in last_split:
    #             all_nominees.append(nom)
    #     return all_nominees

    def helper(award, tweet):
        if "actor" in award or "actress" in award or "director" in award or "award" in award:
            t = sp(tweet)
            for ent in t.ents:
                if ent.label_ == "PERSON":
                    if award not in nominees:
                        poss_nominees[award] = [ent.text]
                    else:
                        poss_nominees[award].append(ent.text)
        else:
            for movie in worldMovies:
                if re.search(movie.lower(), tweet):
                    if award not in poss_nominees:
                        poss_nominees[award] = movie.lower()
                    else:
                        poss_nominees[award].append(movie.lower())
    for tweet in tweet_arr:
        if any([word in tweet for word in search]):
            for award in awards_split:
                if "television" in award and "motion picture" in award[0]:
                    if any([word in tweet for word in television_syn]) and any(
                            [word in tweet for word in motion_picture]):
                        if all([word in tweet for word in award[1]]) or all([word in tweet for word in award[2]]):
                            helper(award[0], tweet)
                elif "television" in award[0]:
                    if any([word in tweet for word in television_syn]):
                        if all([word in tweet for word in award[1]]) or all([word in tweet for word in award[2]]):
                            helper(award[0], tweet)
                elif "motion picture" in award[0]:
                    if any([word in tweet for word in motion_picture]):
                        if all([word in tweet for word in award[1]]) or all([word in tweet for word in award[2]]):
                            helper(award[0], tweet)

    for award in poss_nominees.keys():
        nominees[award] = [freq[0] for freq in most_frequent(poss_nominees[award], 4)]

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
    search_words = ['wins', 'won', 'winning']
    search_words2 = ["awarded", "goes", "went", "took", "taking", "going"]
    remove = ["Golden Globes", "GoldenGlobes", "Golden globes", "Golden Globes %s" % str(year),
              "GoldenGlobes%s" % str(year)]

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

    # print(worldMovies)

    def helper(award, tweet):
        if "actor" in award or "actress" in award or "director" in award or "award" in award:
            t = sp(tweet)
            for ent in t.ents:
                if ent.label_ == "PERSON":
                    if award not in poss_winners:
                        poss_winners[award] = [ent.text]
                    else:
                        poss_winners[award].append(ent.text)
        elif "motion picture" in award:
            for movie in worldMovies:
                if re.search(movie, tweet):
                    if award not in poss_winners:
                        poss_winners[award] = [movie]
                    else:
                        poss_winners[award].append(movie)
        else:
            t = sp(tweet)
            for ent in t.ents:
                if ent.label_ == "GPE":
                    if award not in poss_winners:
                        poss_winners[award] = [ent.text]
                    else:
                        poss_winners[award].append(ent.text)

    for tweet in winner_tweets:
        for award in awards_split:
            if "television" in award and "motion picture" in award[0]:
                if any([word in tweet for word in television_syn]) and any([word in tweet for word in motion_picture]):
                    if all([word in tweet for word in award[1]]) or all([word in tweet for word in award[2]]):
                        helper(award[0], tweet)
            elif "television" in award[0]:
                if any([word in tweet for word in television_syn]):
                    if all([word in tweet for word in award[1]]) or all([word in tweet for word in award[2]]):
                        helper(award[0], tweet)
            elif "motion picture" in award[0]:
                if any([word in tweet for word in motion_picture]):
                    if all([word in tweet for word in award[1]]) or all([word in tweet for word in award[2]]):
                        helper(award[0], tweet)

    for award in poss_winners.keys():
        winners[award] = most_frequent(poss_winners[award], 1)[0][0]

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
    #tweet_arr = ["Priyanka Chopra and Nick Jonas at the 77th Annual Golden Globe Awards present the award for Best TV series for a musical or comedy"]
    #'best television series - musical or comedy',
    my_test_awards = ['best motion picture - drama', 'best motion picture - musical or comedy', 'best performance by an actress in a motion picture - drama', 'best performance by an actor in a motion picture - drama', 'best performance by an actress in a motion picture - musical or comedy', 'best performance by an actor in a motion picture - musical or comedy', 'best performance by an actress in a supporting role in any motion picture', 'best performance by an actor in a supporting role in any motion picture', 'best director - motion picture', 'best screenplay - motion picture', 'best motion picture - animated', 'best motion picture - foreign language', 'best original score - motion picture', 'best original song - motion picture', 'best television series - drama', 'best television series - musical or comedy', 'best television limited series or motion picture made for television', 'best performance by an actress in a limited series or a motion picture made for television', 'best performance by an actor in a limited series or a motion picture made for television', 'best performance by an actress in a television series - drama', 'best performance by an actor in a television series - drama', 'best performance by an actress in a television series - musical or comedy', 'best performance by an actor in a television series - musical or comedy', 'best performance by an actress in a supporting role in a series, limited series or motion picture made for television', 'best performance by an actor in a supporting role in a series, limited series or motion picture made for television', 'cecil b. demille award']
    television_syn = ["television", "tv", "TV" "tv series", "TV series", "television series"]
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
                if "best" in split_award:
                    split_award.remove("best")
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
                            extra_split.remove("Television")
                            #print(tweet)
                            if any([kw in tweet for kw in television_syn]):
                                #print(split_award)
                                #print(extra_split)
                                #print(tweet)
                                if "best" in tweet or "Best" in tweet:
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
                                    #print(tweet)
                                    t = sp(tweet)
                                    #print(t)
                                    for person in t.ents:
                                        #print(person)
                                        if person.label_ == "PERSON":
                                            if person.text not in ["Golden Globes", "goldenglobes", "GoldenGlobes", "Golden globes", "golden globes"]:
                                                poss_host = person.text.lower()
                                                if poss_host not in Dict:
                                                    Dict[poss_host] = 1
                                                else:
                                                    Dict[poss_host] += 1

                sorted_dict = sorted([key for (key,value) in Dict.items()])[-2:]
                #if award == "best television series - musical or comedy":
                    #print(Dict)
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
        tokens = [w for w in tokens]
        table = str.maketrans('', '', string.punctuation)
        stripped = [w.translate(table) for w in tokens]
        words = [w for w in stripped if not w in stop_words and re.match(r'http\S+', w) is None]
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
        json_return[award] = award_dict
    return json_data

def human_readable(year):
    json_format = json_data(year)
    print('Host: ' + json_format['Host'])
    for award in awards_split:
        award_results = json_format[award]
        print('Award: ' + award)
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
    # clean_data(2020)
    # handle_awards(2020)
    # get_awards(2020)
    pprint.pprint(get_winners(2020))
   # pprint.pprint(get_nominees(2020))
    #pprint.pprint(get_carpet(2020))
   # pprint.pprint(get_movie_titles(2020))
    return


if __name__ == '__main__':
    main()
