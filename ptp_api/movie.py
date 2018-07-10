import re

from session import session
from torrent import Torrent

from PIL import Image
from io import BytesIO

class Movie():
    """ A class representing a movie object """

    def __init__(self, data):
        self.torrents = []
        self.data = data
        self.coverArt = None
       
        self._convJsonTorrents()
        self._loadCoverArt()

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value
    
    def _convJsonTorrents(self):
        """Utility function to normalize data"""

        if self.data['Torrents']:
            torrents = self.data['Torrents']
            for t in torrents:
                if 'RemasterTitle' not in t:
                    t['RemasterTitle'] = ''
            self.data['Torrents'] = [Torrent(data=t) for t in torrents]
            
    def _loadCoverArt(self):
        """ Utility function that gets the cover art from the movie """
        cover = self['Cover']
        cover = re.search(r'(https*:\/\/ptpimg.me\/[0-9a-z]{6}.jpg)', cover).group(1)

        req = session.get(cover)
        self.coverArt = req.content
        
