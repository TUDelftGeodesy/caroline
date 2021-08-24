# import requests
from requests import Request, Session
import requests
from requests.utils import requote_uri

class Connector:
    '''
    A parent class for connecting to a datasource using USERNAME/PASSWORD authentification
    '''

    def __init__(self, username, password, root_url) -> None:
        '''
        Creates and test a connection (Session) to a datasource (API) end point.
        Connections use digested credentials, and supports multiple simultaneous connections (requests).

        Args:
            username (str): username of an active account
            password (srt): password for the account
            root_url (srt): root URL to the API
            max_connections (int): maximum number of simultaneous connections used by the connector
            when communicating with the API. The API might impose its own restrctions to this.

        '''

        self.username = username
        self.password = password
        self.root_url = root_url
        
        self.header={}
        self.session = Session()
        self.session.auth = (username, password)
        
        test_request= Request('GET', self.root_url, headers=self.header)
        prepare = self.session.prepare_request(test_request)
        response = self.session.send(prepare)
        response.raise_for_status

        self.status = response.status_code


    def test_connection(self):
        '''
        Tests connection and update the "status" attribute upon success.
        '''
        try:
            test_request= Request('GET', self.root_url, headers=self.header)
            prepare = self.session.prepare_request(test_request)
            response = self.session.send(prepare)
        except:
            ConnectionError("Connection failed. Check if the roor_url is set correctly and if the remote server is responsive")
        self.status = response.status_code

        print("Test completed! Status code:", self.status)


    def close_connection(self):
        '''
        Ends the connection and closes the connection session.
        '''

        self.session.close()
        print("Session for this connector was closed by user")
    

    def get(self, request, stream=False ):
        '''
        Implements HTTP-GET method

        Args:
            request (str): a valid URL
            stream (bolean): set data streaming. Default is FALSE
        
        Returns: requests object
        '''
        encode_request = requote_uri(request)
        get_request= Request('GET', encode_request, headers=self.header)
        prepare = self.session.prepare_request(get_request)
        response = self.session.send(prepare, verify=True, stream=stream, timeout=None) # timeout=None, wait forever for response
        response.raise_for_status

        return response
