import Utils.events as events
from Modules.rsi import *
allsprites={}
rotsprites={}

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
      events.subscribe("setspritelayer",self.setlayer,entity.uid)
      self.rsi=loadrsi(self.icon)
      self.states=dict.get(component,"layers")
      self.state=dict.get(component,"state")
      if not self.states:
        self.states=[{"state":self.state}]
      events.subscribe("render",self.render)
      events.subscribe("Transform",self.move,self.uid)
      self.calcsprites()
    events.call("Sprite",self,self.uid)

  def calcsprites(self):
    self.rotlayers=[]
    for layer in self.states:
      state=dict.get(layer,"state")
      if not state: continue
      name=f'{state}:{self.rot}'
      if name in rotsprites.keys():
        self.rotlayers.append(rotsprites[name])
      else:
        image=self.rsi(state=state)
        rimage=pg.transform.rotate(image,self.rot)
        rotsprites.update({name:rimage})
        self.rotlayers.append(rimage)
  def move(self,comp):
    self.pos=comp.pos
    self.rot=comp.rot
    self.calcsprites()
  def composename(self,path,state,color):
    return f'{path}:{state}:{color}'
  def setlayer(self,args):
    index=dict.get(args,"index",0)
    name=args["state"]
    self.states[index]={"state":name}
    self.calcsprites()
  def render(self,args:dict):
    depth=dict.get(args,"depth")
    if depth==self.depth:
      dst:pg.Surface=args["dst"]
      pos:tuple=args["pos"]
      dst_wh:tuple=dst.get_size()
      dpos_raw=[-pos[0]
            +dst_wh[0]/2
            +self.pos[0]*32,
            (-pos[1]
             -dst_wh[1]
             +dst_wh[1]/2
             +(self.pos[1]-1)*32)*-1]
      if -32<dpos_raw[0]<1920 and -32<dpos_raw[1]<1080:
        for layer in self.rotlayers:
          img_wh=layer.get_size()
          dst.blit(layer,[dpos_raw[i]-img_wh[i]/2 for i in [0,1]])