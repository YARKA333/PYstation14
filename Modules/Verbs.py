import Utils.events as events
import Modules.entityModule as eMod
import pygame as pg
def icon(name:str)->pg.Surface:
  return pg.transform.smoothscale_by(pg.image.load(name),0.5)
img_examine=icon("C:/Servers/SS14 c2/Resources/Textures/Interface/VerbIcons/examine.svg.192dpi.png")
img_delete=icon("C:/Servers/SS14 c2/Resources/Textures/Interface/VerbIcons/delete.svg.192dpi.png")

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