import Utils.events as events
from Modules.rsi import *
from Utils.vector2 import Vector
from Components.InteractionOutlineComponent import check_col,outline
from colors import colors
import random
import time
allsprites={}
mode="anim"
hovered=0
ishovered=0
lasthovered=0
def reset(arg):
  global ishovered,hovered,lasthovered
  if not ishovered:
    hovered=0
  lasthovered=hovered
  ishovered=0
  return {"hover":hovered}
events.subscribe("frame",reset)

class Sprite:
  def __init__(self,entity,component):
    self.entity=entity
    self.time=random.random()*10
    self.depth=dict.get(component,"drawdepth","Objects")
    self.uid=entity.uid
    self.pos=entity.pos
    self.rot=entity.rot
    self.noRot=dict.get(component,"noRot")
    self.icon=dict.get(component,"sprite")
    self.visible=True
    if self.icon:
      self.color=dict.get(
        colors,
        dict.get(component,"color","White"),
        (255,255,255,255))
      events.subscribe("setspritelayer",self.setlayer,entity.uid)
      events.subscribe("setvis",self.setvis,entity.uid)
      self.rsi=loadrsi(self.icon)
      self.states=dict.get(component,"layers")
      self.state=dict.get(component,"state")
      if not self.states:
        self.states=[{"state":self.state}]
      self.offsets=[[float(a)*32 for a in state.get("offset",'0,0').split(",")] for state in self.states]
      self.dirs=[None]*len(self.states)
      self.cpos=[-0.5,-0.5]
      #events.subscribe(f"render:{self.depth}:{self.cpos}",self.render)
      events.followcomp("Transform",self.move,entity)
      if mode=="stat":
        self.calcsprites(nowarn=False)
    events.call("Sprite",self,self.uid)

  def calcsprites(self,nowarn:bool=True):
    self.rotlayers=[]
    self.rotoffsets=[]
    self.edges=None
    names=[]
    for i in range(len(self.states)):
      offset=self.offsets[i]
      layer=self.states[i]
      if not layer.get("visible",True):
        self.time=0
        continue
      if not self.time:self.time=time.time()
      state=layer.get("state")
      if not state: continue
      dirs=self.rsi.getdirs(state,nowarn=nowarn)
      overdir=self.dirs[i]
      if overdir==None:
        if dirs==4:
          dir=[0,2,1,3][(self.rot+45)//90]
        else:
          dir=0
      else:dir=[0,2,1,3][overdir]
      if self.noRot:
        rot=0
      else:
        if dirs==4:
          rot=(self.rot+45)%90-45
        else:
          rot=self.rot
      frame=self.rsi.getframe(state=state,dir=dir,otime=self.time,nowarn=True)
      name=self.composename(self.icon,state,frame,self.color,self.rot)
      names.append(name)
      if name in allsprites.keys():
        image=allsprites[name]
      else:
        image=self.rsi(state=state,dir=dir,frame=frame,nowarn=True)
        if self.color[0:3]!=(255,255,255):
          image.fill(self.color,special_flags=pg.BLEND_RGB_MULT)
        if rot:
          image=pg.transform.rotate(image,self.rot)
        allsprites.update({name:image})
      self.rotlayers.append(image)
      if offset!=[0,0]:
        rotoffset=rotate_vector(offset,self.rot)
      else:
        rotoffset=[0,0]
      self.rotoffsets.append(rotoffset)
      halfsize=Vector(image.get_size())/2
      edges=(halfsize*-1).pos+halfsize.pos
      offset_edges=[edges[i]+rotoffset[i%2] for i in range(4)]
      if self.edges==None:
        self.edges=edges
      else:
        self.edges[0]=min(self.edges[0],edges[0])
        self.edges[1]=min(self.edges[1],edges[1])
        self.edges[2]=max(self.edges[2],edges[2])
        self.edges[3]=max(self.edges[3],edges[3])
    if self.edges==None:self.edges=[0,0,0,0]
    self.center=[-self.edges[0],-self.edges[1]]
    self.size=[self.edges[i+2]+self.center[i] for i in [0,1]]
    name=";".join(names)
    if name in allsprites.keys():
      self.final=allsprites[name]
    else:
      #print(f"new final {name}")
      self.final=pg.Surface(self.size,pg.SRCALPHA)
      for j in range(len(self.rotlayers)):
        layer=self.rotlayers[j]
        offset=self.rotoffsets[j]
        img_wh=layer.get_size()
        self.final.blit(layer,[self.center[i]-img_wh[i]/2+offset[i] for i in [0,1]])
      allsprites.update({name:self.final})
  def move(self,comp):
    self.pos=comp.pos
    cpos=[int(self.pos[i]//16) for i in [0,1]]
    if cpos!=self.cpos:
      #events.unsubscribe(f"render:{self.depth}:{self.cpos}",self.render)
      self.cpos=cpos
      #print(f"render:{self.depth}:{self.cpos}")
      events.subscribe(f"render:{self.depth}:{self.cpos}",self.render)
    self.rot=comp.rot
    if mode=="stat":
      self.calcsprites()

  def setvis(self,args):
    self.visible=args
    #if "layer" in args.keys():
    #  self.states.get[args["layer"]].update({"visible":args["value"]})
    #else:
    #  for layer in self.states:
    #    layer.update({"visible":args["value"]})


  def composename(self,*args):
    return ":".join([str(a) for a in args])

  def setlayer(self,args:dict):
    index=args.get("index",0)
    while len(self.states)<=index:
      self.states.append(None)
      self.offsets.append([0,0])
      self.dirs.append(0)
    name=args["state"]
    self.dirs[index]=args.get("dir",0)
    self.states[index]={"state":name}
    if mode=="stat":
      self.calcsprites()

  def render(self,args:dict):
    global hovered,ishovered
    if self.pos==[0,0]:return
    if not self.visible:return
    select=False
    dst:pg.Surface=args["dst"]
    pos:tuple=args["pos"]
    dst_wh:tuple=dst.get_size()
    dpos=[-pos[0]
          +dst_wh[0]/2
          +self.pos[0]*32,
         (-pos[1]
          -dst_wh[1]
          +dst_wh[1]/2
          +(self.pos[1]-1)*32)*-1]
    if -16<dpos[0]<976 and -16<dpos[1]<556:
      if mode=="anim":
        self.calcsprites()
      fpos=[dpos[i]-self.center[i] for i in [0,1]]
      if lasthovered==self.uid and self.entity.hascomp("InteractionOutline"):
        dst.blit(outline(self.final),[fpos[i]-1 for i in [0,1]])
      dst.blit(self.final,fpos)
      if check_col(self.final,fpos):
        hovered=self.uid
        ishovered=1
