import Modules.component as component
from Components.Transform import Transform
from Components.MetaData import MetaData
import Utils.shared as shared
import Utils.parents as parents
import copy
import Utils.events as events
from Modules.rsi import allp
from time import time
from typing import TypeVar
wanted_comps={}
maxuid=0


class Entity:
  xform:Transform
  meta:MetaData
  def __init__(self,uid,proto:str=None,components:list=None,verb:bool=False,watches=None):
    dt=time()
    global maxuid
    self.uid=uid
    if uid>=maxuid:
      maxuid=uid+1
    self.pos=[0,0]
    self.rot=0
    comps={}
    self.components={}
    meta={"No":"pe"}
    if components:
      comps=typemerge(comps,parents.typedict(components))
    if proto:
      comps=typemerge(parents.typedict(parents.parent(proto)),comps)
      meta={"MetaData":{
        "type":"MetaData",
        "proto":proto,
        "comps":comps,
        }}
      comps.update(meta)
    compclasses=[component.getcomponent(name) for name in comps]
    classes=sort_classes([c for c in compclasses if c])
    if watches:
      watches.add("common",time()-dt)
    for compclass in classes:
      dt=time()
      name=compclass.__name__
      compobj=compclass(self,copy.deepcopy(comps[name]))
      self.components.update({name:compobj})
      match name:
        case "Transform":
          self.xform=compobj
        case "MetaData":
          self.meta=compobj
  #    else:
  #      alr=dict.get(wanted_comps,name) or 0
  #      alr+=1
  #      wanted_comps.update({name:alr})
      if watches:
        watches.add(compclass.__name__,time()-dt)
    if verb:print(f"created entity {uid} with {list(self.components.keys())}")
  def hascomp(self,name):
    return name in self.components
  def comp(self,name)->component.BaseComponent:
    return self.components.get(name)
  def __repr__(self):
    return f"<e-{self.uid}>"
  def __str__(self):
    return f"{self.meta.name} ({self.uid}, {self.meta.proto})"

def find(uid:int)->Entity:
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


from collections import defaultdict, deque


def sort_classes(classes):
  # Создаем граф и список входящих ребер
  graph=defaultdict(list)
  in_degree={cls.__name__:0 for cls in classes}
  class_names={cls.__name__ for cls in classes}
  for cls in classes:
    for before_cls in cls.before:
      if before_cls in class_names:
        graph[before_cls].append(cls.__name__)
        in_degree[cls.__name__]+=1

    for after_cls in cls.after:
      if after_cls in class_names:
        graph[cls.__name__].append(after_cls)
        in_degree[after_cls]+=1

  # Находим все вершины с нулевой степенью входа
  queue=deque([name for name,degree in in_degree.items() if degree==0])

  # Сортируем классы
  sorted_classes=[]
  while queue:
    name=queue.popleft()
    sorted_classes.append(next(cls for cls in classes if cls.__name__==name))

    for neighbor in graph[name]:
      in_degree[neighbor]-=1
      if in_degree[neighbor]==0:
        queue.append(neighbor)

  # Если остались вершины с ненулевой степенью входа, то граф содержит суслика
  if len(sorted_classes)!=len(classes):
    raise ValueError("Граф содержит суслика")

  return reversed(sorted_classes)