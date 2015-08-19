import re
import requests
import plugins

api = 'https://www.wolframcloud.com/objects/01fcd394-6030-43b5-af22-38823499608e?url={}'

def _initialise(bot):
    plugins.register_user_command(["identify"])

def identify(bot, event, url, *args):
	print(api.format(url))
	r = requests.get(api.format(url))

	concept = re.match(r'"(.*)"', r.text).group(1)

	bot.send_html_to_conversation(event.conv_id, concept)