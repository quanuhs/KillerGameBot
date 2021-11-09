import os
from Logic.database import DATABASE_NAME, create_db

from Bot.bot_settings import longpoll
from Bot.vk_bot import vk_resolve_commands
from vk_api.bot_longpoll import VkBotEventType


from Logic.game import Game
from Logic.user import User
from Logic.target import Target


def main():

  db_is_created = os.path.exists(DATABASE_NAME)
  if not db_is_created:
    create_db()


  for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW:
      vk_resolve_commands(event)
      
      
  

if __name__ == "__main__":
  main()
  