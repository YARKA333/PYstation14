from Modules.rsi import *
import pickle

alpha=[chr(i) for i in list(range(65,91))+list(range(97,123))]
beta=["A","Q","g","w"]
def decode(code):
  a=alpha.index(code[0])*4
  if code[1] in beta:
    return a+beta.index(code[1])
  return None

def loadmap(id):
    mapPath:str=findproto_yml(id,"gameMap")["mapPath"]
    print("loading map")
    kakePath=joinpath("kake",mapPath.replace(".yml",".pk"))
    if os.path.exists(kakePath):
      print("cache found!")
      with open(kakePath,"rb") as file:
        map_file=pickle.load(file)
    else:
      print("cache not found\nProcessing map...")
      map_file=yml(mapPath)
      ensuredir(kakePath)
      with open(kakePath,"xb") as file:
        pickle.dump(map_file,file)
    print("loaded map")
    return map_file

def loadfloor(map_file):
  chunks_raw=findict(map_file["entities"],"type","MapGrid",5)["chunks"]
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
  def __init__(self,id):
    self.raw=loadmap(id)
    self.anchoredgrid={}
