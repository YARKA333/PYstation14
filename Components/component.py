from Components.IconSmoothComponent import IconSmooth
from Components.TransformComponent import Transform
from Components.SpriteComponent import Sprite
from Components.CableVisualizerComponent import CableVisualizer
from Components.InteractionOutlineComponent import InteractionOutline
from Components.SubFloorHideComponent import SubFloorHide
from Components.DoorComponent import Door
from Components.OccluderComponent import Occluder
from Components.PointLightComponent import PointLight

def getcomponent(name):
  return dict.get(globals(),name)



