import re
import requests
import plugins

api = 'https://www.wolframcloud.com/objects/01fcd394-6030-43b5-af22-38823499608e?url={}'

def _initialise(bot):
    plugins.register_user_command(["identify"])
    plugins.register_handler(_scan_for_images, type="message")

def identify(bot, event, url, *args):
    print(api.format(url))
    r = requests.get(api.format(url))

    response = re.match(r'"(.*)"', r.text)

    if response is not None:
        concept = response.group(1)
    else:
        concept = 'Could not parse response: {}'.format(r.text)

    bot.send_html_to_conversation(event.conv_id, concept)

def _scan_for_images(bot, event, command):
    if event.user.is_self:
        return

    if " " in event.text:
        """immediately reject anything with spaces, must be a link"""
        return

    probable_image_link = False
    event_text_lower = event.text.lower()

    if re.match("^(https?://)?([a-z0-9.]*?\.)?imgur.com/", event_text_lower, re.IGNORECASE):
        """imgur links can be supplied with/without protocol and extension"""
        probable_image_link = True

    elif event_text_lower.startswith(("http://", "https://")) and event_text_lower.endswith((".png", ".gif", ".gifv", ".jpg")):
        """other image links must have protocol and end with valid extension"""
        probable_image_link = True

    if probable_image_link:
        identify(bot, event, event.text, None)