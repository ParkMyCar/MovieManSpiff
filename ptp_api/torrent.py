import re
import os

from session import session
from ptp_config import config

class Torrent():
    """ Class representing a single torrent of a movie """

    def __init__(self, data):
        self.data = data
        self.ID = data['Id']

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def __str__(self):
        release = self.data['ReleaseName']
        res = self.data['Resolution']
        gb = "%.2f" % (int(self.data['Size']) / 1024 / 1024 / 1024)
        src = self.data['Source']
        return "{0} | Resolution: {1}, Size: {2}GB, Source: {3}".format(release, res, gb, src)

    def __repr__(self):
        return self.__str__()

    def download(self):
        """ Download the torrent file to disk """
        req = session.base_get("torrents.php",
                                params={'action': 'download',
                                        'id': self.ID})
        dest = config.get('Main', 'downloadDirectory')
        filename = re.search(r'filename="(.*)"', req.headers['Content-Disposition']).group(1)   # Get the filename (something.torrent)
        dest = os.path.join(dest, filename)
        with open(dest, 'wb') as fileh:
            fileh.write(req.content)
        print("Downloaded {0} to {1}".format(filename, dest))
        
        return True


