import Utils.events as events
from Modules.rsi import rotate_vector

component={
  "color":"#FFFFFF",
  "radius":5,
  "energy":1,
  "enabled":True,
  "castShadows":True,
}


class PointLight:
  def __init__(self,entity,args):
    self.comp=component.copy()
    self.comp.update(args)
    events.followcomp("Transform",self.onTransform,entity)
  def onTransform(self,comp):
    offset=[float(a)*0.75 for a in self.comp.get("offset",'0,0').split(",")]
    self.rot=comp.rot
    self.comp["radius"]=min(self.comp["radius"],16)
    rotoffset=rotate_vector(offset,self.rot)
    self.comp.update({"gpos":[comp.pos[e]+rotoffset[e] for e in [0,1]]})
    if not self.comp["enabled"]:return
    if not self.comp["castShadows"]:return
    events.call("addLightSource",self.comp)
