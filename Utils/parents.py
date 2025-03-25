from Modules.rsi import *

chains=[]
chainmap=[]

def typedict(todict:list[dict],key:str="type")->dict:
  """takes a list of dicts and converts it do dict with keys corresponding dict's <key> value"""
  return {a[key]:a for a in todict}

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


def parent(protoid:str)->list:
  if protoid in chainmap:
    return chains[chainmap.index(protoid)]
  else:
    if isinstance(protoid,list):
      protoid=protoid[0]
    proto=allp.get(protoid,{})
    if not proto:
      print(f'{protoid} not found, program may not load')
    parids=proto.get("parent")
    comps=proto.get("components",[])
    if parids:
      if isinstance(parids,str):
        parids=[parids]
      for parid in parids:
        comps=merge(parent(parid),comps)
    chainmap.append(protoid)
    chains.append(list(comps))
    return list(comps)

if __name__=="__main__":
  print("\n".join([str(a) for a in parent("GasVentScrubber")]))

