import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import os

# Ключи авторизации.
token = os.environ.get('token')
vk_group_id = os.environ.get('group_id')

API_VERSION = 5.131

vk_session = vk_api.VkApi(token=token, api_version=API_VERSION)
vk_session._auth_token()
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, vk_group_id)