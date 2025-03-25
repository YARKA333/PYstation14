from Components.Sprite import Sprite
from Modules.component import BaseComponent,component
import Modules.Verbs as verbs
from Modules.soundModule import *
from Modules.UInput import PopupEntity
from Modules.Locale import Loc
import Utils.events as events
import time
active_doors=[]



icondeny=verbs.icon("info.svg.192dpi.png")
iconemag=verbs.icon("VerbIcons/zap.svg.192dpi.png")
icotoggle=verbs.icon("pray.svg.png")


def frame(args):
  for door in active_doors:
    door.update()
events.subscribe("frame",frame)




@component
class Door(BaseComponent):
  after = ["Sprite"]
  base_component={
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
    #"emergencyOnSound":{"path":"/Audio/Machines/airlock_emergencyon.ogg"},
    #"emergencyOffSound":{"path":"/Audio/Machines/airlock_emergencyoff.ogg"},
  }


  def __init__(self,entity,args):
    self.entity=entity
    self.comp=self.base_component.copy()
    self.comp.update(args)
    self.uid=entity.uid
    self.partial=False
    self.sprite:Sprite=None
    events.followcomp("Sprite",self.Sprite,entity)
    events.subscribe("use",self.activate,self.uid)
    events.subscribe("getVerbs",self.getVerbs,self.uid)
    self.nextTime=None
    self.appear()
  def getVerbs(self,args):
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
      args={"cancelled":False}
      events.call("BeforeDoorOpened",args,self.uid)
      if args["cancelled"]:return
      PopupEntity("Боевой режим включён!",self.entity)
      self.setstate("Opening")
      self.nextTime=time.time()+self.comp["openingTimeOne"]
      playSound(self.comp["openSound"],0.5)
    elif self.comp["state"]=="Open":
      args={"cancelled":False}
      events.call("BeforeDoorClosed",args,self.uid)
      if args["cancelled"]:return

      PopupEntity("Боевой режим отключён!",self.entity)
      self.setstate("Closing")
      self.nextTime=time.time()+self.comp["closingTimeOne"]
      playSound(self.comp["closeSound"],0.5)

  def emag(self,args):
    self.setstate("Emagging")
    self.nextTime=time.time()+self.comp["emagDuration"]
    playSound(self.comp["sparksSound"],0.5)
    active_doors.append(self)

  def deny(self,args):
    args={"cancelled":False}
    events.call("BeforeDoorDenied",args,self.uid)
    if args["cancelled"]: return

    self.setstate("Denying")
    self.nextTime=time.time()+self.comp["denyDuration"]
    playSound(self.comp["denySound"],0.5)
    active_doors.append(self)
  def trysetstate(self,map,state):
    layer=self.sprite.layerMap.get(map)
    if layer:
      layer.state=state
    else:
      print(f"failed to get layer {map}")
  def set_states(self,baseState,unlitState):
    self.trysetstate("enum.DoorVisualLayers.Base",baseState)
    self.trysetstate("enum.DoorVisualLayers.BaseUnlit",unlitState)
  def appear(self):
    comp=self.comp["state"]
    match comp:
      case "Open":
        self.set_states("open","open_unlit")
        events.call("setDepth",{"depth":self.comp["openDrawDepth"]},self.uid)
      case "Closing":
        self.set_states("closing","closing_unlit")
      case "Closed":
        self.set_states("closed","closed_unlit")
        events.call("setDepth",{"depth":self.comp["closedDrawDepth"]},self.uid)
      case "Opening":
        self.set_states("opening","opening_unlit")
      case "Emagging":
        self.set_states("closed","sparks")
      case "Denying":
        self.set_states("closed","deny_unlit")
      case _:
        print("DOOR: THE WHAT")
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
      "enum.WeldableLayers.BaseWelded":False,
      "enum.DoorVisualLayers.BaseUnlit":True,
      "enum.DoorVisualLayers.BaseEmergencyAccess":False,
      "enum.WiresVisualLayers.MaintenancePanel":False
    },self.uid)

@component
class DoorBolt(BaseComponent):
  icobolt=verbs.icon("AdminActions/bolt.png",False)
  icounbolt=verbs.icon("AdminActions/unbolt.png",False)
  base_component={
    "BoltsUpSound":PathSound("/Audio/Machines/boltsup.ogg"),
    "BoltsDownSound":PathSound("/Audio/Machines/boltsdown.ogg"),
    "BoltsDown":False,
    "BoltLightsEnabled":True,
  }

  def __init__(self,entity,args):
    self.comp=self.base_component.copy()
    self.comp.update(args)
    self.uid=entity.uid

    events.subscribe("BeforeDoorOpened",self.WAIT_A_MINUTE,self.uid)
    events.subscribe("BeforeDoorClosed",self.WAIT_A_MINUTE,self.uid)
    events.subscribe("BeforeDoorDenied",self.WAIT_A_MINUTE,self.uid)
    events.subscribe("getVerbs",self.getVerbs,self.uid)
    self.update()

  def getVerbs(self,args):
    return [{
      "name":Loc("admin-trick-unbolt-description"),
      "priority":10,
      "img":self.icounbolt,
      "click":self.set_bolts_up,
    } if self.comp["BoltsDown"] else {
      "name":Loc("admin-trick-bolt-description"),
      "priority":10,
      "img":self.icobolt,
      "click":self.set_bolts_down,
    }]
  def set_bolts(self,state:bool):
    if self.get_bolts()==state:
      return False

    self.comp["BoltsDown"]=state
    self.comp["Bolts"+("Down" if state else "Up")+"Sound"].play()
    self.update()
    return True

  def set_bolts_up(self,args):
    self.set_bolts(False)
  def set_bolts_down(self,args):
    self.set_bolts(True)

  def get_bolts(self)->bool:
    return self.comp["BoltsDown"]

  def update(self):
    events.call("updateMap",{
      "enum.DoorVisualLayers.BaseBolted":self.get_bolts(),
    },self.uid)

  def WAIT_A_MINUTE(self,args):
    if self.comp["BoltsDown"]:
      args["cancelled"]=True

