from Modules.rsi import *
from Modules.Tiles import Floor
from tqdm import tqdm
from Utils.parents import typedict
import pickle

alpha=[chr(i) for i in list(range(65,91))+list(range(97,123))]
beta=["A","Q","g","w"]

def findmapuid(raw:dict,name=None):
  space=raw["entities"]
  for ent in space:
    if ent["proto"]!="":continue
    for subent in ent["entities"]:
      for comp in subent["components"]:
        if comp["type"]=="BecomesStation" and (name==None or name==comp["id"]):
          return (int(subent["uid"]),typedict(subent["components"]))
  print("station not found")

def decode(code:str)->int|None:
  """scary letters to numbers"""
  a=alpha.index(code[0])*4
  if code[1] in beta:
    return a+beta.index(code[1]),alpha.index(code[5])
  return None,None

def loadmap(mapid):
    mapPath:str=allprotos["gameMap"][mapid]["mapPath"]
    print("loading layerMap")
    kakePath=joinpath("kake",mapPath.replace(".yml",".pk"))
    if os.path.exists(kakePath):
      print("cache found!")
      with open(kakePath,"rb") as kakefile:
        map_file=pickle.load(kakefile)
    else:
      print("cache not found\nProcessing layerMap...")
      map_file=yml(mapPath)
      ensuredir(kakePath)
      with open(kakePath,"xb") as kakefile:
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
    cmap.append([int(a) for a in offset.split(",")])
    grid.append(chunk)
  return [cmap,grid]

class Grid:
  def __init__(self,mapid):
    self.raw=loadmap(mapid)
    self.uid,self.comps=findmapuid(self.raw)
    self.anchoredgrid={}
    self.chunkMap,self.chunkGrid=loadfloor(self.comps)
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
