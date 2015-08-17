import logging
import re

import plugins


logger = logging.getLogger(__name__)


_lookup = {}


def _initialise(bot):
    plugins.register_handler(_scan_for_triggers)



def _scan_for_triggers(bot, event, command):

    text = event.text.lower()
    m = re.match(r'^thanks[, ]+(.*)$', text, re.I)
    if m:
        subject = m.group(1).lower()
        subject = re.sub(r'^(y|[^aeiouy]+|)', 'th', subject)
        bot.send_html_to_conversation(event.conv_id, subject)
