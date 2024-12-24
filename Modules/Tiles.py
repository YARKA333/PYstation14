import pygame as pg
from Modules.rsi import openfile,allprotos,resolve
import random

mig:dict=allprotos["tileAlias"]
tiles:dict=allprotos["tile"]

class Floor:

  def __init__(self,id:str="Space"):

    self.baseTurf="Plating"
    self.isSubfloor=False
    self.isSpace=False
    self.deconstructTools=["Prying"]
    self.friction=0.2
    self.thermalConductivity=0.04
    self.heatCapacity=0.0003
    self.mobFriction:float
    self.mobFrictionNoInput:float
    self.mobAcceleration:float
    self.itemDrop="FloorTileItemSteel"
    self.sturdy=True
    self.weather=False
    self.indestrictible=False

    try:
      id=mig[id]["target"]
    except:pass
    try:
      tile=tiles[id]
    except:
      print("No tile with id:"+id+"\nReplaced with Space")
      #tile=next((item for item in tiles if item["id"]=="Space"),None)
      tile=tiles["Space"]
    for k,v in tile.items():
      setattr(self,k,resolve(v))
    if hasattr(self,"sprite"):
      self.image=pg.image.load(openfile(self.sprite))
      surf=pg.Surface([32]*2,pg.SRCALPHA)
      self.images=[]
      if not hasattr(self,"variants"):
        self.variants=1
        self.placementVariants=[1]
      for i in range(self.variants):
        surf.blit(self.image,[-32*i,0])
        self.images.append(surf.copy())
    else:self.sprite=False

  def __call__(self,variant=None):
    if self.sprite:
      if variant is None:
        return random.choices(self.images,weights=self.placementVariants)[0]
      else:
        assert variant<self.variants
        return self.images[variant]
    else: return False