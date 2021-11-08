from vk_api.keyboard import VkKeyboard, VkKeyboardColor

def main_menu() -> VkKeyboard:
  _keyboard:VkKeyboard = VkKeyboard()
  
  # _keyboard.add_button("Присоединиться", VkKeyboardColor.POSITIVE, payload={"command": "!join"})
  # _keyboard.add_line()
  _keyboard.add_button("Создать лобби", VkKeyboardColor.PRIMARY, payload={"command": "!create"})
  _keyboard.add_line()
  _keyboard.add_button("Правила", VkKeyboardColor.SECONDARY, payload={"command": "!rules"})
  _keyboard.add_button("Удалить аккаунт", VkKeyboardColor.NEGATIVE, payload={"command": "!remove"})

  return _keyboard


def host_start_panel(game_id:int) -> VkKeyboard:
  _game_data = {"game_id": game_id}
  _keyboard:VkKeyboard = VkKeyboard()

  _keyboard.add_button("Начать игру", VkKeyboardColor.POSITIVE, payload={"command": "!start", "data": _game_data})
  _keyboard.add_button("Сменить код", VkKeyboardColor.NEGATIVE, payload={"command": "!change", "data": _game_data})

  _keyboard.add_line()
  _add_lobby_info(_keyboard, _game_data)
  _keyboard.add_line()
  _add_footer(_keyboard, _game_data)

  return _keyboard


def player_start_panel(game_id:int) -> VkKeyboard:
  _game_data = {"game_id": game_id}
  _keyboard:VkKeyboard = VkKeyboard()

  _add_lobby_info(_keyboard, _game_data)
  _keyboard.add_line()
  _add_footer(_keyboard, _game_data)

  return _keyboard


def player_game_panel(game_id:int) -> VkKeyboard:
  _game_data = {"game_id": game_id}
  _keyboard:VkKeyboard = VkKeyboard()

  _add_game_info(_keyboard, _game_data)
  _keyboard.add_line()
  _add_footer(_keyboard, _game_data)

  return _keyboard


def host_game_panel(game_id:int) -> VkKeyboard:
  _game_data = {"game_id": game_id}
  _keyboard:VkKeyboard = VkKeyboard()

  _add_game_info(_keyboard, _game_data)
  _keyboard.add_line()
  _keyboard.add_button("Завершить игру", VkKeyboardColor.PRIMARY, payload={"command": "!stop", "data": _game_data})
  _keyboard.add_line()
  _add_footer(_keyboard, _game_data)

  return _keyboard


def _add_footer(_keyboard:VkKeyboard, game_data):
  _keyboard.add_button("Правила", VkKeyboardColor.SECONDARY, payload={"command": "!rules"})
  _keyboard.add_button("Выйти", VkKeyboardColor.NEGATIVE, payload={"command": "!leave", "data": game_data})

  return _keyboard


def _add_lobby_info(_keyboard:VkKeyboard, game_data):
  _keyboard.add_button("Показать код", VkKeyboardColor.PRIMARY, payload={"command": "!code", "data": game_data})
  _keyboard.add_button("Список игроков", VkKeyboardColor.PRIMARY, payload={"command": "!players", "data": game_data})

  return _keyboard


def _add_game_info(_keyboard:VkKeyboard, game_data):
  _keyboard.add_button("Цель", VkKeyboardColor.NEGATIVE, payload={"command": "!target", "data": game_data})
  _keyboard.add_button("Список игроков", VkKeyboardColor.PRIMARY, payload={"command": "!players", "data": game_data})

  return _keyboard


def target_keyboard(game_id:int) -> VkKeyboard:
  _game_data = {"game_id": game_id}
  _keyboard:VkKeyboard = VkKeyboard(inline=True)
  _keyboard.add_button("Цель устранена", VkKeyboardColor.NEGATIVE, payload={"command": "!submit", "data": _game_data})

  return _keyboard


def game_confirm_death(game_id:int, hunter_id:int) -> VkKeyboard:
  _game_data = {"game_id": game_id, "hunter_id": hunter_id}
  _keyboard:VkKeyboard = VkKeyboard(inline=True)
  _keyboard.add_button("Подтверждаю", VkKeyboardColor.POSITIVE, payload={"command": "!confirm", "data": _game_data})

  return _keyboard