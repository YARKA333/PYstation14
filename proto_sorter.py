import pickle as picklelib

import ruamel.yaml.comments
from ruamel.yaml.loader import RoundTripLoader
from yaml.loader import FullLoader

from Modules.rsi import *
from tqdm import tqdm
import os.path
import shutil
import json as jsonlib
names,cerrors,allProtos=[],[],[]
import yaml
def detag(data):
  if isinstance(data,dict):
    return {k:detag(v) for k,v in data.items()}
  elif isinstance(data,list):
    return [detag(v) for v in data]
  elif isinstance(data,ruamel.yaml.comments.TaggedScalar):
    l=data._yaml_tag.suffix.split(":")
    d={l[0]:l[1]}
    print(d)
    return d
  else:
    return data

yaml=ruamel.yaml.YAML(typ="rt")
#@numba.njit(cache=1)
def load_protos(reload=False,source=None,pickle=False,json=False):
  global names,allProtos
  namess=namelist("Prototypes/",source)
  names=[name for name in namess if name.endswith(".yml")]
  for name in tqdm(names,desc="Reading protos"):
    try:
      allProtos+=yaml.load(openfile(joinpath("Prototypes/",name),source))
    except Exception as error:
     print(f"{error} in file {name}")
    #  cerrors.append(f"{error} in file {name}")

  with open("errors.log","w") as file:
    file.write("\n".join(cerrors))
  allp={}
  for proto in tqdm(allProtos,desc="sorting protos"):
    prototype=proto["type"]
    id=proto["id"]
    if not prototype in allp:
      allp[prototype]={}
    type=allp[prototype]
    if id in type:
      print(f'proto {id} is conflicting')
    else:
      type[id]=proto
  allp=detag(allp)
  input("press enter to continue")
  print(allp["entity"])
  input("press enter to dump")
  if json:
    try:
      with open("protrotypes.json","wt") as file:
        jsonlib.dump(allp,file)
    except Exception as error:print(error)
  if pickle:
    try:
      with open("kake/prototypes.pk","wb") as file:
        picklelib.dump(allp,file)
    except Exception as error:print(error)


if __name__=="__main__":
  load_protos(True,json=True,pickle=True,source="C:/Servers/SS14 c2/Resources")
  #with open("kake/prototypes.pk","rb") as file:
  #  allp=pickle.load(file)
  #allp={1:2}
  #with open("protrotypes.json","wt") as file:
  #  jsonlib.dump(allp,file)