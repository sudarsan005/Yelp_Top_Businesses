Instructions:
-------------
Install the below dependencies
1)Install pandas with pip
2)pip install -r requirements.txt (I have attached requirements.txt file)
3) Also include your oauth credentials(CONSUMER_KEY, CONSUMER_SECRET, TOKEN, TOKEN_SECRET in the code in line number 34-37) , as of now for your convenience I have included my key in the code. 

then use the following format to run the code
python yelp_ranking.py --term="cafe" --location="San Francisco, CA" --category="cafes"

Note:
term=search term
location=location to search for the business
category=category of the business (the reason why I included category is, without this filter yelp returns more than 1300 records and Yelp API allows only 20 records to queried at a time so with this filter it reduced the search records to 400+ records)