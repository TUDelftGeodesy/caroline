#!/usr/bin/env python3 
# -*- coding: utf-8 -*- 
# Created By  : Manuel G. Garcia
# Created Date: 06-12-2021

# import requests
from requests import Request, Session
from requests.utils import requote_uri

class Connector:
    '''
    A class for connecting to a datasource using USERNAME/PASSWORD authentification
    '''

    def __init__(self, username, password, root_url, retain_auth=False) -> None:
        '''
        Creates and test a connection (Session) to a datasource (API) end point.
        Connections use digested credentials, and supports multiple simultaneous connections (requests).

        Args:
            username (str): username of an active account
            password (srt): password for the account
            root_url (srt): root URL to the API
            retain_auth (bol): retain authorisation headers when connect implements auto-rediction

        '''

        self.username = username
        self.password = password
        self.root_url = root_url
        
        self.header={}

        # controls overwrite redirect of authorisation headers 
        if retain_auth:
            self.session = RetainAuthSession()
        else:
            self.session = Session()

        self.session.auth = (username, password)
        self.status = "Use test_connection() before checking the connection status"


    def test_connection(self):
        '''
        Tests connection and update the "status" attribute upon success.
        
        returns:
            True on sucessful connection
        '''
        
        try:
            test_request= Request('GET', self.root_url, headers=self.header)
            prepare = self.session.prepare_request(test_request)
            response = self.session.send(prepare)
        except ConnectionError:
            print("Connection failed. Check if the roor_url is set correctly and if the remote server is responsive")
        else:
            self.status = response.status_code
            print("Test completed! Status code:", self.status)
            return True


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
        response = self.session.send(prepare, verify=True, stream=stream, timeout=None) # timeout=None, wait forever for a response
        response.raise_for_status

        return response


class RetainAuthSession(Session):
    """" """
    def rebuild_auth(self, prepared_request, response):
        """
        No code here means requests will always preserve the Authorization
        header when redirected.
        Be careful not to leak your credentials to untrusted hosts!
        """