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
        # self.max_connection= max_connections

        self.session = requests.Session()
        self.session.auth = (username, password)
        
        try:
            response = self.session.get(root_url)
        except:
            ConnectionError("Connection failed. Check if the roor_url is set correctly and if the remote server is responsive")
        
        self.status = response.status_code

        if self.status != 200:
            raise RuntimeError

    def test_connection(self):
        '''
        Tests connection and update the "status" attribute upon success.
        '''
        try:
            response  = self.session.get(self.root_url)
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
    
    def get(self, request):
        '''
        Implements HTTP-GET method

        Args:
            request (str): a valid URL
        
        Returns: requests object
        '''

        # deling with spaces and special caracters in the request string
        encode_request = requote_uri(request)
        respone = self.session.get(encode_request)

        return respone

