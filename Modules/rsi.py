print("rsi.py loading")
if __name__=="__main__":
  raise RuntimeError("why did you do this")

import os.path
import math
import time
import pygame as pg
import json
import pickle
import ruamel
from ruamel import yaml as ryaml
import Utils.shared as shared
from Utils.hasher import check,ismod
from pathlib import Path
import dill
from Utils.serial import Surface
from Utils.vector2 import Vector
import Utils.events as events
from Utils.fileutils import joinpath,openfile,namelist
#from threading import Thread

resources=shared.get("resources")
yaml=ryaml.YAML(typ='rt')
allr={}
pg.init()

print("rsi.py inited")



class RSI:
  class State:
    def __init__(self,path,state,source=None):
      self.image=Surface(pg.image.load(openfile(joinpath(path,state["name"]+".png"),source)).convert_alpha())

      self.image_x,self.image_y=self.image.get_size()
      if "directions" in state:
        self.directions=state["directions"]
      else:
        self.directions=1
      if "delays" in state:
        self.delays=state["delays"]
      else:
        self.delays=None

    def getframe(self,dir=0,frame: int = None,otime: float = 0) -> int:
      if self.delays is None: return dir
      delay=self.delays[dir]
      if frame is None:
        secs=(time.time()-otime)%sum(delay)
        summ=0
        for frame in range(len(delay)):
          summ+=delay[frame]
          if secs<summ:
            break
      return frame+len(delay)*dir

    def getframes(self,dir=0):
      if self.delays is None: return 1
      return len(self.delays[dir])
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
      self.states.update({state["name"]:self.State(path,state,source)})
  @property
  def size(self):
    return Vector(self.frame_x,self.frame_y)
  def __str__(self):
    return f"RSI({self.path})"
  def __call__(self,size:float|int=1,state:str|None=None,dir:int=0,frame:int|None=None,otime:float=0,nowarn:bool=False)->pg.Surface:
    state=self.getstate(state,nowarn)
    dir=dir%state.directions
    surf=pg.Surface([self.frame_x,self.frame_y],flags=pg.SRCALPHA)
    if frame is None:
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
        #traceback.print_stack()
        print(f"Tried to get state \"{state}\" of object \"{self.path}\"")
      return self.states[self.default]
  def getstates(self)->list:return self.states.keys()
  def getframe(self,state:str=None,dir:int=0,frame:int=None,otime:float=0,nowarn:bool=True)->int:
    state=self.getstate(state,nowarn)
    return state.getframe(dir,frame,otime)
  def getdirs(self,state=None,nowarn=True):
    return self.getstate(state,nowarn).directions

def yml(path,raw=False):
  """[Deprecated]
  fast way to open YAML
  deprecated since detag()
  """
  try:
    if raw:
      with open(path,"rb") as file:
        return yaml.load(file)
    else:
      return yaml.load(openfile(path))
  except Exception as error:print(f'{error} \nError when opening {path} in {raw and "raw" or "auto"} mode')

def loadrsi(path):
  """
  gives instance of RSI with given path
  or creates new if there's no such
  """
  result=allr.get(path)
  if not result:
    result=RSI(path)
    allr.update({path:result})
  return result
from tqdm import tqdm

def preload_rsi(ldr):
  """
  preloads ready RSI classes from .dill cache
  if there is no, creates one
  """
  print("preloading .RSI")
  global allr
  kake_path="kake/rsi.dill"
  path=joinpath(resources,"Textures")
  #old_hash=hasher.get_hash("Textures")
  #new_hash=hasher.hash_path(path)
  if os.path.exists(kake_path) and check(path):
    with open(kake_path,"rb") as file:
      allr=dill.load(file)
  else:
    files=namelist("Textures")
    for path in tqdm(ldr.iter(files),desc="Textures updating... "):
      if not path.endswith(".rsi/meta.json"):continue
      loadrsi(path.replace("/meta.json",""))
    with open(kake_path,"wb") as file:
      dill.dump(allr,file)
    #hasher.set_hash("Textures",new_hash)
    print("re",end="")
  print(f"loaded {len(allr)} .RSI")


def str_angle(raw:str):
  return round(float(raw.split(" ")[0])/math.pi*180)

def strtuple(cor:str)->list[int]:
  return [int(a) for a in cor.split(",")]

allprotos:dict[str,dict]={}
allp:dict[str,dict]={}

def load_protos(ldr,ldg):
  global allprotos,allp
  ldg("loading prototypes")
  if ismod(joinpath(resources,"Prototypes")):
    from proto_sorter import load_protos
    data=load_protos(pickle=True,ldr=ldr,source=resources)
  else:
    print("loading protos")
    with open("prototypes.pk","rb") as file:
      data=pickle.load(file)
  from yaml_tag import retag
  ldg("processing prototypes")
  allprotos|=retag(data)
  allp|=allprotos["entity"]
  events.call("proto_ready")
  print("loaded",sum([len(p) for p in allprotos.values()]),"protos")

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

def topdict(input_dict:dict)->list:
  return "{"+",".join([f'{item[0]}:{item[1]}' for item in sorted(input_dict.items(),key=lambda item:item[1],reverse=True)])+"}"

print("rsi.py loaded")