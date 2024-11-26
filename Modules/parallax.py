import random
import pygame as pg
import random
import math
from Modules.rsi import *
import tomllib
import noise
from tqdm import tqdm

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

class BaseParallaxLayer:
  def baseinit(self,proto):
    self.offset=[0,0]
    self.scroll=declist(proto["scrolling"])
    self.scale=declist(proto["scale"])
    self.speed=(1-proto["slowness"])
    self.offset=[0,0]
    self.scroll=declist(proto["scrolling"])
    self.scale=declist(proto["scale"])
class Stars:
  def __init__(self,proto):
    self.offset=[0,0]
    self.scroll=declist(proto["scrolling"])
    self.scale=declist(proto["scale"])
    toml=tomllib.load(openfile(proto["texture"]["configPath"]))
    self.image=pg.Surface([1920, 1080],flags=pg.SRCALPHA)
    self.speed=(1-proto["slowness"])
    for tomlayer in reversed(toml["layers"]):
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
        while i<layer["count"]:
          x=random.randint(0,self.image.get_width())
          y=random.randint(0,self.image.get_height())
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
          self.image.fill(
            [farcolor[i]*dist+closecolor[i]*(1-dist) for i in range(3)],
            [x-o,y-o,o*2+1,o*2+1])
          i+=1
    self.image=pg.transform.scale_by(self.image,self.scale)
    self.baked=calcbake(self.image)
    self.size=self.image.get_size()
  def draw(self,surf:pg.Surface,x,y):
    self.offset[0]-=self.scroll[0]
    self.offset[1]-=self.scroll[1]
    surf.blit(self.baked,
      [(-x*self.speed+self.offset[0])%self.size[0]-self.size[0],
      (y*self.speed+self.offset[1])%self.size[1]-self.size[1]],special_flags=pg.BLEND_ADD)

class Background:
  def __init__(self,proto):
    self.offset=[0,0]
    self.scroll=declist(proto["scrolling"])
    self.scale=declist(proto["scale"])
    self.speed=(1-proto["slowness"])
    self.image=pg.image.load(openfile(proto["texture"]["path"]))

    self.image=pg.transform.scale_by(self.image,self.scale[0])
    if "tiled" in proto.keys() and not proto["tiled"]:
      self.baked=None
    else:
      self.baked=calcbake(self.image)
    self.size=self.image.get_size()

  def draw(self,surf,x,y):
    self.offset[0]-=self.scroll[0]*.5
    self.offset[1]-=self.scroll[1]*.5
    if self.baked:
      surf.blit(self.baked,[
        (-x*self.speed+self.offset[0])%self.size[0]-self.size[0],
        (y*self.speed+self.offset[1])%self.size[1]-self.size[1]])
    else:
      surf.blit(self.image,[-x*self.speed,y*self.speed])

class Parallax:
  def __init__(self,id):
    self.layers=[]
    ymlayers=allprotos["parallax"][id]["layers"]
    for ymlayer in tqdm(ymlayers,desc="generating parallax... "):
      proto=default_proto.copy()
      proto.update(ymlayer)
      if "path" in proto["texture"].keys():
        self.layers.append(Background(proto))
      if "configPath" in proto["texture"].keys():
        self.layers.append(Stars(proto))
  def draw(self,surf,x,y):
    for layer in self.layers:
      layer.draw(surf,x,y)


