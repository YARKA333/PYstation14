import Utils.shared as shared
import Utils.parents as parents
import Components.component as component
import copy
import Utils.events as events
from Modules.rsi import allp
wanted_comps={}
maxuid=0


class Entity:
  def __init__(self,uid,proto:str=None,components:list=None,verb:bool=False):
    global maxuid
    self.uid=uid
    if uid>=maxuid:
      maxuid=uid+1
    self.pos=[0,0]
    self.rot=0
    comps={}
    self.components={}
    self.meta={"No":"pe"}
    if components:
      comps=typemerge(comps,parents.typedict(components))
    if proto:
      comps=typemerge(parents.typedict(parents.parent(proto)),comps)
      self.meta={"MetaData":{
        "type":"MetaData",
        "proto":proto,
        "comps":comps,
        }}
      comps.update(self.meta)


    for name,comp in comps.items():
      compclass=component.getcomponent(name)
      if compclass:
        compobj=compclass(self,copy.deepcopy(comp))
        self.components.update({name:compobj})
      else:
        alr=dict.get(wanted_comps,name) or 0
        alr+=1
        wanted_comps.update({name:alr})
    if verb:print(f"created entity {uid} with {list(self.components.keys())}")
  def hascomp(self,name):
    return name in self.components
  def comp(self,name):
    return self.components.get(name)

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

def typemerge(old:dict,new:dict)->dict:
  confls=set(old.keys())&set(new.keys())
  result=old.copy()
  result.update(new)
  for confl in confls:
    temp=old[confl].copy()
    temp.update(new[confl])
    result.update({confl:temp})
  return result

def spawn(proto:str|None=None,comps:list[dict]|None=None)->int:
  global maxuid
  if not proto in allp:
    print(f"invalid proto \"{proto}\"")
  uids=shared.get("uids")
  ents=shared.get("entities")
  uid=maxuid
  maxuid+=1
  ents.append(Entity(uid,proto,comps,True))
  uids.append(uid)

def getEcomp(uid,comp):
  uids=shared.get("uids")
  ents=shared.get("entities")
  return ents[uids.index(uid)].comp(comp)

def delete(uid:int):
  events.delentity(uid)
  shared.get("entities").pop(uid)
