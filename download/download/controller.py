"""
Download data from external data sources, given a url, into the local data directory.
"""


class Controller:
    '''
    Provides a loop for setting recurrent data searching and downloading.
    '''

    def __init__(self, frequency):
        
        self.frequency = frequency


    def start(self):
        pass

        #TODO: loop for calling search and download using the frequency.