import Utils.shared as shared
import Utils.events as events
from Modules.component import BaseComponent,component
from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from Components.SpriteComponent import Sprite

@component
class SubFloorHide(BaseComponent):
  after = ["Transform","Sprite"]
  def __init__(self,entity,args):
    self.sprite=None
    self.pos=None
    self.map=shared.get("layerMap")
    self.uid=entity.uid
    self.sprite:Sprite=entity.comp("Sprite")
    events.followcomp("Transform",self.Transform,entity)
    events.subscribe("Sprite",self.Sprite,self.uid)
    self.calc()
  def Transform(self,args):
    self.pos=args.pos
    self.calc()
  def Sprite(self,args):
    self.calc()
  def calc(self):
    if not (self.pos and self.sprite):return
    tile=self.map.getTile([self.pos[0]-.5,self.pos[1]-.5])
    if not tile:print(f"no tile {self.pos}?")
    else:
      #self.visible=tile.isSubfloor
      #events.call("setvis",tile.isSubfloor,self.uid)
      events.call("setvis",True,self.uid)
      for layer in self.sprite.layers:
        if not "enum.SubfloorLayers.FirstLayer" in layer.map:
          layer.visible=tile.isSubfloor