import Utils.events as events
import Utils.shared as shared
from Modules.rsi import *
import Modules.entityModule as entityModule
grid=shared.get("globalgrid")

class CableVisualizer:
  def __init__(self,entity,args):
    self.uid=entity.uid
    self.dstate=dict.get(args,"statePrefix")
    events.followcomp("Transform",self.OnTransform,entity)
    events.subscribe("start",self.startup)
  def OnTransform(self,args):
    self.trans=args
    self.calcsprites()
  def startup(self,args):self.calcsprites()
  def calcsprites(self):
    mask=0
    for i in range(4):
      dif=vec([0,4,2,6][i])
      pos=[dif[e]+self.trans.pos[e] for e in [0,1]]
      uids=grid.get(str(pos))
      for uid in uids:
        entity=entityModule.find(uid)
        if not entity: continue
        comp=entity.comp("CableVisualizer")
        if not comp: continue
        if comp.dstate!=self.dstate: continue
        mask+=2**i
        break
    events.call("setspritelayer",{"state":f'{self.dstate}{mask}'},self.uid)