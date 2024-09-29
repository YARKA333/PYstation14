import Utils.events as events
from Modules.rsi import *
from colors import colors
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
    self.icon=dict.get(component,"sprite")
    if self.icon:
      self.color=dict.get(
        colors,
        dict.get(component,"color","White"),
        (255,255,255,255))
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
      name=self.composename(self.icon,layer,self.color,self.rot)
      if name in allsprites.keys():
        self.rotlayers.append(allsprites[name])
      else:
        image=self.rsi(state=state)
        if self.color[0:4]!=(255,255,255):
          image.fill(self.color,special_flags=pg.BLEND_RGB_MULT)
        rimage=pg.transform.rotate(image,self.rot)
        allsprites.update({name:rimage})
        self.rotlayers.append(rimage)
  def move(self,comp):
    self.pos=comp.pos
    self.rot=comp.rot
    self.calcsprites()
  def composename(self,*args):
    return ":".join([str(a) for a in args])
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