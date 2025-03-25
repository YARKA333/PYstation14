from typing import TYPE_CHECKING
if TYPE_CHECKING:
  from Modules.entityModule import Entity
from abc import ABC, abstractmethod
comps={}
class BaseComponent(ABC):
  after:list=[]
  before:list=[]
  @abstractmethod
  def __init__(self,entity:"Entity",args:dict):...
  def __repr__(self):
    data=[f"  {k}:{repr(v) if not isinstance(v,BaseComponent) else str(v)}".replace("\n","\n  ") for k,v in self.__dict__.items()]
    if data:
      return "\n".join(data)
    else:
      return "< no data >"
  def __str__(self):
    return super().__repr__()

def component(cls):
  comps[cls.__name__]=cls
  return cls


import os
import importlib.util

def load_components():
  for root, dirs, files in os.walk("Components"):
    for file in files:
      if file.endswith(".py"):
        file_path = os.path.join(root, file)
        spec = importlib.util.spec_from_file_location("module.name", file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

  #print("comps: ",",".join(comps.keys()))

def getcomponent(name):
  comp=comps.get(name)
  if not comp:
    comp=globals().get(name)
  return comp






