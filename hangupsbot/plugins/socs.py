import hangups
import re
from urllib.request import urlopen

import plugins


def _initialise(bot):
    plugins.register_user_command(["socs"])


def socs(bot, event, *args):
    """Is socs open?"""

    url = "http://issocsopen.com/api"
    page = urlopen(url).read().decode('utf-8')
    bot.send_html_to_conversation(event.conv_id, "Socs is %s" % page)
