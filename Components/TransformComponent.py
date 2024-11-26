import Utils.events as events
import Utils.shared as shared
from Modules.rsi import *

class Transform:
  def __init__(self,entity,component:dict):
    self.uid=entity.uid
    result={}
    pos=component.get("pos",None)
    rot=component.get("rot",None)
    anc=component.get("anchored",False)
    self.parent=int(component.get("parent",0))
    self.maingrid=shared.get("layerMap").uid==self.parent
    self.maingrid=True
    if not self.maingrid:pos=[666,666]
    #anc=dict.get(component,"anchored",None)
    if type(pos)==list:
      self.pos=pos
      component.update({"pos":self.pos})
    elif pos!=None:
      self.pos=[float(a) for a in pos.split(",")]
      component.update({"pos":self.pos})
    else:
      print("lox")
      self.pos=[0,0]
    if anc!=None:
      self.anchor=1
      if self.maingrid:
        grid=shared.get("globalgrid")
        grid.add(str(self.pos),self.uid)
      #shared.set(grid)
    else:
      self.anchor=0
    if rot!=None:
      self.rot=angle(rot)
      component.update({"rot":self.rot})
    else:
      self.rot=0
    if self.maingrid:
      events.call("Transform",self,self.uid)

