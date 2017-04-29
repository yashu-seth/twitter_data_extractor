import csv

import tweepy
import requests

from secret import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET


class TwitterData():
    """
    Class used for extracting data from the twitter profile
    and feed of a particular user.
    """
    def __init__(self, user_id, tweets_required):
        """
        Parameters
        ----------
        user_id: string
        The username of the profile of interest.

        no_of_tweets: integer
        The number of tweets whose data is required.

        Examples
        --------
        >>> profile = TwitterData('narendramodi', 2000)

        >>> profile.name
        'Narendra Modi'

        >>> profile.about
        'Prime Minister of India'

        >>> profile.born
        'September 17'

        >>> profile.to_csv
        writing to narendramodi_user_data.csv

        """
        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

        api = tweepy.API(auth)        

        self.user_id = user_id
        self.user = api.get_user(user_id)
        self.tweets_required = tweets_required

        self.tweets = api.user_timeline(user_id, count=min(tweets_required,200))

        for no in range(tweets_required/200 - 1):
            oldest_tweet_id = self.tweets[-1].id - 1
            self.tweets.extend(api.user_timeline(user_id, max_id=oldest_tweet_id, count=200))

        self._request = None

    @property
    def url(self):
        return "https://twitter.com/" + self.user_id

    @property
    def request(self):
        if self._request is not None:
            return self._request
        self._request = requests.get(self.url)
        return self._request

    @property
    def name(self):
        return self.user.name

    @property
    def username(self):
        return self.user.screen_name

    @property
    def about(self):
        return self.user.description

    @property
    def location(self):
        return self.user.location

    @property
    def website(self):
        return self.user.url

    @property
    def joined_on(self):
        return self.user.created_at

    @property
    def verified(self):
        return self.user.verified

    @property
    def no_of_tweets(self):
        return self.user.statuses_count

    @property
    def following(self):
        return self.user.friends_count

    @property
    def followers(self):
        return self.user.followers_count

    @property
    def listed_count(self):
        return self.user.listed_count

    def get_all_user_data(self):
        """
        Returns a list of all the available user data.
        """
        return  [self.url, self.name, self.username, self.about, self.location,
                self.website, self.joined_on.date(), self.joined_on.time(),
                self.verified, self.no_of_tweets,
                self.following, self.followers, self.listed_count]

    def _get_tags(self, tweet, entity):
        """
        Parameters
        ----------
        tweet: Tweepy status object
        entity: string
            user_mentions or hashtags

        Returns
        -------
        Returns a two element tuple with the number of tags (hashtags or user mentions) as
        the first element and a string of comma separated tag texts as the second element.
        """
        tags = tweet._json["entities"][entity]
        text_key = 'text' if entity == 'hashtags' else 'name'
        all_tags = []
        for tag in tags:
            all_tags.append(tag[text_key])
        return len(all_tags), (",".join(all_tags).encode('utf-8'))

    def _get_media_type(self, tweet):
        if 'extended_entities' not in tweet._json:
            return ""
        media_type = [media["type"] for media in tweet._json["extended_entities"]["media"]]
        return ",".join(media_type).encode('utf-8')

    def _possibly_sensitive(self, tweet):
        """
        Wrapper method because some of the json outputs
        have missing 'possibly_sensitive' key.
        """

        if 'possibly_sensitive' not in tweet._json:
            return ""
        return tweet._json["possibly_sensitive"]

    def to_csv(self):
        """
        Creates a csv file of the user details.
        """
        print("writing to {0}_user_data.csv".format(self.user_id))
        with open("{0}_user_data.csv".format(self.user_id), "w+") as file:
            writer = csv.writer(file)
            column_headers = ["Url", "Name", "Username", "About", "Location", "Website",
                              "Date", "Time", "Verified",
                              "No. of Tweets", "Following", "Followers", "List Counts"]
            writer.writerows([column_headers, self.get_all_user_data()])
            column_headers = ["Tweet ID", "Retweeted", "Date Created", "Time Created", "No. of Retweets", "Likes",
                              "No. of hashtags", "Hashtag texts", "No. of User Mentions", "User Mentions Text",
                              "Media Type", "Source", "Is Quote Status",
                              "Favorited", "Possibly Sensitive", "Language"]
            writer.writerows([column_headers])

            writer.writerows([tweet.id_str + " - id", tweet.retweeted, tweet.created_at.date(),
                              tweet.created_at.time(),
                              tweet.retweet_count, tweet.favorite_count,
                              self._get_tags(tweet, 'hashtags')[0],
                              self._get_tags(tweet, 'hashtags')[1],
                              self._get_tags(tweet, 'user_mentions')[0],
                              self._get_tags(tweet, 'user_mentions')[1],
                              self._get_media_type(tweet), tweet.source.encode('utf-8'),
                              tweet._json["is_quote_status"],
                              tweet.favorited, self._possibly_sensitive(tweet),
                              tweet._json["lang"]] for tweet in self.tweets)

p = TwitterData('AmitShah', 1000)
p.to_csv()
print(len(p.tweets))
