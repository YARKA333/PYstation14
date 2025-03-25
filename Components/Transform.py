from Modules.rsi import *
import math
from Modules.component import BaseComponent,component
from Utils.vector2 import Vector
import Utils.events as events

@component
class Transform(BaseComponent):
  def __init__(self,entity,component:dict):
    entity.xform=self
    self.entity=entity
    self.uid=entity.uid
    result={}
    pos=component.get("pos",None)
    rot=component.get("rot",None)
    self.noRot=component.get("noRot",False)
    anc=component.get("anchored",False)
    events.subscribe("teleport",self.replace,self.uid)
    self.parent=int(component.get("parent","Default"))
    self.maingrid=shared.get("layerMap").uid==self.parent or self.parent=="Default"
    if not self.maingrid:pos=[666,666]
    #anc=dict.get(component,"anchored",None)
    if pos is None:
      print(f"object {self.uid} dont have position")
    self.pos=Vector(pos)
    if anc!=None:
      self.anchor=1
      if self.maingrid:
        grid=shared.get("globalgrid")
        grid.add(str(self.pos),entity)
      #shared.set(grid)
    else:
      self.anchor=0
    if rot!=None:
      self.rot=str_angle(rot)
      component.update({"rot":self.rot})
    else:
      self.rot=0
    if self.maingrid:
      events.call("Transform",self,self.uid)

  def get_dir(self):
    return int((self.rot+45)%360)//90

  def replace(self,args):
    anc=args.get("anc")
    if not anc is None:
      self.anchor=anc
    pos=args.get("pos")
    if not pos is None:
      dos=list(pos)
      if math.isnan(dos[0]) or math.isnan(dos[1]):
        pass
        #self.pos=[0,0]
      else:
        self.pos=Vector(pos)
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

  def __repr__(self):
    return "\n".join([
      f"pos: {self.pos}",
      f"rot: {self.rot}",
      "Anchored" if self.anchor else "Loose"
      f"Parent: {self.parent}"
    ])
