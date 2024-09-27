import Utils.events as events
from Modules.rsi import *
allsprites={}

class Sprite:
  def __init__(self,entity,component):
    self.depth=dict.get(component,"drawdepth")
    if not self.depth:
      print("no depth!")
      self.depth="Overlays"
    self.uid=entity.uid
    self.pos=entity.pos
    self.rot=entity.rot
    #print(f'{entity.uid} called Sprite with {component}')
    self.icon=dict.get(component,"sprite")
    if self.icon:
      self.rsi=loadrsi(self.icon)
      self.states=dict.get(component,"layers")
      self.state=dict.get(component,"state")
      if not self.states:
        self.states=[{"state":self.state}]
      events.subscribe("render",self.render)
      events.subscribe("Transform",self.move,self.uid)
      self.layers=[]
      for layer in self.states:
        state=dict.get(layer,"state")
        if not state:continue
        self.layers.append(self.rsi(state=state))
      self.calcsprites()
    events.call("Sprite",self,self.uid)
  def calcsprites(self):
    self.rotlayers=[]
    for layer in self.layers:
      self.rotlayers.append(
        pg.transform.rotate(layer,self.rot))
  def move(self,comp):
    self.pos=comp.pos
    self.rot=comp.rot
    self.calcsprites()
  def composename(self,path,state,color):
    return f'{path}:{state}:{color}'

  def render(self,args:dict):
    depth=dict.get(args,"depth")
    if depth==self.depth:
      dst:pg.Surface=args["dst"]
      pos:tuple=args["pos"]
      dst_wh:tuple=dst.get_size()
      for layer in self.rotlayers:
        img_wh=layer.get_size()
        dpos=[-pos[0]
           -img_wh[0]/2
           +dst_wh[0]/2
           +self.pos[0]*32,
           (-pos[1]-dst_wh[1]
           -img_wh[1]/2
           +dst_wh[1]/2
           +self.pos[1]*32)*-1]
        dst.blit(layer,dpos)