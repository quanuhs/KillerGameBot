from sqlalchemy import Column, Integer, ForeignKey, DateTime
from Logic.database import Base
from sqlalchemy.orm import relationship

class Target(Base):
  __tablename__ = 'targets'

  id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)

  game_id = Column(Integer, ForeignKey('games.id'))
  
  hunter_id = Column(Integer, ForeignKey('users.id'))
  hunter = relationship("User", uselist=False, post_update=True, foreign_keys=[hunter_id])

  prey_id = Column(Integer, ForeignKey('targets.hunter_id'))
  
  eliminated_by = Column(Integer, ForeignKey('users.id'))

  eliminated_date = Column(DateTime)

  game = relationship("Game", back_populates="targets", uselist=False)
  prey = relationship("Target", uselist=False, primaryjoin="Target.prey_id == Target.hunter_id", remote_side=[hunter_id], post_update=True)


  def __init__(self, hunter_id, game_id = None):
    self.hunter_id =  hunter_id

    if game_id:
      self.game_id = game_id
  
  def eliminate(self):
    self.game.eliminated(self)

  
  def __str__(self):
    return f"{self.hunter_id} -> {self.prey_id}"


  def __repr__(self):
    return self.__str__()