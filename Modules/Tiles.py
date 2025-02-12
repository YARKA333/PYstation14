import os

import pygame as pg
from Modules.rsi import openfile,allprotos,resolve,joinpath
import random
notile_path=joinpath(os.getcwd(),"assets/noTile.png")
notile={
  "type":"tile",
  "id":"notile",
  "name":"error",
  "sprite":notile_path,
  "isSubFloor":True,
}
notile_sprite=pg.image.load(notile_path)

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

    mig: dict=allprotos["tileAlias"]
    tiles: dict=allprotos["tile"]

    if id in mig:
      id=mig[id]["target"]
    if id in tiles:
      tile=tiles[id]
    else:
      print("No tile with id:"+id+"\nReplaced with Space")
      #tile=next((item for item in tiles if item["id"]=="Space"),None)
      tile=notile
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
      elif variant<self.variants:
        return self.images[variant]
      else:
        return notile_sprite
    else: return False