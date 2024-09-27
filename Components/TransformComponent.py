import Utils.events as events
import Utils.shared as shared
from Modules.rsi import *

class Transform:
  def __init__(self,entity,component):
    self.uid=entity.uid
    result={}
    pos=dict.get(component,"pos",None)
    rot=dict.get(component,"rot",None)
    #anc=dict.get(component,"anchored",None)
    anc=1
    if pos!=None:
      self.pos=[float(a) for a in pos.split(",")]
      entity.__setattr__("pos",self.pos)
      component.update({"pos":self.pos})
    else:
      self.pos=[0,0]
    if anc!=None:
      self.anchor=1
      grid=shared.get("globalgrid")
      grid.add(str(self.pos),self.uid)
      #shared.set(grid)
    else:
      self.anchor=0
    if rot!=None:
      self.rot=angle(rot)
      entity.__setattr__("rot",self.rot)
      component.update({"rot":self.rot})
    else:
      self.rot=0
    events.call("Transform",self,self.uid)

