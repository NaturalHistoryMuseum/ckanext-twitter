import logging

import oauth2
from beaker.cache import cache_region
from ckanext.twitter.lib import cache_helpers, config_helpers
logger = logging.getLogger('ckanext.twitter')


@cache_region('twitter', 'client')
def twitter_client():
    '''
    Attempts to create a client for accessing the twitter API using the
    credentials specified in the configuration file. Does not test for
    success. Caches the resulting client in the 'twitter' cache.
    :return: oauth2.Client
    '''
    consumer_key, consumer_secret, token_key, token_secret = \
        config_helpers.twitter_get_credentials()
    consumer = oauth2.Consumer(consumer_key, consumer_secret)
    token = oauth2.Token(token_key, token_secret)
    client = oauth2.Client(consumer, token)
    return client


def twitter_authenticate():
    '''
    Verifies that the client is able to connect to the twitter API.
    Refreshes any unauthenticated cached client.
    :return: boolean
    '''
    authenticated = False
    while not authenticated:
        was_cached = 'client' in cache_helpers.twitter_cache
        client = twitter_client()
        url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
        response, content = client.request(url, 'GET')
        authenticated = response.status == 200
        if was_cached and not authenticated:
            cache_helpers.twitter_cache.remove_value('client')
        else:
            break
    return authenticated


def post_tweet(tweet_text, pkg_id):
    '''
    Attempts to post the tweet. Returns a boolean success variable and a
    message describing the reason for the failure/success in posting the tweet.
    :param tweet_text: The text to post. This is passed in rather than
    generated inside the method to allow users to change the tweet before
    posting (if enabled).
    :param pkg_id: The package ID (for caching).
    :return: boolean, str
    '''
    if config_helpers.twitter_is_debug():
        logger.debug('Not posted (debug): ' + tweet_text)
        return False, 'debug'

    # if not enough time has passed since the last tweet
    if not cache_helpers.expired(pkg_id):
        logger.debug('Not posted (insufficient rest period): ' + tweet_text)
        return False, 'insufficient rest period'

    # if we can't authenticate
    if not twitter_authenticate():
        logger.debug('Not posted (not authenticated): ' + tweet_text)
        return False, 'not authenticated'

    # try to actually post
    client = twitter_client()
    url = 'https://api.twitter.com/1.1/statuses/update.json'
    params = {
        'status': tweet_text
        }
    request = oauth2.Request(method = 'POST', url = url, parameters = params)
    postdata = request.to_postdata()
    response, content = client.request(url, 'POST', postdata)
    if response.status == 200:
        cache_helpers.cache(pkg_id)
        logger.debug('Posted successfully: ' + tweet_text)
    else:
        logger.debug('Not posted (tweet unsuccessful): ' + tweet_text)
    return response.status == 200, '{0} {1}'.format(response.status,
                                                    response.reason)
