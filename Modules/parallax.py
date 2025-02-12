import os.path
import random
from Modules.rsi import *
import tomllib
import noise
from tqdm import tqdm
from yaml_tag import tag
from Utils.colors import hextorgb

def calcfill(src,dst):
  #if not dst:dst=[WIDTH,HEIGHT]
  return [1+math.ceil(dst[i]/src[i]) for i in range(len(src))]+list(src)

def calcbake(image:pg.Surface):
  fill=calcfill(image.get_size(),[1920,1080])
  surf=pg.Surface([fill[0]*fill[2],fill[1]*fill[3]],flags=image.get_flags())
  for fx in range(0,fill[0]):
    for fy in range(0,fill[1]):
      surf.blit(image,[fx*fill[2],fy*fill[3]])
  return surf

def declist(list):
  return [float(a) for a in list.split(",")]

def rdnext():random.seed+=1

default_layer={
  "seed":1234,
  "pointcount":100,
  "closecolor":"#ffffff",
  "farcolor":"#000000",
  "pointsize":1,
  "mask":False,
  "masksed":1234,
  "maskpersistence":0.5,
  "masklacunarity":math.pi*2/3,
  "maskfrequency":1,
  "maskoctaves":3,
  "maskthreshold":None,
  "maskpower":1,
  "masknoise_type":"fbm",
}

default_proto={
  "scale":"1, 1",
  "scrolling":"0, 0",
  "tiled":True,
}

class Layer:
  def __init__(self,proto):
    self.image=proto["texture"]
    if self.image:
      self.offset=[0,0]
      self.scroll=declist(proto["scrolling"])
      self.scale=[a/1 for a in declist(proto["scale"])]
      self.speed=(1-proto["slowness"])

      self.image=pg.transform.scale_by(self.image,self.scale[0]*2)
      if "tiled" in proto.keys() and not proto["tiled"]:
        self.baked=None
      else:
        self.baked=calcbake(self.image)
      self.size=self.image.get_size()
  def draw(self,surf:pg.Surface,x,y):
    if not self.image:return
    self.offset[0]-=self.scroll[0]*.5
    self.offset[1]-=self.scroll[1]*.5
    if self.baked:
      surf.blit(self.baked,[
        (-x*self.speed+self.offset[0])%self.size[0]-self.size[0],
        (y*self.speed+self.offset[1])%self.size[1]-self.size[1]])
    else:

      surf.blit(self.image,[-x*self.speed,y*self.speed])
@tag("ImageParallaxTextureSource")
def image_texture(path):return pg.image.load(openfile(path))
@tag("GeneratedParallaxTextureSource")
def generated_texture(configPath,id):
  path=f"kake/parallax/{id}.png"
  if os.path.exists(path):
    image=pg.image.load(path)
  else:
    def alpha(color):return color+[min(sum(color),255)]
    image=pg.Surface([960,540],flags=pg.SRCALPHA)
    toml=tomllib.load(openfile(configPath))
    for tomlayer in reversed(toml["layers"]):
      print(tomlayer)
      if tomlayer["type"]=="points":
        layer=default_layer.copy()
        layer.update(tomlayer)
        farcolor=hextorgb(layer["farcolor"])
        closecolor=hextorgb(layer["closecolor"])
        random.seed(layer["seed"])
        o=layer["pointsize"]-1
        if layer["mask"]:
          seed=layer["maskseed"]
          freq=float(layer["maskfrequency"])
          pers=float(layer["maskpersistence"])
          lacu=float(layer["masklacunarity"])
          octs=layer["maskoctaves"]
          threshVal=1/(1-float(layer["maskthreshold"]))
          powFactor=1/float(layer["maskpower"])
        i=0
        while i<layer["count"]//4:
          x=random.randint(0,image.get_width())
          y=random.randint(0,image.get_height())
          if layer["mask"]:
            noiseVal=noise.snoise2(x*freq+seed*12345,y*freq-seed*54321,octaves=octs,persistence=pers,lacunarity=lacu)
            noiseVal=min(1,max(0,noiseVal+1)/2)
            noiseVal=max(0,noiseVal-float(layer["maskthreshold"]))
            noiseVal*=threshVal
            noiseVal=noiseVal**powFactor
            randomThresh=random.random()
            if randomThresh>noiseVal:
              continue
          dist=random.random()
          image.fill(alpha([farcolor[j]*dist+closecolor[j]*(1-dist) for j in range(3)]),
            [x-o,y-o,o*2+1,o*2+1])
          i+=1
    ensuredir(path)
    pg.image.save(image,path)
  return image

class Parallax:
  def __init__(self,id):
    self.layers=[]
    ymlayers=allprotos["parallax"][id]["layers"]
    for ymlayer in tqdm(ymlayers,desc="generating parallax... "):
      proto=default_proto.copy()
      print(ymlayer)
      proto.update(ymlayer)
      self.layers.append(Layer(proto))
  def draw(self,surf,x,y):
    for layer in self.layers:
      layer.draw(surf,x,y)


