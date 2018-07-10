import os
import os.path
import configparser

from io import StringIO


confFile = os.path.join(os.environ['HOME'], '.ptp_api.conf')

default = """
[Main]
baseURL=https://passthepopcorn.me/
cookiesFile=~/.ptp.cookies.txt
downloadDirectory=.
filter=

[Reseed]
action=hard
findBy=filename,title
"""

config = configparser.ConfigParser()
config.readfp(StringIO(default))
config.read(confFile)
