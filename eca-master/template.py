# All used Libraries
from eca import *
from eca.generators import start_offline_tweets
import datetime
import time
import textwrap
import eca.http
import re
import random
import pprint


# Filter dictionary which contains the filter chosen by the user
filterDict = {
    "Language": "ALL",
    "Hashtags": [],
    "FIFApage": False,
    "filterOn": False,
}


# This function will be called to set up the HTTP server
def add_request_handlers(httpd):
    # add an event-generating request handler to fire 'order' events
    # This requires the POST method because the event generation handler only
    # understands POST requests.
    httpd.add_route('/api/filter', eca.http.GenerateEvent('filter'), methods=['POST'])

    # use the library content from the template_static dir instead of our own
    # this is a bit finicky, since execution now depends on a proper working directory.
    httpd.add_content('/lib/', 'template_static/lib')
    httpd.add_content('/style/', 'template_static/style')


# returs a boolean whether a filter is used or not.
def filterStatus():
    return filterDict["filterOn"]

# returns a boolean whether the box for the official FIFAWorldCup page is ticked or not.
def fifaPageTicked():
    return filterDict["FIFApage"]


# binds the 'setup' function as the action for the 'init' event
# the action will be called with the context and the event
@event('init')
def setup(ctx, e):
    start_offline_tweets('worldcupfinal_2014.txt', time_factor=0.5, event_name='chirp')
    ctx.words = {}



@event('filter')
def log(ctx, e):
    filterData = e.data
    
    # Checks whether the box for the official FIFA page is ticked or not.  
    if len(filterData["fifa_ticked"])!=0:
        filterDict["FIFApage"] = True
    else:
        filterDict["FIFApage"] = False

    # Whole if else statement is for updating 'filterDict'-data, whether a filter is on and what attributes it has.
    if filterData["Language"] == "ALL" and filterData["Hashtag"] == '':
        filterDict["Language"],filterDict["Hashtags"] = "ALL", ''
        filterDict["filterOn"] = False
        print(filterDict)
    else:
        filterDict["Language"],filterDict["Hashtags"] = filterData["Language"], makeHashtagIter(filterData["Hashtag"])
        filterDict["filterOn"] = True
        print(filterDict)
        
    """
    Log is for recording the filter history of a user. Initially, intended to be for academic purposes and in order to do 'personalized ads/stuff'(idea).
    It will probably be removed for the final product since it does not have any usage for the user or stakeholder, other than beeing able to see what filter(s) have been tried out.
    """
    """
    print(e.data)
    emit('filtering', {
    'text': "Chosen Langauge: {0}\nHashtag: {1}\nPage: {2}".format(filterData["Language"], filterData["Hashtag"], None)
    })
    """

# Makes the hashtag(s) iterable by splitting the text. In order to look for multiple hashtags, the user has to seperate them with a comma. (GER,ARG,Alemania......)
def makeHashtagIter(tags):
    hashtagsList = tags.split(',')
    return hashtagsList

# Checks whether a tweet contains the hashtag(s) given by the user and returns a boolean.
def tagsInTweet(user, tweet):
    try:
        for userTag in user["Hashtags"]:
            for hashTagObject in tweet["hashtags"]:
                tweetTag = hashTagObject["text"]
                if userTag.lower()==tweetTag.lower():
                    return True
        return False
    except KeyError:
        print("Probably 'user_mentions' which we do not filter.")
    

# word splitter
pattern = re.compile('\W+')


# keywords - words the wordcloud should display, namely players, countries and others common for the worldcup final and soccer
keyWords = ["brasil", "brasil2014", "ger", "arg", "argentine", "argentina", "alemania", "worldcup", "deutschland", "argentinien", "worldcup2014","mesut", "özil", "mesutözil", "toni",
"kroos", "tonikroos","manuel", "neuer", "manuelneuer", "kevin","grosskreutz",  "kevingrosskreutz", "matthiasginterbenedikt","matthias","ginter","benedikthöwedes", "benedikt", "höwedes",
"matshummels","mats", "hummels", "samikhedira", "sami", "khedira", "bastianschweinsteiger", "bastian", "schweinsteiger","andréschürrle", "andré", "schürle", "lukaspodolski", "lukas", "podolski",
"miroslavklose", "miroslav", "klose","ron-robertzieler", "ron-robert", "zieler", "thomasmüller", "thomas", "müller", "juliandraxler", "julian" "draxler","erikdurm", "erik", "durm", 
"philipplahm", "phillip", "lahm", "permertesacker", "per", "mertesacker", "mariogötze","mario","götze","jérômeboateng", "jérôme", "boateng", "shkodranmustafi","shkodran","mustafi",
"roman","romanweidenfeller","weidenfeller","christoph","kramer","christophkramer","sergioromero", "sergio", "romero", "marianoandujar", "marian", "andujar", "agustinorion", "augustin",
"orion", "federicofernandez", "federico", "fernandez", "ezequielgaray", "ezequiel", "garay", "martindemichelis", "martin", "demichelis", "pablozabaleta", "pablo", "zabate", "marcosrojo",
"marcos", "rojo", "josebasanta", "jose", "basante", "hugocampagnaro", "hugo", "campagnaro", "fernandogago", "fernando", "gago", "augustofernandez", "augusto", "fernandez", "javiermascherano",
"javier", "mascherano", "angeldimaria", "angel", "di", "maria", "lucasbiglia", "lucas", "biglia", "maxirodriguez", "maxi", "rodriguez", "ricardoalvarez", "ricardo", "alvarez", "football"
"enzoperez", "enzo", "perez", "sergioaguero", "sergio", "aguero", "gonzalohiguain", "gonzalo", "higuain", "lionelmessi", "lionel", "messi", "ezequiellavezzi", "ezequiel", "lavezzi", "soccer"
"rodrigopalacio", "rodrigo", "palacio", "fusßball", "fútbol", "fifa", "germany"]

# Idea of the two lists(Germany, Argentina) is that we want to see which country(with its player) is more popular
# and maybe whom the people want to see.

# List of German/Germany related words for the piechart
germany = ["mesut", "özil", "mesutözil", "toni","kroos", "tonikroos","manuel", "neuer", "manuelneuer", "kevin","grosskreutz",  "kevingrosskreutz", "matthiasginterbenedikt","matthias","ginter",
"benedikthöwedes", "benedikt", "höwedes","matshummels","mats", "hummels", "samikhedira", "sami", "khedira", "bastianschweinsteiger", "bastian", "schweinsteiger","andréschürrle", "andré", 
"schürle", "lukaspodolski", "lukas", "podolski","miroslavklose", "miroslav", "klose","ron-robertzieler", "ron-robert", "zieler", "thomasmüller", "thomas", "müller", "juliandraxler", "julian" 
"draxler","erikdurm", "erik", "durm", "philipplahm", "phillip", "lahm", "permertesacker", "per", "mertesacker", "mariogötze","mario","götze","jérômeboateng", "jérôme", "boateng", "shkodranmustafi",
"shkodran","mustafi","roman","romanweidenfeller","weidenfeller","christoph","kramer","christophkramer", "deutschland", "alemania", "germany"]
# List of spanish/Argentina related words for the piechart
argentina = ["sergioromero", "sergio", "romero", "marianoandujar", "marian", "andujar", "agustinorion", "augustin","orion", "federicofernandez", "federico", "fernandez", "ezequielgaray", "ezequiel",
 "garay", "martindemichelis", "martin", "demichelis", "pablozabaleta", "pablo", "zabate", "marcosrojo","marcos", "rojo", "josebasanta", "jose", "basante", "hugocampagnaro", "hugo", "campagnaro", "fernandogago", 
 "fernando", "gago", "augustofernandez", "augusto", "fernandez", "javiermascherano","javier", "mascherano", "angeldimaria", "angel", "di", "maria", "lucasbiglia", "lucas", "biglia", "maxirodriguez", "maxi", "rodriguez", 
 "ricardoalvarez", "ricardo", "alvarez", "football", "enzoperez", "enzo", "perez", "sergioaguero", "sergio", "aguero", "gonzalohiguain", "gonzalo", "higuain", "lionelmessi", "lionel", "messi", "ezequiellavezzi", "ezequiel",
 "lavezzi", "soccer","rodrigopalacio", "rodrigo", "palacio", "argentina", "argentinien"]


# Prepares a list for both the wordcloud and the piechart. Words are filtered by given patterns and conditions.
def words(message):
    result = pattern.split(message)
    result = map(lambda w: w.lower(), result)
    result = filter(lambda w: w in keyWords, result)
    result = filter(lambda w: len(w) > 2, result)
    return result


# Checks whether given parameter belongs to either of these country or not, and gives a boolean back.
def countrySlice(word):
    if word in germany:
        return "Germany"
    elif word in argentina:
        return "Argentina"
    else:
        return None


# Words get emitted to the cloud and piechart
def pie_cloud(e):
    tweet = e
    for w in words(tweet['text']):
        emit('word', {
            'action': 'add',
            'value': (w, 1)
            })
        # If the word w is not related to Argentina or Germany, we do not want it in the chart.
        if countrySlice(w)!=None:
            emit('piepie', {
                'action':'add',
                'value': (countrySlice(w),1)
        })


# Checks whether the official FIFAWorldCup page is mentioned in a text, so we can almost derive that it is a retweet.(look below)
def retweetFIFA(eventData):
    try:
        for userMentions in eventData["entities"]["user_mentions"]:
            if userMentions["screen_name"] == "FIFAWorldCup":
                return True
        return False
    except KeyError:
        print("user_mention probably does not exist.(occurs rarely)")


@event('chirp')
# Condition function should check whether the new retrieved suits the criteria of filters given by the user.
def tweet(ctx, e):
    # recieved metadata of tweet e
    tweet = e.data

    # Wordcloud is independent from the filter since we want to give the user the most occured/mentioned players, countries(from the final) and some other keywords related to soccer.
    pie_cloud(tweet)

    # If the box on the dashboard is ticked and the event data is a or includes a retweet of the official FIFAWorldCup page then it gets emitted.
    # fifaPageTicked() and retweetFIFA() not combined because then we would never reach the filter even though the box of FIFApage is not ticked.
    if fifaPageTicked():
        try: #Set the condition above fifty because their posts(FIFA page) got tweeted tons of times. Considering the possibility that other tweets got retweeted as well with a mention of Fifa(maybe from Stars etc.)
            if retweetFIFA(tweet) and tweet["retweeted_status"]["retweet_count"]>50:
                emit('tweet', tweet)
                return
            else:
                return
        except KeyError:
            print("It happens if the text of a tweet mentions the official FIFAWorldCup page but is not a retweet.")

    # Analyses the stored data and emits tweets accordingly to the filters.
    if filterStatus():
        if e.data["lang"] == filterDict["Language"] and filterDict["Hashtags"][0]=='':
            emit('tweet', tweet )
            return
        elif filterDict["Language"]=="ALL" and len(filterDict["Hashtags"])!=0 and len(tweet["entities"]["hashtags"])!=0:
            if tagsInTweet(filterDict, tweet["entities"]):
                emit('tweet', tweet)
        elif filterDict["Language"]!="ALL" and len(filterDict["Hashtags"])!=0 and len(tweet["entities"]["hashtags"])!=0:
            if e.data["lang"]==filterDict["Language"] and tagsInTweet(filterDict, tweet["entities"]):
                emit('tweet', tweet)
        else:
            return
    else:
        emit('tweet', tweet)
