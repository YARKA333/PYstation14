from rsi import *
import events
import shared
from IconSmoothComponent import IconSmooth
from TransformComponent import Transform
from SpriteComponent import Sprite
from CableVisualsComponent import CableVisuals

def getcomponent(name):
  return dict.get(globals(),name)



