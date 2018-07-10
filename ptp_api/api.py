"""
API for PassThePopcorn
More or less a copy of kannibalox's project PTPAPI on GitHub 
Rewritten for Python 3, a better understanding, and as a learning exercise

Features:

Author: Parker Timmerman
"""

import re
import os
import json
import pickle
import logging
from html.parser import HTMLParser
from configparser import ConfigParser
from sys import exit

from bs4 import BeautifulSoup as bs4
import requests

from ptp_config import config
from session import session

LOGGER = logging.getLogger(__name__)

class API():
    """ Object used to access the API """

    def __init__(self, username=None, password=None, passkey=None):
        json = None
        self.cookies_file = os.path.expanduser(config.get('Main', 'cookiesFile'))
        
        LOGGER.info("Initiating login sequence.")
        password = (password or config.get('PTP', 'password'))
        username = (username or config.get('PTP', 'username'))
        passkey  = (passkey or config.get('PTP', 'passkey'))

        if os.path.isfile(self.cookies_file):                      # If cookies exists (a crude test to see if we're logged in)
            self.__loadCookies()
            session.max_redirects = 1
            try:
                req = session.base_get('torrents.php')
            except requests.exceptions.TooManyRedirects:
                if os.path.isfile(self.cookies_file):
                    os.remove(self.cookies_file)                    # Delete the cookies
                session.cookies = requests.cookies.RequestsCookieJar()
            session.max_redirects = 3
        if not os.path.isfile(self.cookies_file):
            if not password or not passkey or not username:
                print("Not enough info provided to login! Exiting...")
                exit(0)
            try:
                req = session.base_post('ajax.php?action=login',
                                        data = {'username': username,
                                                'password': password,
                                                'passkey' : passkey})
                json = req.json()
            except ValueError:
                if req.status_code == 200:
                    print("Could not parse returned JSON data. Exiting...")
                    exit(0)
                else:
                    if req.status_code == 429:
                        LOGGER.critical(req.text.strip())
                    req.raise_for_status()

            if json['Result'] != 'Ok':
                print("Failed to login. Please check the username, password, and passkey. Response: {0}".format(json))

            self.__saveCookies()
            req = session.base_get('index.php')

        print("Login successful!")
        self.current_user_id = re.search(r'user.php\?id=(\d+)', req.text).group(1)  # regex to capture user id that is all digits
        self.auth_key = re.search(r'auth=([0-9a-f]{32})', req.text).group(1)        # regex to capture hex auth key that is 32 digits long


    def __saveCookies(self):
        """ Save requests' cookies to a file """
        with open(self.cookies_file, 'wb') as cookie_file:
            LOGGER.debug("Pickling HTTP cookies to {0}".format(self.cookies_file))
            pickle.dump(requests.utils.dict_from_cookiejar(session.cookies), cookie_file)

    def __loadCookies(self):
        """ Load requests' cookies from a file """
        with open(self.cookies_file, 'rb') as cookie_file:
            LOGGER.debug("Unpickling HTTP cookies from file: {0}".format(self.cookies_file))
            session.cookies = requests.utils.cookiejar_from_dict(pickle.load(cookie_file))
