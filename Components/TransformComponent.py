import Utils.events as events
import Utils.shared as shared
from Modules.rsi import *
import math
class Transform:
  def __init__(self,entity,component:dict):
    self.uid=entity.uid
    result={}
    pos=component.get("pos",None)
    rot=component.get("rot",None)
    anc=component.get("anchored",False)
    events.subscribe("teleport",self.replace,self.uid)
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
      print("no position for object",self.uid)
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

  def replace(self,args):
    anc=args.get("anc")
    if not anc is None:
      self.anchor=anc
    pos=args.get("pos")
    if not pos is None:
      pos=list(pos)
      if math.isnan(pos[0]) or math.isnan(pos[1]):
        pass
        #self.pos=[0,0]
      else:
        self.pos=list(pos)
    rot=args.get("rot")
    if not rot is None:
      rot=float(rot)
      if math.isnan(rot):
        pass
        #self.rot=0
      else:
        self.rot=rot
    par=args.get("par")
    if not par is None:
      self.parent=par
    events.call("Transform",self,self.uid)
