# -*- coding: utf-8 -*-

from eventlet.greenthread import sleep
from eventlet.green import urllib2
import simplejson as json
from collections import defaultdict
import urllib
from kral.utils import fetch_json

def stream(queries, queue, settings, kral_start_time):

    api_url = "http://www.reddit.com/search.json?"

    prev_items = defaultdict(list)

    user_agent = settings.get('DEFAULT', 'user_agent', '')

    while True:

        for query in queries:
           
            p = {
                'q' : query,
                'sort' : settings.get('Reddit', 'orderby', 'relevance'), 
            }
            
            url = api_url + urllib.urlencode(p)
        
            request = urllib2.Request(url)

            if user_agent:
                request.add_header('User-agent', user_agent)

            response = fetch_json(request)
            
            if not response:
                sleep(5)
                break

            if 'data' in response and 'children' in response['data']:

                #api returns back 25 items
                for item in response['data']['children']:
                    
                    item_id =  item['data']['id']
                    
                    #if we've seen this item in the last 50 items skip it
                    if item_id not in prev_items[query]:   
                    
                        post = {
                            'service' : 'reddit',
                            'query' : query,
                            'user' : {
                                'name' : item['data']['author'],
                            },
                            'id' : item_id,
                            'date' : item['data']['created_utc'],
                            'text' : item['data']['title'],
                            'source' : item['data']['url'],
                            'likes': item['data'].get('likes', 0),
                            'dislikes': item['data'].get('downs', 0),
                            'comments': item['data'].get('num_comments', 0),
                            'favorites': item['data'].get('saved', 0),
                        }
                         
                        queue.put(post)
                        
                        prev_items[query].append(item_id)
            
            #keep dupe buffer 50 items long
            #TODO: look into using deque with maxlength
            prev_items[query] = prev_items[query][:50]
        
        sleep(30)
