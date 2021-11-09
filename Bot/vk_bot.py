from Bot.bot_settings import vk
import Bot.vk_keyboards as vk_keys

from Logic.database import Session
from Logic.game import Game
from Logic.user import User
from Logic.target import Target

import json


def vk_resolve_commands(event):
  # Начинаем сессию с БД.
  # Id пользователя ВК.

  session = Session()
  user_id = event.object.message.get("from_id")

  # Находим в БД пользователя с VK user_id.
  user = session.query(User).filter(User.user_id == user_id).one_or_none()

  # Если НЕ находим пользователя в БД, регестрируем его
  if user == None:
    user = register_user(user_id, session)

    vk.messages.send(
      peer_id = user.user_id,
      message = "Добро пожаловать!",
      keyboard = vk_keys.main_menu().get_keyboard(),
      random_id = 0
    )
  

  # Получаем payload (в случае, если используется клавиатура)
  payload = event.object.message.get("payload")

  if payload:
    payload = json.loads(payload)
    resolve_commands(user, payload.get("command"), payload, event, session)

  else:
    
    # Обробатываем сообщение от пользователя.
    request = str(event.object.message.get("text"))
    resolve_commands(user, request, {}, event, session)
    session.close()



def register_user(user_id, session) -> User:
  user:User = User(user_id)

  session.add(user)
  session.commit()

  return user
  


def resolve_commands(user, command:str, data, event, session):

  if len(data) == 0:
    if command.startswith("!join"):
      if len(user.games_played) == 0:
        lobby_join(user, command.replace("!join ", ""), event, session)
    
    elif command == "!menu":
      vk.messages.send(
        user_id = user.user_id,
        keyboard = vk_keys.main_menu().get_keyboard(),
        random_id = 0,
        message = "Главное меню."
      )

    return

  if command == "!create":
    create_game(user, event, session)
  
  elif command == "!target":
    game_get_target(user, data.get("data").get("game_id"), event, session)

  elif command == "!leave":
    leave_game(user, data.get("data").get("game_id"), event, session)
  
  elif command == "!submit":
    game_submit(user, data.get("data").get("game_id"), event, session)
  
  elif command == "!erase_my_data":
    print("clears user data")
  
  elif command == "!confirm":
    game_confirm_death(user, data.get("data").get("game_id"), data.get("data").get("hunter_id"), event, session)

  elif command == "!host_kick":
    print("host kicked user")

  elif command == "!rules":
    vk.messages.send(
      user_id = user.user_id,
      message = "Правила игры\nvk.com/@icebreaker4bonch-pravila-igry-killer",
      random_id = 0
    )
  
  elif command == "!change":
    lobby_change_code(user, data.get("data").get("game_id"), event, session)
  
  elif command == "!code":
    lobby_show_code(user, data.get("data").get("game_id"), event, session)
  
  elif command == "!stop":
    lobby_finish(user, data.get("data").get("game_id"), event, session)

  elif command == "!start":
    lobby_start(user, data.get("data").get("game_id"), event, session)

  elif command == "!players":
    lobby_players(user, data.get("data").get("game_id"), event, session)
  

def create_game(user, event, session):
  if len(user.games_played) == 0:
    _game = user.create_game()
    session.commit()
    
    vk.messages.send(
      peer_id = user.user_id,
      message = "Игра создана!\n\nКод для подключения: %s\nКоманда: !join %s" % (_game.password, _game.password),
      keyboard = vk_keys.host_start_panel(_game.id).get_keyboard(),
      random_id = 0
    )

    return
  
  vk.messages.send(
      peer_id = user.user_id,
      message = "Вы превысили лимит на создание игр.\nЕсли это не так, обратитесь к администратору.",
      random_id = 0
    )

def lobby_show_code(user, game_id, event, session):
  _game:Game = session.query(Game).filter(Game.id==game_id, Game.players.any(id=user.id), Game.has_started == False).one_or_none()

  if _game:
    vk.messages.send(
      peer_id = user.user_id,
      message = "Код для подключения: %s\nКоманда: !join %s" % (_game.password, _game.password),
      random_id = 0
    )

def lobby_change_code(user, game_id, event, session):
  _game:Game = session.query(Game).filter(Game.id==game_id, Game.host_id == user.id, Game.has_started == False).one_or_none()

  if _game:
    _game.change_password()
    session.commit()

    vk.messages.send(
      peer_id = user.user_id,
      message = "Код изменён!\nНовый код: %s" % _game.password,
      random_id = 0
    )


def leave_game(user, game_id, event, session):
  # Игрок покидает лобби/игру
  _game = session.query(Game).filter(Game.id==game_id, Game.players.any(id=user.id)).one_or_none()
  
  if _game is None:
    vk.messages.send(
      peer_id = user.user_id,
      message = "Игра, которую вы хотите покинуть, не найдена.",
      random_id = 0
    )
    return
  
  if _game.host_id == user.id:
    vk.messages.send(
      user_ids = ",".join(str(x.user_id) for x in _game.players),
      message = "Создатель лобби вышел.\nЛобби распущено.",
      keyboard = vk_keys.main_menu().get_keyboard(),
      random_id = 0
    )

    session.delete(_game)
    
  
  else:
    _game.remove_player(user)

    vk.messages.send(
      user_ids = ",".join(str(x.user_id) for x in _game.players if x.user_id != user.user_id),
      message = "@id%s (Игрок) покинул лобби.\nВ игре осталось: %s игроков." % (user.user_id, len(_game.players)),
      random_id = 0
    )

    vk.messages.send(
      user_id = user.user_id,
      message = "Вы вышли из игры.",
      random_id = 0,
      keyboard = vk_keys.main_menu().get_keyboard()
    )

  session.commit()


def lobby_players(user, game_id, event, session):
  # Показывает список игроков в лобби
  _game:Game = session.query(Game).filter(Game.id==game_id, Game.players.any(id=user.id)).one_or_none()
  
  vk.messages.send(
    user_id = user.user_id,
    message="Игроков в лобби: %s.\n%s" % (len(_game.players), get_all_players_str(_game.players, _game.host.user_id)),
    random_id = 0
  )

def get_all_players_str(players, host_id=None):
  # Запрашивает информацию о пользователях VK и выдаёт пронумерованный список пользователей.
  users = vk.users.get(
    user_ids = ",".join(str(x.user_id) for x in players)
  )

  _result:str = ""
  for i in range(len(users)):
    _result += f"{i+1}. {'★' if users[i].get('id') == host_id else ''} @id{users[i].get('id')} ({users[i].get('first_name')} {users[i].get('last_name')})\n"
  
  return _result


def lobby_join(user, game_password, event, session):
  # Подключает игрока к лобби
  if len(game_password) > 5:
    return
  
  _game:Game = session.query(Game).filter(Game.password == game_password, Game.has_started == False).one_or_none()
  
  if _game:
    vk.messages.send(
      user_ids = ",".join(str(x.user_id) for x in _game.players if x.user_id != user.user_id),
      message = "@id%s (Игрок) подключился к лобби.\nВ игре: %s игроков." % (user.user_id, len(_game.players)+1),
      random_id = 0
    )

    vk.messages.send(
      user_id = user.user_id,
      message = "Вы подключились к лобби %s." % (game_password),
      keyboard = vk_keys.player_start_panel(_game.id).get_keyboard(),
      random_id = 0
    )
    
    _game.players.append(user)
    session.commit()
  
  else:
    vk.messages.send(
    user_id = user.user_id,
    message="Игры с таким кодом не найдено или она уже началсь.",
    random_id = 0
  )


def lobby_start(user, game_id, event, session):
  # Начинает игру
  _game:Game = session.query(Game).filter(Game.id==game_id, Game.host_id == user.id).one_or_none()


  if _game:

    if _game.has_started:
      vk.messages.send(
          user_id =  user.user_id,
          message = "Игра уже началась.",
          random_id = 0
        )

      return

    # НЕ ЗАБЫТЬ ИСПРАВИТЬ!
    # ТОЛЬКО ДЛЯ ДЕБАГА -> ДОЛЖНО БЫТЬ > 2!
    if len(_game.players) >= 2:

      vk.messages.send(
        user_ids = ",".join(str(x.user_id) for x in _game.players if x.user_id != user.user_id),
        message = "Игра началась!",
        keyboard = vk_keys.player_game_panel(_game.id).get_keyboard(),
        random_id = 0
      )

      vk.messages.send(
        user_id =  user.user_id,
        message = "Игра началась!\nВам доступено управление игрой.",
        keyboard = vk_keys.host_game_panel(_game.id).get_keyboard(),
        random_id = 0
      )

      _game.start_game()
      session.commit()
    
    else:
       vk.messages.send(
        user_id =  user.user_id,
        message = "Для начала игры необходимо минимум 3 игрока.\nСейчас игроков: %s." % len(_game.players),
        random_id = 0
      )

  

def game_get_target(user, game_id, event, session):
  # Получаем цель пользователя в игре
  _game:Game = session.query(Game).filter(Game.id==game_id, User.games_played.any(id=game_id), Game.has_started==True).one_or_none()
  
  if _game:
    _target:Target = session.query(Target).filter(Target.hunter_id == user.id, Target.game_id == game_id, Target.eliminated_by == None).one_or_none()
    
    if _target:
      prey_user_vk = vk.users.get(
        user_ids = str(_target.prey.hunter.user_id)
      )

      vk.messages.send(
        user_id =  user.user_id,
        message = "Ваша цель: @id%s (%s %s)." % (_target.prey.hunter.user_id, prey_user_vk[0].get('first_name'), prey_user_vk[0].get('last_name')),
        keyboard = vk_keys.target_keyboard(game_id).get_keyboard(),
        random_id = 0
      )


def game_submit(user, game_id, event, session):
  # Сдаём цель -> выполняем "контракт"

  _game:Game = session.query(Game).filter(Game.id==game_id, User.games_played.any(id=game_id), Game.has_started==True).one_or_none()

  if _game:
    _target:Target = session.query(Target).filter(Target.hunter_id == user.id, Target.game_id == game_id, Target.eliminated_by == None).one_or_none()
  
    if _target:
      vk.messages.send(
        user_id =  user.user_id,
        message = "Ждём подтверждения у вашей цели.",
        random_id = 0
      )

      vk.messages.send(
        user_id =  _target.prey.hunter.user_id,
        message = "Вы были устранены.\nЕсли это так - подтвердите нажав на кнопку.",
        keyboard = vk_keys.game_confirm_death(game_id, user.id).get_keyboard(),
        random_id = 0
      )


def game_confirm_death(user, game_id, hunter_id, event, session):
  # Цель подтверждает нейтрализацию

  _game:Game = session.query(Game).filter(Game.id==game_id, User.games_played.any(id=game_id), Game.has_started==True).one_or_none()

  if _game:
    _target:Target = session.query(Target).filter(Target.hunter_id == hunter_id, Target.prey_id == user.id, Target.game_id == game_id, Target.eliminated_by == None).one_or_none()
  
    if _target:
      vk.messages.send(
        user_id =  user.user_id,
        message = "Вы были устранены.\nПечально.",
        random_id = 0
      )

      vk.messages.send(
        user_id =  _target.hunter.user_id,
        message = "Цель устранена.\nТеперь вы можете посмотреть вашу новую цель!",
        random_id = 0
      )

      _game.eliminated(_target)
      session.commit()


def lobby_finish(user, game_id, event, session):
  _game:Game = session.query(Game).filter(Game.id==game_id, Game.host_id == user.id, Game.has_started==True).one_or_none()

  if _game is None:
    return

  users_headcount = session.query(User, Target).join(Target, (Target.eliminated_by == User.id)).filter(Target.game_id == _game.id).all()


  _dict = {}
  for headcount in users_headcount:
    _user:User = headcount[0]
    _target:Target = headcount[1]

    if _dict.get(_user.user_id):
      _dict[_user.user_id].append(_target)
    else:
      _dict[_user.user_id] = [_target]

  _dict = dict(sorted(_dict.items(), key=lambda item: len(item[1]), reverse=True))

  users = vk.users.get(
    user_ids = ",".join(str(x) for x in _dict.keys())
  )

  _msg_text:str = ""
  _index:int = 0
  for user_id in _dict:
    _msg_text += f"{_index+1}. @id{user_id} ({users[_index].get('first_name')} {users[_index].get('last_name')}) -> {len(_dict[user_id])}\n"

    _index += 1
  
  if _msg_text == "":
    _msg_text = "\n\nПобедила дружба!"
  
  else:
    _msg_text = "\n\nСписок устранений:\n" + _msg_text

  vk.messages.send(
      user_ids = ",".join(str(x.user_id) for x in _game.players),
      message = "Игра завершена!" + _msg_text,
      keyboard = vk_keys.main_menu().get_keyboard(),
      random_id = 0
    )
  
  session.delete(_game)
  session.commit()
  
