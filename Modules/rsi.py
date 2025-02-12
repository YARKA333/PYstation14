print("rsi.py loading")
if __name__=="__main__":
  raise RuntimeError("why did you do this")

import io
import os.path
import traceback
import math
#from tqdm import tqdm
import time
import pygame as pg
import json
import pickle
import ruamel
from ruamel import yaml as ryaml
import Utils.shared as shared
import Utils.hasher as hasher
from pathlib import Path
from zipfile import ZipFile
import dill
from Utils.serial import Surface
from Utils.vector2 import Vector
#from threading import Thread


resources=shared.get("resources")
yaml=ryaml.YAML(typ='rt')
allr={}
pg.init()

print("rsi.py inited")

class _State:
  def __init__(self,path,state,source=None):
    self.image=Surface(pg.image.load(openfile(joinpath(path,state["name"]+".png"),source)).convert_alpha())

    self.image_x,self.image_y=self.image.get_size()
    if "directions" in state:
      self.directions=state["directions"]
    else:self.directions=1
    if "delays" in state:
      self.delays=state["delays"]
    else: self.delays=None
  def getframe(self,dir=0,frame:int=None,otime:float=0)->int:
    if self.delays==None: return dir
    delay=self.delays[dir]
    if frame==None:
      secs=(time.time()-otime)%sum(delay)
      summ=0
      for frame in range(len(delay)):
        summ+=delay[frame]
        if secs<summ:
          break
    return frame+len(delay)*dir
  def getframes(self,dir=0):
    if self.delays==None:return 1
    return len(self.delays[dir])

def sin(a):return math.sin(math.radians(a))
def cos(a):return math.cos(math.radians(a))

class RSI:
  def __init__(self,path:Path,source=None):
    if not "Textures" in path:
      path=joinpath("Textures",path)
    f=openfile(joinpath(path,"meta.json"),source)
    meta=json.load(f)
    f.close()
    self.path=path
    self.frame_x=meta["size"]["x"]
    self.frame_y=meta["size"]["y"]
    self.default=meta["states"][0]["name"]
    self.states={}
    for state in meta["states"]:
      self.states.update({state["name"]:_State(path,state,source)})
  @property
  def size(self):
    return Vector(self.frame_x,self.frame_y)
  def __str__(self):
    return f"RSI({self.path})"
  def __call__(self,size:float|int=1,state:str|None=None,dir:int=0,frame:int|None=None,otime:float=0,nowarn:bool=False)->pg.Surface:
    state=self.getstate(state,nowarn)
    dir=dir%state.directions
    surf=pg.Surface([self.frame_x,self.frame_y],flags=pg.SRCALPHA)
    if frame==None:
      frame=state.getframe(dir,otime=otime)
    row=state.image_x/self.frame_x
    x=frame%row*self.frame_x
    y=frame//row*self.frame_y
    surf.blit(state.image,[-x,-y])
    if size!=1:
      surf=pg.transform.scale_by(surf,size)
    return surf
  def getstateframes(self,state:str=None,dir:int=0)->int:
    if not state in self.states:
      state=self.default
    return self.states[state].getframes(dir)
  def getstate(self,state:str=None,nowarn:bool=False):
    state=str(state)
    if state in self.states:
      return self.states[state]
    else:
      if self.path!="Textures/deprecated.rsi" and not nowarn:
        traceback.print_stack()
        print(f"Tried to get state \"{state}\" of object \"{self.path}\"")
      return self.states[self.default]
  def getstates(self)->list:return self.states.keys()
  def getframe(self,state:str=None,dir:int=0,frame:int=None,otime:float=0,nowarn:bool=True)->int:
    state=self.getstate(state,nowarn)
    return state.getframe(dir,frame,otime)
  def getdirs(self,state=None,nowarn=True):
    return self.getstate(state,nowarn).directions

def yml(path,raw=False):
  try:
    if raw:
      with open(path,"rb") as file:
        return yaml.load(file)
    else:
      return yaml.load(openfile(path))
  except Exception as error:print(f'{error} \nError when opening {path} in {raw and "raw" or "auto"} mode')


def openfile(path,source=None):
  if not source:source=shared.get("resources")
  assert os.path.isdir(source)
  #try:
  jpath=Path(joinpath(source,path))
  return io.BytesIO(jpath.read_bytes())
  #except:pass
  #try:
  #  with ZipFile(joinpath(source,"Content.Client.zip")) as archive:
  #    return io.BytesIO(archive.read(joinpath(path)))
  #except:raise Exception("incorrect path: "+path)

def listdir(path,source=None):
  if not source: source=shared.get("resources")
  assert os.path.isdir(source)
  try:
    return os.listdir(joinpath(source,path))
  except:pass
  try:
    with ZipFile(joinpath(source,"Content.Client.zip")) as archive:
       return[f.split("/")[-1] for f in archive.namelist() if f.startswith(path)]
  except:raise Exception("incorrect path: "+path)

#@numba.njit(cache=1)
def namelist(path:str,source=None,full=False):
  if not path.startswith("C:/"):
    if source=="Project": fpath=path
    else:
      if not source: source=shared.get("resources")
      fpath=joinpath(source,path)
  else:fpath=path
  #try:
  e=[]
  for a,b,c in os.walk(fpath):
    a=a.replace(fpath,"")
    for d in c:
      try:
        e.append(
          joinpath(path,a,d)
          if full else
          joinpath(a,d))
      except IndexError:print(f'a:{a},d:{d}')
  return e
  #except:pass
  #try:
  #  with ZipFile(joinpath(source,"Content.Client.zip")) as archive:
  #    return[f.split("/")[-1] for f in archive.namelist() if f.startswith(path)]
  #except:raise Exception("incorrect path: "+path)

#@numba.njit(cache=1)
def joinpath(*paths:str|os.PathLike):
  result=""
  for path in paths:
    if path=="":continue
    path=path.replace("\\","/")
    if path[0]=="/":
      path=path[1:]
    if path[-1]=="/":
      path=path[0:-1]
    if result:result+="/"
    result+=path
  return result

def loadrsi(name):
  result=allr.get(name)
  if not result:
    result=RSI(name)
    allr.update({name:result})
  return result
from tqdm import tqdm
def preload_rsi():
  print("preloading .RSI")
  global allr
  kake_path="kake/rsi.dill"
  path=joinpath(resources,"Textures")
  old_hash=hasher.get_hash("Textures")
  new_hash=hasher.hash_path(path)
  if os.path.exists(kake_path) and new_hash==old_hash:
    with open(kake_path,"rb") as file:
      allr=dill.load(file)
  else:
    files=namelist("Textures")
    for path in tqdm(files,desc="Textures updating... "):
      if not path.endswith(".rsi/meta.json"):continue
      loadrsi(path.replace("/meta.json",""))
    with open(kake_path,"wb") as file:
      dill.dump(allr,file)
    hasher.set_hash("Textures",new_hash)
    print("re",end="")
  print(f"loaded {len(allr)} .RSI")


def findict(dicts,key,value=None,maxdepth=0):
  if type(dicts)==ruamel.yaml.CommentedMap and key in dicts and (value==None or dicts[key]==value):
      return dicts
  if maxdepth!=0:
    if type(dicts)==ruamel.yaml.CommentedMap:
      for a,b in dicts.items():
        #print((" "*-maxdepth)+str(a)+":")
        r=findict(b,key,value,maxdepth-1)
        if r!=False:return r
    elif type(dicts)==ruamel.yaml.CommentedSeq:
      for a in dicts:
        r=findict(a,key,value,maxdepth-1)
        if r!=False:return r
    #else: print((" "*-maxdepth)+str(dicts))
  return False

def str_angle(raw:str):
  return round(float(raw.split(" ")[0])/math.pi*180)

def strtuple(cor:str)->list[int]:
  return [int(a) for a in cor.split(",")]

def findproto(id,list:list):
  for proto in list:
    try:
      if proto["id"]==id:
        return proto
    except:
      print(f"dolbany shashlik:\n{proto}")

allprotos={}
allp={}

def load_protos():
  global allprotos,allp,tiles
  print("loading protos")
  from yaml_tag import retag
  with open("prototypes.pk","rb") as file:
    allprotos|=retag(pickle.load(file))
  allp|=allprotos["entity"]
  print("loaded",sum([len(p) for p in allprotos.values()]),"protos")
  comptypes=[]
  for en in allp.values():
    comps=en.get("components")
    if not comps:continue
    for c in comps:
      t=c["type"]
      if not t in comptypes:
        comptypes.append(t)
  print("with total of",len(comptypes),"component types")
  #print(classes[0])
  #print(comptypes)
  #for i in range(100):
  #  gen=generate()
  #  #if "-" in gen:
  #  print(gen)

def vec(a):
  return [max(-1,min(1,abs(4-(a+i)%8)-2)) for i in [-2,0]]
def svec(a,l=1):
  return [l*sin(a),l*cos(a)]

def ensuredir(path):
  dirs=path.split("/")[:-1]
  cpath=""
  for i in range(len(dirs)):
    cpath="/".join(dirs[:i+1])
    if os.path.isdir(cpath): continue
    os.mkdir(cpath)

def rotate_vector(vector:list[float,float],angle:float):
  if vector==[0,0]:return vector
  angle_rad=math.radians(angle)
  return [
    vector[0]*math.cos(angle_rad)-vector[1]*math.sin(angle_rad),
    vector[0]*math.sin(angle_rad)+vector[1]*math.cos(angle_rad)]

def resolve(string:str):
  try:
    return int(string)
  except:...
  try:
    return float(string)
  except:...
  try:
    bunch=string.split(",")
    assert isinstance(bunch,list) and len(bunch)>1
    r=[]
    print(bunch)
    for elem in bunch:
      r.append(resolve(elem))
    return r
  except:...
  return string

print("rsi.py loaded")