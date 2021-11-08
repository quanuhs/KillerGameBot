from sqlalchemy import Column, Integer, String

from Logic.database import Base
from Logic.game import Game
from sqlalchemy.orm import relationship

class User(Base):
  __tablename__ = 'users'

  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
  user_id = Column(Integer)
  nickname = Column(String)
  
  games_played = relationship("Game", secondary="game_players", back_populates="players")

  games_hosted = relationship("Game", back_populates="host")

  def __init__(self, user_id:int):
    self.user_id =  user_id
  

  def create_game(self) -> Game:
    _game = Game()
    self.games_hosted.append(_game)
    self.games_played.append(_game)
    
    return _game


  def __str__(self):
    return f"user@id{self.user_id}"

  def __repr__(self):
    return self.__str__()