########## IMPORTS ##########
import config  # external configuration file with API keys
import tweepy
import json
import jsonpickle
from datetime import datetime
from datetime import timedelta
from collections import Counter
import plotly
from plotly.offline import plot
import plotly.graph_objs as go

########## CONNECTING TO TWITTER API USING TWEEPY ##########
auth = tweepy.AppAuthHandler(config.twitter['API_KEY'], config.twitter['API_SECRET'])
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

if (not api):
  print ("Twitter API authentication failed")
  sys.exit(-1)

########## DEFINE VARIABLES ##########
#user = "@DelhiPolice"
#fname = "delhipolice.json"
user = "@bostonpolice"
fname = "bostonpolice.json"
tweets = []
likeCount = 0
likeCountText = 0
likeCountImage = 0
likeCountVideo = 0
retweetCount = 0
retweetCountText = 0
retweetCountImage = 0
retweetCountVideo = 0
tweetCount = 0
tweets_with_text = 0
tweets_with_images = 0
tweets_with_videos = 0
retweet_ids = []
tweets_dates = []
dateStart = datetime.strptime('1 August 2017, 00:00:00', '%d %B %Y, %H:%M:%S')
dateEnd = datetime.strptime('8 September 2017, 00:00:00', '%d %B %Y, %H:%M:%S')
lessCount = 0

########## GET ALL TWEETS OF USER ##########
with open(fname, 'w') as f:
  print "Collecting tweets..."
  for tweet in tweepy.Cursor(api.user_timeline, id=user, exclude_replies=1).items():
    datetime = tweet.created_at
    datetime = datetime - timedelta(hours=7)
    string_date = datetime.strftime('%d %B %Y')
    tweets_dates.append(string_date)
    #print type(tweet) #<class 'tweepy.models.Status'>
    obj = jsonpickle.encode(tweet._json, unpicklable=False)
    #print type(obj) #<type 'str'>
    data = json.loads(obj)
    #print type(data) #<type 'dict'>
    if datetime >= dateStart and datetime <= dateEnd:
      tweetCount = tweetCount + 1
      likeCount = likeCount + data['favorite_count']
      retweetCount = retweetCount + data['retweet_count']
      text = data['text'].encode('utf-8')
      text = str.lower(text)
      if text[0:2] == 'rt':
        id = data['retweeted_status']['user']['id']
        screen_name = data['retweeted_status']['user']['screen_name']
        name = data['retweeted_status']['user']['name']
        key = str(id) + " " + screen_name + " " + name
        retweet_ids.append(key)
      else:
        # get count of tweets containing media
        try:
          if 'media' not in data['entities']:
            tweets_with_text = tweets_with_text + 1
            likeCountText = likeCountText + data['favorite_count']
            retweetCountText = retweetCountText + data['retweet_count']
          else:
            for image in data['entities']['media']:
              if image['type'] == 'photo':
                tweets_with_images = tweets_with_images + 1
                likeCountImage = likeCountImage + data['favorite_count']
                retweetCountImage = retweetCountImage + data['retweet_count']
              elif image['media_url']:
                tweets_with_videos = tweets_with_videos + 1
                likeCountVideo = likeCountVideo + data['favorite_count']
                retweetCountVideo  = retweetCountVideo + data['retweet_count']
        except KeyError:
          pass
      #print obj
      f.write(obj + '\n')
      #print datetime.strftime('%d %B %Y, %H:%M:%S')
      #print data['text'].encode('utf-8')
      #print ""
    elif datetime <= dateStart:
      lessCount = lessCount + 1
    if lessCount > 10:
      break

print "Done!"
print ""
avg = tweetCount/38.0
print ("No. of tweets by {0}: {1}".format(user, tweetCount))
print ("Frequency of tweets by {0}: {1} tweets per day".format(user, avg))
#print ("Number of likes on these tweets: {0}".format(likeCount))
#print ("Number of retweets of these tweets: {0}".format(retweetCount))
print ("")

dates_dict = {}
for date in tweets_dates:
  if date in dates_dict:
    dates_dict[date] = dates_dict[date] + 1
  else:
    dates_dict[date] = 1
dates = dates_dict.keys()
dates_sorted = sorted(dates, key=lambda date: datetime.strptime(date, '%d %B %Y'))
keys = dates_sorted
values = []
for date in dates_sorted:
  values.append(dates_dict[date])
plot(
  [go.Scatter(
    x=keys,
    y=values
  )],
  show_link=False,
  filename='Tweet Frequency Graph.html',
  image='svg',
  image_filename='line'
)

print ("Number of tweets with text only: {0}".format(tweets_with_text))
print ("Number of likes on these tweets: {0}".format(likeCountText))
print ("Number of retweets of these tweets: {0}".format(retweetCountText))
if tweets_with_text > 0:
  temp = likeCountText/tweets_with_text
  print ("Average number of likes on tweets with text only: {0}".format(temp))
  temp = retweetCountText/tweets_with_text
  print ("Average number of retweets of tweets with text only: {0}".format(temp))
print ("")

print ("Number of tweets with image: {0}".format(tweets_with_images))
print ("Number of likes on these tweets: {0}".format(likeCountImage))
print ("Number of retweets of these tweets: {0}".format(retweetCountImage))
if tweets_with_images > 0:
  temp = likeCountImage/tweets_with_images
  print ("Average number of likes on tweets with image: {0}".format(temp))
  temp = retweetCountImage/tweets_with_images
  print ("Average number of retweets of tweets with image: {0}".format(temp))
print ("")

print ("Number of tweets with video: {0}".format(tweets_with_videos))
print ("Number of likes on these tweets: {0}".format(likeCountVideo))
print ("Number of retweets of these tweets: {0}".format(retweetCountVideo))
if tweets_with_videos > 0:
  temp = likeCountVideo/tweets_with_videos
  print ("Average number of likes on tweets with video: {0}".format(temp))
  temp = retweetCountVideo/tweets_with_videos
  print ("Average number of retweets of tweets with video: {0}".format(temp))
print ("")

print ("{0} has retweeted tweets from the following 10 user IDs the most -".format(user))
retweet_ids_dict = Counter(retweet_ids)
most_common_retweeted_ids = retweet_ids_dict.most_common(10)
for i in most_common_retweeted_ids:
  key = i[0]
  value = i[1]
  l = key.split(" ", 3)
  print l[1], value
print ("")
