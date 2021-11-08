from sqlalchemy import Column, Integer, Boolean, ForeignKey, Table, String
from Logic.database import Base
from sqlalchemy.orm import relationship

from Logic.target import Target

import datetime
import random

import uuid

def generate_password(string_length=5):
    _random = str(uuid.uuid4())
    _random = _random.replace("-","")
    _random = _random.upper()
    return _random[0:string_length]


association_table_game_players = Table('game_players', Base.metadata,
    Column('game_id', Integer, ForeignKey('games.id', ondelete="CASCADE")),
    Column('user_id', Integer, ForeignKey('users.id'))
)

class Game(Base):
  __tablename__ = 'games'

  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)

  host_id = Column(Integer, ForeignKey("users.id"))
  host = relationship("User", uselist=False, back_populates="games_hosted")
  
  players = relationship("User", secondary="game_players", back_populates="games_played")
  max_players = Column(Integer)

  has_started = Column(Boolean, default=False)

  targets = relationship("Target", back_populates="game", cascade="all, delete-orphan")
  password = Column(String(5), unique=True)

  def __init__(self, max_players:int=None):
    if max_players:
      self.max_players = max_players
    
    self.change_password()
  
  

  # Создаёт игру - выдаёт каждому игроку цель
  def start_game(self):
    _players_amount:int = len(self.players)
    _players = random.sample(self.players, len(self.players))

    for i in range(_players_amount-1):
      _target = Target(_players[i].id)
      _target.prey_id = _players[i+1].id
      self.targets.append(_target)
    
    self.targets.append(Target(_players[-1].id))
    self.targets[-1].prey_id = self.targets[0].hunter_id
  
    self.has_started = True



  def eliminated(self, target):

    if target.hunter_id == target.prey_id:
      return
    
    target.prey.eliminated_date = datetime.datetime.now()
    target.prey.eliminated_by = target.hunter_id
    target.prey_id = target.prey.prey_id
  


  def change_password(self):
    self.password = generate_password(5)
  


  def remove_player(self, player):
    if self.has_started:
        for target in self.targets:
          if target.prey_id == player.id:
            self.eliminated(target)
            target.prey.eliminated_by = None
            
            break
    
    self.players.remove(player)



  def get_player_headcount(self, player):    
    _res = []
    if self.has_started:
      for target in self.targets:
        if target.eliminated_by == player.id:
          _res.append(target)
    
    return _res
  
