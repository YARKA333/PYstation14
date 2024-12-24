from Components.IconSmoothComponent import IconSmooth
from Components.TransformComponent import Transform
from Components.SpriteComponent import Sprite
from Components.CableVisualizerComponent import CableVisualizer
from Components.InteractionOutlineComponent import InteractionOutline
from Components.SubFloorHideComponent import SubFloorHide
from Components.DoorComponent import Door
from Components.MetaDataComponent import MetaData
from Components.OccluderComponent import Occluder
from Components.PointLightComponent import PointLight
from Components.PhysicsComponent import Fixtures,Physics
from Components.AppearanceComponent import Appearance,GenericVisualizer
from Components.ComputerComponent import Computer

def getcomponent(name):
  return dict.get(globals(),name)



