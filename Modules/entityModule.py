import Utils.shared as shared
import Utils.parents as parents
import Components.component as component
wanted_comps={}

class Entity:
  def __init__(self,uid,id:str=None,components:list=None):
    self.uid=uid
    self.pos=[0,0]
    self.rot=0
    self.proto=id
    comps={}
    self.components={}
    if id:
      comps.update(parents.typedict(parents.parent(id)))
    if components:
      comps.update(parents.typedict(components))
    for name,comp in comps.items():
      compclass=component.getcomponent(name)
      if compclass:
        compobj=compclass(self,comp)
        self.components.update({name:compobj})
      else:
        alr=dict.get(wanted_comps,name) or 0
        alr+=1
        wanted_comps.update({name:alr})
  def hascomp(self,name):
    return name in self.components.keys()
  def comp(self,name):
    return dict.get(self.components,name)

def find(uid):
  uids=shared.get("uids")
  ents=shared.get("entities")
  if not uid in uids:
    print(f"no {uid} in uids")
    return
  uidindex=uids.index(uid)
  if uidindex>=len(ents):
    print(f"uid({uid}) in place {uidindex}/{len(uids)} is higher than ents len {len(ents)}")
    return
  return ents[uidindex]