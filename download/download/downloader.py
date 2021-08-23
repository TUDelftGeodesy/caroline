"""
Download data from external data sources, given a url, into the local data directory.
"""


class Downloader:

    def __init__(self, url):
        self.url = url
        self.session= request.Session()    

    def start_download(self):    
        
        #TODO: USE request-future for assync requests: https://github.com/ross/requests-futures
        pass


