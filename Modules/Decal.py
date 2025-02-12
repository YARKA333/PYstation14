from Modules.rsi import allprotos,loadrsi,str_angle
import pygame as pg
from Utils.vector2 import Vector

class Decal:
  def __init__(self,data):
    node=data["node"]
    id=node["id"]
    spritedata=allprotos["decal"][id]["sprite"]
    sprite=spritedata["sprite"]
    rsi=loadrsi(sprite)
    try:ang=str_angle(node["angle"])
    except:ang=0
    color=[int(node["color"][i*2+1:i*2+3],16) for i in range(4)]
    self.sprite=pg.transform.rotate(rsi(state=spritedata["state"]),ang)
    self.sprite.fill(color[:3],special_flags=pg.BLEND_RGB_MULT)
    self.sprite.convert_alpha()
    self.sprite.set_alpha(color[3])
    self.instances=dict([(c,Vector(a)) for c,a in data["decals"].items()])

  def prebake(self,chunks,cmap):
    for ins in self.instances.values():
      cpos=ins//16
      dpos=Vector(ins[0]%16*32,(15-ins[1]%16)*32)
      chunks[cmap.index(cpos)].blit(self.sprite,dpos.pos)