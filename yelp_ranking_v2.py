"""
This code queries data by using the Search API to query for businesses by a 
search term,location and category. The data is then ranked using True Bayesian Estimate method
and Top 50 from the result in the search criteria is printed in the console. This Code also
generates two files " Top50_Ranked_Data_"Date/Time" "-Contains top 50 records of the rank system 
and "Ranked_Data_all"Date/Time""- contains all records sorted with new ranking system.

Sample usage of the program:
`python yelp_ranking.py --term="cafe" --location="San Francisco, CA" --category="cafes"`
"""
import argparse
import json
import sys
import urllib
import urllib2
import pandas as pd
import oauth2
import time


#from yelpapi import YelpAPI
#250-25
API_HOST = 'api.yelp.com'
DEFAULT_TERM = 'cafe'
DEFAULT_LOCATION = 'San Francisco, CA'
SEARCH_LIMIT = 20
MIN_VOTE=250
DEFAULT_CATEGORY = 'cafes'
SEARCH_PATH = '/v2/search/'
BUSINESS_PATH = '/v2/business/'

# OAuth credential placeholders that must be filled in by users.

CONSUMER_KEY = 'Enter your CONSUMER_KEY here'
CONSUMER_SECRET = 'Enter your CONSUMER_SECRET here'
TOKEN = 'Enter your Token here'
TOKEN_SECRET = 'Enter your Token _Secret here'


def request(host, path, url_params=None):
    """Prepares OAuth authentication and sends the request to the API.
    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        url_params (dict): An optional set of query parameters in the request.
    Returns:
        dict: The JSON response from the request.
    Raises:
        urllib2.HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = 'http://{0}{1}?'.format(host, urllib.quote(path.encode('utf8')))

    consumer = oauth2.Consumer(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_request = oauth2.Request(method="GET", url=url, parameters=url_params)

    oauth_request.update(
        {
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': oauth2.generate_timestamp(),
            'oauth_token': TOKEN,
            'oauth_consumer_key': CONSUMER_KEY
        }
    )
    token = oauth2.Token(TOKEN, TOKEN_SECRET)
    oauth_request.sign_request(oauth2.SignatureMethod_HMAC_SHA1(), consumer, token)
    signed_url = oauth_request.to_url()
    
    print u'Querying {0} ...'.format(url)
    conn = urllib2.urlopen(signed_url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    return response

def search(term, location, offset, category):
    """Query the Search API by a search term and location.
    Args:
        term (str): The search term passed to the API.
        location (str): The search location passed to the API.
        offset (int): The starting value of search index passed to the API.
        category (str): The search category passed to the API.
    Returns:
        dict: The JSON response from the request.
    """
    #http://api.yelp.com/v2/search/?location=San Francisco, CA&category_filter=cafes
    
    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'offset': offset,
        'limit': SEARCH_LIMIT,
        'category_filter': category.replace(' ', '+'),
    }
    return request(API_HOST, SEARCH_PATH, url_params=url_params)

def rank_results(term, location, category):
    """Queries the API by the input values from the user.
    Args:
        term (str): The search term to query.
        location (str): The location of the business to query.
        category (str): The search category passed to the API.
    Description:
        Uses Bayes Estimator algorithm to rank the system        
    """
    
    response = search(term, location,0,category)
    total = response.get('total')

    ind=0
    r_sum=0
    """store the required parameters from json obect into a dataframe"""
    yelp_df = pd.DataFrame(columns=['Name','R_Count','Yelp_Rating'])
    
    """increment the offset value by 20 as YELP api allows only a max of 
    20 results per api call"""
    for i in xrange(0,total,20):
        response=search(term, location, i,category)
        businesses = response.get('businesses')
    
        for j in response['businesses']:       
            name=j['name']
            v_count = j["review_count"]
            rating = j["rating"]
            r_sum=r_sum+j["rating"]
            yelp_df.loc[ind] = pd.Series({'Name':name, 'R_Count':v_count, 'Yelp_Rating':rating})
            ind=ind+1
    
    print 'Total number of results found: ', total
    r_avg=r_sum/(total)
    """The formula for Bayesian Estimate: WR = (vR+mC)/(v+m)
    where WR-weighted Rating
    R = yelp review of each businesses in the dataset = (Review)
    v = number of review count for businesses in the dataset = (Review Count)
    m = minimum votes required (assumed 250)
    C = average yelp review of the businesses in the dataset (mean) """
    yelp_df['WR'] = ((yelp_df['R_Count']*yelp_df['Yelp_Rating'])+(MIN_VOTE*r_avg))/(yelp_df['R_Count']+MIN_VOTE)    
    yelp_df=yelp_df.sort(['WR'], ascending=[0])
    print 'Top 50 Ranked' + term +'in' + 'location'
    print yelp_df[['Name','WR','Yelp_Rating']].head(50)
    businesses = response.get('businesses')
    res_filename = 'Top50_Ranked_Data_' + time.strftime("%m%d%Y-%HH%MM%SS")
    yelp_df.head(50).to_csv(res_filename+'.csv', sep='\t',encoding='utf-8',index=False)        
     
    yelp_df.to_csv('Ranked_Data_'+'all'+time.strftime("%m%d%Y-%HH%MM%SS")+'.csv', sep='\t',encoding='utf-8',index=False)        
    if not businesses:
        print u'No businesses for {0} in {1} found.'.format(term, location)
        return

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM, type=str, help='Search term (default: %(default)s)')
    parser.add_argument('-l', '--location', dest='location', default=DEFAULT_LOCATION, type=str, help='Search location (default: %(default)s)')
    parser.add_argument('-c', '--category', dest='category', default=DEFAULT_CATEGORY, type=str, help='Search category (default: %(default)s)')
    input_values = parser.parse_args()
    try:
        rank_results(input_values.term, input_values.location, input_values.category)
    except urllib2.HTTPError as error:
        sys.exit('Encountered HTTP error {0}. Abort program.'.format(error.code))

if __name__ == '__main__':
    main()