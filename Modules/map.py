import os
import pickle
import Utils.shared as shared
from Utils.fileutils import ensuredir,joinpath
from Utils.parents import typedict
from Utils.vector2 import Vector
from Modules.rsi import allprotos
from Modules.Tiles import Floor
from Utils.hasher import check
from tqdm import tqdm
from yaml_tag import quick_load



resources=shared.get("resources")
alpha=[chr(i) for i in list(range(65,91))+list(range(97,123))]
beta=["A","Q","g","w"]


def findmap(raw:dict,name=None):
  for ent in raw["entities"]:
    if ent["proto"]=="":break
  else:raise Exception("map LOading Error")
  ents=ent["entities"]
  for e in ents:
    e["components"]=typedict(e["components"])
  ents=typedict(ents,"uid")

  for grid in ents.values():
    comps=grid["components"]
    if "MapGrid" in comps and (name is None or name==comps["MapGrid"]["id"]):
      break
  else:raise Exception("Station Not Found")
  return ents[int(comps["Transform"]["parent"])],grid


def decode(code:str)->int|None:
  """scary letters to numbers"""
  a=alpha.index(code[0])*4
  if code[1] in beta:
    return a+beta.index(code[1]),alpha.index(code[5])
  else:raise Exception("map is invalid")

def loadmap(mapid):
    mapPath:str=allprotos["gameMap"][mapid]["mapPath"]
    print("loading layerMap")
    kakePath=joinpath("kake",mapPath.replace(".yml",".pk"))
    fullPath=joinpath(resources,mapPath)
    if os.path.exists(kakePath) and check(fullPath):
      print("cache found!")
      with open(kakePath,"rb") as kakefile:
        map_file=pickle.load(kakefile)
    else:
      print("cache not found\nProcessing layerMap...")
      map_file=quick_load(fullPath)
      ensuredir(kakePath)
      with open(kakePath,"wb") as kakefile:
        pickle.dump(map_file,kakefile)
    print("loaded layerMap")
    return map_file

def loadfloor(comps):
  chunks_raw=comps["MapGrid"]["chunks"]
  grid=[]
  cmap=[]
  for chunk_raw in chunks_raw.values():
    chunk_data=chunk_raw["tiles"]
    offset=chunk_raw["ind"]
    chunk=[]
    for y in range(16):
      chunkline=[]
      for x in range(16):
        i=y*16+x
        a=chunk_data[i*8:i*8+8]
        chunkline.append(a)
      chunk.append(chunkline)
    cmap.append(Vector(offset))
    grid.append(chunk)
  return [cmap,grid]

class Grid:
  def __init__(self,mapid):
    self.raw=loadmap(mapid)
    self.map,self.grid=findmap(self.raw)
    self.uid=self.grid["uid"]
    self.gridcomps=self.grid["components"]
    self.mapcomps = self.map["components"]
    self.anchoredgrid={}
    self.chunkMap,self.chunkGrid=loadfloor(self.gridcomps)
    self.tiledict=dict([(a,Floor(b)) for a,b in tqdm(self.raw["tilemap"].items(),desc="Ordering tiles")])
  def getChunk(self,pos:list[int])->list|None:
    if pos in self.chunkMap:
      return self.chunkGrid[self.chunkMap.index(pos)]
    else:return
  def getTile(self,pos:list[int]):
    cpos=[int(pos[0]//16),int(pos[1]//16)]
    chunk=self.getChunk(cpos)
    if not chunk:
      num=0
    else:
      num,var=decode(chunk[int(pos[1])%16][int(pos[0])%16])
    return self.tiledict[num]
