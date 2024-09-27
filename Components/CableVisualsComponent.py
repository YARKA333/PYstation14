import Utils.events as events
import Utils.shared as shared
grid=shared.get("globalgrid")

class CableVisuals:
  def __init__(self,entity,args):
    self.dstate=dict.get(args,"statePrefix")
    events.followcomp("Transform",self.OnTransform,entity)
  def OnTransform(self,args):
    self.trans=args
    self.scan()

  def scan(self):
    self.nbrs=[]
    for i in range(4):
      dif=vec([0,4,2,6][i])
      pos=[dif[e]+self.trans.pos[e] for e in [0,1]]
      uids=grid.get(str(pos))
      for uid in uids:
        entity=entityModule.find(uid)
        if not entity: continue
        comp=entity.comp("CableVisuals")
        if not comp: continue
        if comp.ctype!=self.ctype: continue
        self.nbrs.append(1)
        break
      else:
        self.nbrs.append(0)
