from concurrent.futures import ThreadPoolExecutor
import requests
from requests.auth import HTTPDigestAuth
from requests_futures.sessions import FuturesSession

class Connector:
    '''
    A parent class for opening a connection to a datasource using a username,passworkd authentification
    '''

    def __init__(self, username, password, root_url, max_connections=1) -> None:
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
        self.max_connection=1
        
        # instanciate session for asynchronous requests
        self.session = FuturesSession(executor=ThreadPoolExecutor(max_workers=max_connections),
                                     session=requests.Session())
        self.session.auth = HTTPDigestAuth(username, password)
        response = self.session.get(root_url)
        self.status = response.result().status_code

    def test_connection(self):
        '''
        Tests connection and update the "status" attribute upon success.
        '''

        response  = self.session.get(self.root_url)
        response.raise_for_status()
        self.status = response.status_code
        print("Test successful! Status code:", self.status)

    def close_connection(self):
        '''
        Ends the connection and closes the connection session.
        '''

        self.session.close()
        print("Session for this connector was closed by user")

