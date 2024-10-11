import ruamel.yaml

from Modules.rsi import *
import pickle

chains=[]
chainmap=[]

with open("kake/entity.pk","rb") as file:
  allp=pickle.load(file)

def typedict(todict:list)->dict:
  result={}
  try:
    for a in todict:
      result.update({a["type"]:a})
  except:pass
  return result

def merge(old:list,new:list)->list:
  part=typedict(old)
  compt=typedict(new)
  confls=set(part.keys())&set(compt.keys())
  result=part.copy()
  result.update(compt)
  for confl in confls:
    temp=part[confl].copy()
    temp.update(compt[confl])
    result.update({confl:temp})
  return list(result.values())


def parent(id:str)->list:
  if id in chainmap:
    return chains[chainmap.index(id)]
  else:
    proto=dict.get(allp,id,{})
    if not proto:
      #print(f'proto {id} not in \"allp\", searching...')
      #proto=findproto_yml(id,"entity")
      #if proto:
      #  print(f'{id} was found! Check \"allp\"')
      #else:
      print(f'{id} not found, program may not load')
      #  return
    parids=dict.get(proto,"parent")
    comps=dict.get(proto,"components",[])
    if parids:
      if type(parids)!=ruamel.yaml.CommentedSeq:
        parids=[parids]
      resultlist=merge(parent(parids[0]),comps)
    else:
      resultlist=list(comps)
    chainmap.append(id)
    chains.append(resultlist)
    return resultlist


#print("\n".join([str(a) for a in parent("CEPDA")]))

