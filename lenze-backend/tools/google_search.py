import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

# Load the environment variables from the .env file
load_dotenv()
my_api_key = os.getenv('GOOGLE_API_KEY')
my_cse_id = os.getenv('CSE_ID')

class SearchEngine():

    def __init__(self):
        self.api_key = my_api_key
        self.cse_id = my_cse_id
        self.customsearch = build("customsearch", "v1", developerKey=self.api_key)
        self.youtube = build("youtube", "v3", developerKey=self.api_key)

    def web_search(self, search_term, num=10, **kwargs):

        all_sources = []
        start = 1
        while start < num:
            res = self.customsearch.cse().list(q=search_term, cx=self.cse_id, start=start, num=10, **kwargs).execute()
            start += 10
            sources = [{'title': result['title'], 'link': result['link']} for result in res['items']]
            all_sources.extend(sources)

        return all_sources[:num]

    def image_search(self, search_term, **kwargs):

        res = self.customsearch.cse().list(q=search_term, cx=self.cse_id, searchType = "image", **kwargs).execute()
        image_urls = [item['link'] for item in res['items']]

        return image_urls

    def video_search(self, search_term, **kwargs):

        request = self.youtube.search().list(q=search_term, part='snippet', type='video', maxResults=5)
        res = request.execute()
        video_ids = [item['id']['videoId'] for item in res['items']]
        
        return video_ids
        
