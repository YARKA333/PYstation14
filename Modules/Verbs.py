import Utils.events as events
import Modules.entityModule as eMod
import pygame as pg
from Modules.rsi import joinpath
import Utils.shared as shared

icondir=joinpath(shared.get("resources"),"Textures/Interface")
def icon(name:str)->pg.Surface:
  name=joinpath(icondir,name)
  img=pg.transform.smoothscale_by(pg.image.load(name),0.5)
  size=32
  surf=pg.Surface((size,size),pg.SRCALPHA)
  surf.blit(img,[(size-img.width)/2,(size-img.height)/2])
  return surf

img_examine=icon("VerbIcons/examine.svg.192dpi.png")
img_delete=icon("VerbIcons/delete.svg.192dpi.png")


def Examine(uid):
  print(eMod.getEcomp(uid,"MetaData").desc)
  return
default_verbs=[{
    "name":"Examine",
    "priority":10,
    "img":img_examine,
    "click":Examine,
    },{
    "name":"Delete",
    "priority":10,
    "img":img_delete,
    "click":Examine,
    }]
def getVerbs(uid):
  verbs=default_verbs
  g=sum(events.call("getVerbs",entity=uid,noreturn=False),start=[])
  return verbs+g