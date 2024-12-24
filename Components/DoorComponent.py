#from enum import Enum
import Components.SpriteComponent
import Utils.events as events
import time
import Modules.Verbs as verbs
import pygame as pg
from Modules.soundModule import *
#DoorStates=Enum("DoorStates",["Open","closing","Closed","Opening","Welded","Denying","Emagging"])
active_doors=[]

component={
  "state":"Closed",
  "openingAnimationTime":1.0,
  "closingAnimationTime":1.0,
  "openingTimeOne":0.4,
  "openingTimeTwo":0.2,
  "closingTimeOne":0.4,
  "closingTimeTwo":0.2,
  "emagDuration":0.8,
  "denyDuration":0.45,
  "occludes":True,
  "openDrawDepth":"Doors",
  "closedDrawDepth":"Doors",
  "openSound":{"path":"/Audio/Effects/explosion1.ogg"},
  "closeSound":{"path":"/Audio/Effects/explosion1.ogg"},
  "denySound":{"path":"/Audio/Effects/explosion1.ogg"},
  "sparksSound":{"collection":"sparks"},
}

icondeny=verbs.icon("info.svg.192dpi.png")
iconemag=verbs.icon("VerbIcons/zap.svg.192dpi.png")
icotoggle=verbs.icon("pray.svg.png")


def frame(args):
  for door in active_doors:
    door.update()
events.subscribe("frame",frame)




class Door:
  def __init__(self,entity,args):
    self.comp=component.copy()
    self.comp.update(args)
    self.uid=entity.uid
    self.partial=False
    self.sprite:Components.SpriteComponent.Sprite=None
    events.followcomp("Sprite",self.Sprite,entity)
    events.subscribe("use",self.activate,self.uid)
    events.subscribe("RMB",self.emag,self.uid)
    events.subscribe("MMB",self.deny,self.uid)
    events.subscribe("getVerbs",self.getVerbs,self.uid)
    self.nextTime=None
    self.appear()
  def getVerbs(self,args):
    print("ae")
    return [{
      "name":"Toggle",
      "priority":10,
      "img":icotoggle,
      "click":self.activate,
      },{
      "name":"Trigger deny",
      "priority":10,
      "img":icondeny,
      "click":self.deny,
      },{
      "name":"Trigger emag",
      "priority":10,
      "img":iconemag,
      "click":self.emag,
      }]
  def setstate(self,state):
    self.comp["state"]=state
    self.appear()
  def activate(self,args):
    active_doors.append(self)
    if self.comp["state"]=="Closed":
      self.setstate("Opening")
      self.nextTime=time.time()+self.comp["openingTimeOne"]
      playSound(self.comp["openSound"],0.5)
    elif self.comp["state"]=="Open":
      self.setstate("Closing")
      self.nextTime=time.time()+self.comp["closingTimeOne"]
      playSound(self.comp["closeSound"],0.5)

  def emag(self,args):
    self.setstate("Emagging")
    self.nextTime=time.time()+self.comp["emagDuration"]
    playSound(self.comp["sparksSound"],0.5)
    active_doors.append(self)
  def deny(self,args):
    self.setstate("Denying")
    self.nextTime=time.time()+self.comp["denyDuration"]
    playSound(self.comp["denySound"],0.5)
    active_doors.append(self)
  def setlayer(self,args):
    events.call("setspritelayer",args,self.uid)
  def appear(self):
    comp=self.comp["state"]
    if   comp=="Open":
      self.setlayer({"index":0,"state":"open"})
      self.setlayer({"index":1,"state":"open_unlit"})
      events.call("setDepth",{"depth":self.comp["openDrawDepth"]},self.uid)
    elif comp=="Closing":
      self.setlayer({"index":0,"state":"closing"})
      self.setlayer({"index":1,"state":"closing_unlit"})
    elif comp=="Closed":
      self.setlayer({"index":0,"state":"closed"})
      self.setlayer({"index":1,"state":"closed_unlit"})
      events.call("setDepth",{"depth":self.comp["closedDrawDepth"]},self.uid)
    elif comp=="Opening":
      self.setlayer({"index":0,"state":"opening"})
      self.setlayer({"index":1,"state":"opening_unlit"})
    elif comp=="Emagging":
      self.setlayer({"index":0,"state":"closed"})
      self.setlayer({"index":1,"state":"sparks"})
    elif comp=="Denying":
      self.setlayer({"index":0,"state":"closed"})
      self.setlayer({"index":1,"state":"deny_unlit"})
  def update(self):
    if self.nextTime==None:return
    if time.time()>=self.nextTime:
      if self.comp["state"]=="Opening":
        if self.partial:
          self.partial=False
          self.setstate("Open")
          active_doors.remove(self)
        else:
          self.partial=True
          events.call("setDepth",{"depth":self.comp["openDrawDepth"]},self.uid)
          self.nextTime=time.time()+self.comp["openingTimeTwo"]
          events.call("setOccluder",{"enabled":False},self.uid)
          events.call("Set_collidable",{"state":False},self.uid)
      elif self.comp["state"]=="Closing":
        if self.partial:
          self.partial=False
          self.setstate("Closed")
          active_doors.remove(self)
        else:
          self.partial=True
          events.call("setDepth",{"depth":self.comp["closedDrawDepth"]},self.uid)
          self.nextTime=time.time()+self.comp["closingTimeTwo"]
          events.call("setOccluder",{"enabled":self.comp["occludes"]},self.uid)
          events.call("Set_collidable",{"state":True},self.uid)
      elif self.comp["state"]=="Emagging":
        self.setstate("Closed")
        self.activate(None)
      elif self.comp["state"]=="Denying":
        self.setstate("Closed")
  def Sprite(self,args):
    self.sprite=args
    events.call("updateMap",{
      "enum.DoorVisualLayers.Base":True,
      "enum.DoorVisualLayers.BaseUnlit":True,
      "enum.WeldableLayers.BaseWelded":False,
      "enum.DoorVisualLayers.BaseBolted":False,
      "enum.DoorVisualLayers.BaseEmergencyAccess":False,
      "enum.WiresVisualLayers.MaintenancePanel":False
    },self.uid)
