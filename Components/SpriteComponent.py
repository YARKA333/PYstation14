import Utils.events as events
from Modules.rsi import *
import Modules.mouseHandler as mouse
from Utils.vector2 import Vector
from Components.InteractionOutlineComponent import outline
from colors import colors
import Utils.shared as shared
import random
import time
import copy
allsprites={}
allshades={}
allshadebools={}
mode="anim"

#shaded=[pg.mask.Mask([512,256])]
#shared.set("shaded_map",shaded)
#def reset(args):shaded[0].fill()
#events.subscribe("frame",reset)

#def resize(args):
#  shaded=[pg.mask.Mask(args["render"])]
#  shared.set("shaded_map",shaded)
#events.subscribe("resize",resize)
def addshade(dst:pg.mask,src:pg.Surface,pos:list=[0,0],erase:bool=False):
  #mask=pg.mask.from_surface(src)
  if erase:
    dst.erase(src,pos)
  else:
    dst.draw(src,pos)

def optishade(masks:list[pg.mask.Mask],bools:list[bool])->list[pg.mask.Mask]:
  i=1
  while 1:
    if i>=len(bools):
      break
    if bools[i-1]==bools[i]:
      masks[i-1].draw(masks[i],[0,0])
      masks.pop(i)
      bools.pop(i)
      continue
    i+=1





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
    self.renderevent=None
    if self.icon:
      self.layerMap={}
      self.color=dict.get(
        colors,
        dict.get(component,"color","White"),
        (255,255,255,255))
      events.subscribe("setspritelayer",self.setlayer,entity.uid)
      events.subscribe("setvis",self.setvis,entity.uid)
      events.subscribe("updateMap",self.updateMap,entity.uid)
      events.subscribe("setDepth",self.setdepth,entity.uid)
      self.rsi=loadrsi(self.icon)
      self.states=dict.get(component,"layers")
      self.state=dict.get(component,"state")
      if not self.states:
        self.states=[{"state":self.state}]
      self.offsets=[[float(a)*32 for a in state.get("offset",'0,0').split(",")] for state in self.states]
      for layer in self.states:
        layer.update({"shaded":False if layer.get("shader",None)=="unshaded" else True})
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
    self.rotshaders=[]
    names=[]
    for i in range(len(self.states)):
      layer=self.states[i]
      try:
        offset=self.offsets[i]
        overdir=self.dirs[i]
      except:
        print(self.states)
        print(self.offsets)
        print(self.dirs)
        offset=[0,0]
        overdir=None
      if not layer.get("visible",True):
        self.time=0
        continue
      layerMap=layer.get("map",None)
      if layerMap and not self.layerMap.get(layerMap[0],True):
        continue
      if not self.time:self.time=time.time()
      state=layer.get("state")
      if not state: continue

      #calculate rotation
      dirs=self.rsi.getdirs(state,nowarn=nowarn)
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

      #find name of image
      frame=self.rsi.getframe(state=state,dir=dir,otime=self.time,nowarn=True)
      name=self.composename(self.icon,state,frame,self.color,self.rot)
      names.append(name)
      if name in allsprites.keys():
        image=allsprites[name] #get cached image
      else: #generate new
        image=self.rsi(state=state,dir=dir,frame=frame,nowarn=True)
        if self.color[0:3]!=(255,255,255):
          image.fill(self.color,special_flags=pg.BLEND_RGB_MULT)
        if rot:
          image=pg.transform.rotate(image,self.rot)
        allsprites.update({name:image})
      self.rotlayers.append(image)
      #add shadebool
      self.rotshaders.append(layer.get("shaded",True))
      #rotate and add offset
      self.rotoffsets.append(rotate_vector(offset,self.rot))

      #define new image size
      halfsize=Vector(image.get_size())/2
      edges=(halfsize*-1).pos+halfsize.pos
      offset_edges=[edges[i]+self.rotoffsets[-1][i%2] for i in range(4)]
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
    if name in allsprites.keys() and name in allshades.keys():
      self.final=allsprites[name]
      self.shading=allshades[name]
      self.rotshaders=allshadebools[name]
    else:
      self.shading=[]
      #print(f"new final {name}")
      self.final=pg.Surface(self.size,pg.SRCALPHA)
      for j in range(len(self.rotlayers)):
        layer=self.rotlayers[j]
        offset=self.rotoffsets[j]
        img_wh=layer.get_size()
        pos=[self.center[i]-img_wh[i]/2+offset[i] for i in [0,1]]
        self.shading.append(pg.mask.from_surface(layer))
        #addshade(self.shading,layer,pos,self.rotshaders[i])
        self.final.blit(layer,pos)
      optishade(self.shading,self.rotshaders)
      allshadebools.update({name:self.rotshaders})
      allshades.update({name:self.shading})
      allsprites.update({name:self.final})
  def move(self,comp):
    self.pos=comp.pos
    cpos=[int(self.pos[i]//16) for i in [0,1]]
    if cpos!=self.cpos:
      #events.unsubscribe(f"render:{self.depth}:{self.cpos}",self.render)
      self.cpos=cpos
      #print(f"render:{self.depth}:{self.cpos}")
      self.resub()
    self.rot=comp.rot
    if mode=="stat":
      self.calcsprites()
  def resub(self):
    events.unsubscribe(self.renderevent)
    self.renderevent=events.subscribe(f"render:{self.depth}:{self.cpos}",self.render)
  def setvis(self,args):
    self.visible=args

  def updateMap(self,args):
    self.layerMap.update(args)

  def composename(self,*args):
    return ":".join([str(a) for a in args])

  def setdepth(self,args):
    self.depth=args.get("depth",self.depth)
    print(f"{self.uid} set depth to {args.get("depth")}")
    self.resub()

  def setlayer(self,args:dict):
    index=args.get("index",0)
    if len(self.states)<=index and not args.get("force",False):return
    while len(self.states)<=index:
      self.states.append({})
      self.offsets.append([0,0])
      self.dirs.append(None)
    self.dirs[index]=args.get("dir",None)
    self.states[index].update({"state":args["state"]})
    self.time=time.time()
    if mode=="stat":
      self.calcsprites()

  def render(self,args:dict):
    if self.pos==[0,0]:return
    if not self.visible:return
    dst:pg.Surface=args["dst"]
    smap:pg.Surface=args["smap"]
    pos:tuple=args["pos"]
    dst_wh:tuple=dst.get_size()
    dpos=[-pos[0]
          +dst_wh[0]/2
          +self.pos[0]*32,
         (-pos[1]
          -dst_wh[1]/2
          +(self.pos[1]-1)*32)*-1]
    if -16<dpos[0]<976 and -16<dpos[1]<556:
      if mode=="anim":
        self.calcsprites()
      fpos=[dpos[i]-self.center[i] for i in [0,1]]
      if mouse.lasthovered==self.uid and self.entity.hascomp("InteractionOutline"):
        mouse.active=1
        dst.blit(outline(self.final),[fpos[i]-1 for i in [0,1]])
      for i in range(len(self.rotshaders)):
        s,b=self.shading[i],self.rotshaders[i]
        addshade(smap,s,fpos,b)
      dst.blit(self.final,fpos)
      mouse.check(self.final,fpos,self.uid)

