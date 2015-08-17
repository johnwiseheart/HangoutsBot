import hangups
import re
from urllib.request import urlopen

import plugins


def _initialise(bot):
    plugins.register_user_command(["fortune"])


def fortune(bot, event, *args):
    """Gives a random fortune."""

    url = "http://www.fortunecookiemessage.com"
    html = urlopen(url).read().decode('utf-8')
    m = re.search("class=\"cookie-link\">(<p>)?", html)
    m = re.search("(</p>)?</a>",html[m.end():])
    bot.send_html_to_conversation(event.conv_id, m.string[:m.start()])
