from Modules.rsi import *
from Utils.mathutils import vec
from Modules.component import BaseComponent,component
from Components.Sprite import Sprite
from Utils.vector2 import Vector
import Utils.events as events
grid=shared.get("globalgrid")


@component
class CableVisualizer(BaseComponent):
  after = ["Sprite"]
  def __init__(self,entity,args):
    #self.entity=entity
    self.uid=entity.uid
    self.sprite:Sprite=entity.comp("Sprite")
    self.dstate=args.get("statePrefix")
    events.followcomp("Transform",self.OnTransform,entity)
    events.subscribe("start",self.startup)
  def OnTransform(self,args):
    self.pos=args.pos
    #self.calcsprites()
  def startup(self,args):self.calcsprites()
  def calcsprites(self):
    #self.entity.comp("Sprite")
    mask=0
    for i in range(4):
      dif=Vector(vec([0,4,2,6][i]))
      pos=self.pos+dif
      for entity in grid.get(str(pos)):
        if not entity: continue
        comp=entity.comp("CableVisualizer")
        if not comp: continue
        if comp.dstate!=self.dstate: continue
        mask+=2**i
        break
    if self.sprite.layers:
      layer=self.sprite.layers[0]
      layer.state=f'{self.dstate}{mask}'