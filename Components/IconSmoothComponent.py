import pickle
from Modules.rsi import *
import math
import pygame as pg
import Utils.events as events
import Utils.shared as shared
import Modules.entityModule as entityModule
grid=shared.get("globalgrid")



class IconSmooth:
  def __init__(self,entity,args):
    self.pos=[0,0]
    self.rpos=1
    self.uid=entity.uid
    self.ctype=dict.get(args,"key")
    self.mode=dict.get(args,"mode","Corners")
    #events.subscribe("scanpos",self.OnScan)
    if self.mode=="Corners":
      self.cpos=[-0.5,-0.5]
      self.depth="Objects"
      self.rsi=loadrsi("deprecated.rsi")
      self.dstate=dict.get(args,"base")
      self.calcsprite()
      events.followcomp("Sprite",self.OnSprite,entity)
      #events.subscribe(f"render:{self.depth}:{self.cpos}",self.OnRender)
      events.subscribe("pingpos",self.OnPing)
    events.followcomp("Transform",self.OnTransform,entity)


  def scanold(self):
    self.nbrs=[]
    for i in range(8):
      dif=vec(i)
      pos=[dif[e]+self.pos[e] for e in [0,1]]
      self.nbrs.append(1 in events.call("scanpos",{"ctype":self.ctype,"pos":self.pos}))
    print(f'scanned {self.pos} with {self.nbrs}')

  def scan(self):
    self.nbrs=[]
    for i in range(8):
      dif=vec(4-i)
      pos=[dif[e]+self.pos[e] for e in [0,1]]
      uids=grid.get(str(pos))
      for uid in uids:
        entity=entityModule.find(uid)
        if not entity:continue
        comp=entity.comp("IconSmooth")
        if not comp:continue
        if comp.ctype!=self.ctype:continue
        self.nbrs.append(1)
        break
      else:
        self.nbrs.append(0)
    #print(f'scanned {self.pos} with results {self.nbrs}')


  def OnTransform(self,comp):
    #events.call("pingpos",{"pos":self.pos,"ctype":self.ctype,"uid":self.uid})
    self.pos=comp.pos
    if self.mode=="Corners":
      cpos=[int(self.pos[i]//16) for i in [0,1]]
      if cpos!=self.cpos:
        #events.unsubscribe(f"render:{self.depth}:{self.cpos}",self.OnRender)
        self.cpos=cpos
        #events.subscribe(f"render:{self.depth}:{self.cpos}",self.OnRender)
      self.calcsprite()
    self.rpos=0
  def OnSprite(self,args):
    self.depth=args.depth
    self.rsi=loadrsi(args.icon)
    self.calcsprite()
  def OnScan(self,args):
    if dict.get(args,"ctype")!=self.ctype:return 0
    if dict.get(args,"pos")!=self.pos:return 0
    if self.rpos:return 0
    return 1
  def calcsprite(self):
    self.scan()
    self.sprite=pg.Surface([32,32],pg.SRCALPHA)
    for i in range(0,8,2):
      state=f"{self.dstate}{
         self.nbrs[i%8]*4+
         self.nbrs[(i+1)%8]*2+
         self.nbrs[(i+2)%8]}"
      events.call("setspritelayer",{"index":int(i/2),"state":state,"dir":i//2,"force":True},self.uid)
      #self.sprite.blit(self.rsi(1,state,
      #   [0,2,1,3][i//2]),[0,0])
  def OnPing(self,args):
    #if dict.get(args,"uid")==self.uid:return
    #if dict.get(args,"ctype")!=self.ctype:return
    #diff=[args["pos"][i]-self.pos[i] for i in [0,1]]
    #if not [abs(diff[i])<=1 for i in [0,1]] or diff==[0,0]:return
    self.calcsprite()

  def OnRender(self,args):
    dst:pg.Surface=args["dst"]
    pos:tuple=args["pos"]
    dst_wh:tuple=dst.get_size()
    dpos=[-pos[0]
          -16
          +dst_wh[0]/2
          +self.pos[0]*32,
         (-pos[1]
          -dst_wh[1]
          -16
          +dst_wh[1]/2
          +self.pos[1]*32)*-1]
    if -32<dpos[0]<960 and -32<dpos[1]<540:
      dst.blit(self.sprite,dpos)
