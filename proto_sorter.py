import pickle as picklelib
from Modules.rsi import namelist,joinpath
from tqdm import tqdm
import json as jsonlib
names,cerrors,allProtos=[],[],[]
import yaml
from yaml_tag import TagPlaceholder

yaml.CLoader.yaml_implicit_resolvers.pop("O")
yaml.CLoader.yaml_implicit_resolvers.pop("o")


#yaml.add_constructor(None,TagPlaceholder)
yaml.CLoader.add_constructor(None,TagPlaceholder)
#@numba.njit(cache=1)
def load_protos(reload=False,source=None,pickle=False,json=False):
  global names,allProtos
  namess=namelist("Prototypes/",source)
  names=[name for name in namess if name.endswith(".yml")]
  for name in tqdm(names,desc="Reading protos"):
    with open(joinpath(source,"Prototypes/",name),"rt",encoding="UTF-8") as file:
      text=file.read()
    if not text: continue
    try:
      data=yaml.load(text,yaml.CLoader)
      if data:
        allProtos+=data
    except Exception as error:

      print(f"{error} in file {name}")
      print(text)
      cerrors.append(f"{error} in file {name}")

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
  #allp=detag(allp)
  input("press enter to continue")
  print(allp["entity"])
  input("press enter to dump")
  if json:
    try:
      with open("protrotypes.json","wt") as file:
        jsonlib.dump(allp,file)
      print("json dump successfull")
    except Exception as error:print(error)
  if pickle:
    try:
      with open("prototypes.pk","wb") as file:
        picklelib.dump(allp,file)
      print("pickle dump successfull")
    except Exception as error:print(error)


if __name__=="__main__":
  load_protos(True,json=False,pickle=True,source="C:/Servers/SS14 c2/Resources")