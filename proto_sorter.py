import pickle

from rsi import *
from tqdm import tqdm
import os.path
names,cerrors,allProtos=[],[],[]
#@numba.njit(cache=1)
def load_protos(reload=False,source=None):
  if reload and os.path.isdir("opti_proto"):
    shutil.rmtree("opti_proto")
  if not os.path.isdir("opti_proto"):
    global names,allProtos
    namess=namelist("Prototypes/")
    names=[name for name in namess if name.endswith(".yml")]
    if False:
      threads=[Thread(target=load_tread) for i in range(200)]
      for t in tqdm(threads,desc="Starting threads"):
        t.start()
      for i in tqdm(range(len(names),0,-1),desc="Reading protos"):
        while i<len(names):
          pass
      for t in threads:
        t.join()
    else:
      for name in tqdm(names,desc="Reading protos"):
        try:
          allProtos+=yaml.load(openfile(joinpath("Prototypes/",name)))
        except Exception as error:
          #print(f"{error} in file {name}")
          cerrors.append(f"{error} in file {name}")
    with open("errors.log","w") as file:
      file.write("\n".join(cerrors))
    sorted={}
    allp={}
    for proto in tqdm(allProtos,desc="sorting protos"):
      prototype=proto["type"]
      id=proto["id"]
      try:idletter=id[0].upper()
      except:idletter="-"
      if not prototype in sorted.keys():
        sorted.update({prototype:{}})
        allp.update({prototype:{}})
      letters=sorted[prototype]
      type=allp[prototype]
      if id in type.keys():
        print(f'proto {id} is conflicting')
      else:
        type.update({id:proto})
      if not idletter in letters.keys():
        letters.update({idletter:[]})
      letters[idletter].append(proto)
    with open("kake/prototypes.pk","wb") as file:
      pickle.dump(allp,file)
    os.mkdir("opti_proto")
    for cat,lets in sorted.items():
      os.mkdir(joinpath("opti_proto",cat))
      for let,list in lets.items():
        for i in range(3):
          try:
              file=io.open(joinpath("opti_proto",cat,let+".yml"),"w",encoding="UTF-8")
              yaml.dump(list,file)
              file.close()
              break
          except Exception as error:
            file.close()
            if i<2:continue
            else:print(f"{error} in compiling {joinpath("opti_proto",cat,let+".yml")}")


@numba.njit(cache=1)
def load_tread():
  global names,allProtos,cerrors
  while names:
    name=names.pop(0)
    try:
      allProtos.append(yaml.load(openfile(name)))
    except Exception as error:
      cerrors.append(f"{error} in file {name}")

load_protos(True)