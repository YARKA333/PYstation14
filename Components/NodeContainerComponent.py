from Utils.colors import colors
import Utils.events as events
import Utils.multidict
from Modules.component import BaseComponent,component
import Utils.shared as shared
from Utils.cheaper import *
from Utils.vector2 import Vector
import Modules.entityModule as eMod
from yaml_tag import tag
import pygame as pg
import math
import time
grid:Utils.multidict.Multidict=shared.get("globalgrid")

@component
class NodeContainer(BaseComponent):
  after = ["Transform"]
  def __init__(self,entity:eMod.Entity,comp):
    self.uid=entity.uid
    self.nodes:dict=comp.get("nodes",{})
    for node in self.nodes.values():
      if not node:continue
      node.init(entity)
      if shared.get("started"):
        node.connect()

def updpos(cell:list["Node"]):
  for i,node in enumerate(cell):
    c=len(cell)
    rel=i-(c-1)/2
    x,y=[(node.pos[e]*size+rel*nodesize) for e in [0,1]]
    node.ox=x
    node.oy=-y

def updpos_starter(args):
  for pos in grid.keys():
    cell=get_grid(pos)
    if cell:
      updpos(cell)
events.subscribe("start",updpos_starter)
dirs=[[0,0],[0,1],[1,0],[0,-1],[-1,0]]
nodegroups={}

def NodeGroup(*groups):
  def decorator(cls:type):
    for group in groups:
      nodegroups[group]=cls
    return cls
  return decorator

def to_grid(pos):return f"{pos[0]},{pos[1]}"
def get_grid(pos)->list["Node"]:
  ents=grid.get(str(pos))
  if not ents:
    return []
  nodes=[]
  for ent in ents:
    comp:NodeContainer=ent.comp("NodeContainer")
    if not comp:continue
    for node in comp.nodes.values():
      if node:
        nodes.append(node)
  return nodes

class Group:
  def __init__(self,nodes,groupid=None):
    self.groupId=groupid
    self.nodes=nodes
    for node in self.nodes:
      node.group=self
  def __iadd__(self, other:"Group"):
    for node in other.nodes:
      node.group=self
    self.nodes+=other.nodes
    return self

  def reflood(self):
    scans=[]
    for node in self.nodes:
      if any(node in sublist for sublist in scans):
        continue
      vis=[]
      node.scan(vis)
      scans.append(vis)
    for scan in scans:
      Group(scan)

class Node:
  ox=0
  oy=0
  group:Group
  nbrs:list["Node"]=[]
  def __init__(self,nodeGroupID=None):
    self.groupId=nodeGroupID
  def init(self,owner:eMod.Entity):
    self.owner=owner.uid
    self.pos=owner.xform.pos
    events.subscribe("get_all_nodes",lambda args:self)
    cell=get_grid(self.pos)
    if shared.get("started"):
      updpos(cell)
    #self.group=None
  def connect(self):
    nbrs=self.get_compatible()

    groups=[]
    for nbr in nbrs:
      if not nbr.group in groups:
        groups.append(nbr.group)

    if groups:
      self.group=groups[0]
      self.group.nodes.append(self)
      if len(groups)>1:
        for group in groups[1:]:
          self.group+=group
    else:
      self.group=Group([self],self.groupId)

  def remove(self):
    global rmqueue
    cell=get_grid(self.pos)
    cell.remove(self)
    self.group.nodes.remove(self)
    rmqueue.append(self)
    #self.reflood()
    self.group.reflood()
    updpos(cell)

  def reflood(self):
    scans=[]
    nbrs=list(self.get_compatible())
    if len(nbrs)<=1:
      return
    for i in nbrs:
      if any(i in sublist for sublist in scans):
        continue
      vis=[]
      i.scan(vis)
      scans.append(vis)
    if len(scans)<=1:
      return

    def compare_lists(list1,list2):
      return sorted([id(x) for x in list1])==sorted([id(x) for x in list2])

    if compare_lists(scans,self.group.nodes):
      return
    for n in scans:
      Group(n)
    rmqueue.append(self.group)

  def scan(self,visited):
    visited.append(self)
    for nbr in self.get_compatible():
      if nbr in visited:
        continue
      nbr.scan(visited)

  def __str__(self):
    return f"{self.__class__.__name__}:ent {self.owner}"
  def __repr__(self):
    return f"{self.__class__.__name__}:ent {self.owner}"
  def get_compatible(self)->list["Node"]:
    ret=[a for a in self.get_reachable() if a.groupId==self.groupId]
    self.nbrs=ret
    return ret
  def get_reachable(self)->list["Node"]:
    return [a[1] for a in self.get_cardinal_neighbours()]

  def get_cardinal_neighbours(self)->list[tuple[int,"Node"]]:
    for i,dir in enumerate(dirs):
      for node in get_grid(self.pos+dir):
        if node!=self:
          yield i,node


@tag()
class CableNode(Node):
  def get_reachable(self):
    nodeDirs=[]
    terminalDirs=[]
    for i,nbr in self.get_cardinal_neighbours():
      if isinstance(nbr,CableNode):
        nodeDirs.append((i,nbr))
      if isinstance(nbr,CableDeviceNode) and i==0:
        nodeDirs.append((i,nbr))
      if isinstance(nbr,CableTerminalNode):
        if i==0:
          terminalDirs.append(nbr.offset)
        else:
          off=Vector(dirs[i])
          if nbr.offset==-off:
            terminalDirs.append(off)
    for i,node in nodeDirs:
      if Vector(dirs[i]) in terminalDirs:
        continue
      yield node

@tag()
class CableDeviceNode(Node):
  def __init__(self,nodeGroupID,enabled=True):
    #self.enabled=enabled
    super().__init__(nodeGroupID)
  def get_reachable(self):
    for node in get_grid(self.pos):
      if isinstance(node,CableNode):
        yield node

@tag()
class CableTerminalNode(CableDeviceNode):
  dir:int
  offset:Vector
  def init(self,owner):
    super().init(owner)
    self.dir=owner.xform.get_dir()+1
    self.offset=Vector(dirs[self.dir])
  def get_reachable(self):
    for node in get_grid(self.pos):
      yield node
    for node in get_grid(self.pos+self.offset):
      if isinstance(node,CableTreminalPortNode):
        yield node

@tag()
class CableTreminalPortNode(Node):
  def get_reachable(self):
    for i,nbr in self.get_cardinal_neighbours():
      idir=Vector(dirs[i])
      if not isinstance(nbr,CableTerminalNode):
        continue
      if idir==-nbr.offset:
        yield nbr

types=[Node,CableNode,CableDeviceNode,CableTerminalNode,CableTreminalPortNode]
ctype:type=Node

def reflood(args=None):
  scans=[]
  for node in events.call("get_all_nodes",noreturn=False):
    if any(node in sublist for sublist in scans):
      continue
    vis=[]
    node.scan(vis)
    scans.append(vis)
  for scan in scans:
    Group(scan)
events.subscribe("start",reflood)


font=pg.Font()

size=64
nodesize=16

def toscreen(bpos,dpos,wh):
  return [
    -dpos[0]*2
    +wh[0]/2
    +bpos[0]*2,
   (-dpos[1]*2
    -wh[1]/2
    +(bpos[1]-1)*2)*-1+64]

nselected=None


def get_color(groupid):
  match groupid:
    case "HVPower": return colors["Orange"]
    case "MVPower": return colors["Yellow"]
    case "Apc":     return colors["LimeGreen"]
    case "AMEngine":return colors["Purple"]
    case "Pipe":    return colors["Blue"]
    case "WireNet": return colors["DarkMagenta"]
    case "Teg":     return colors["Red"]
    case _:         return colors["White"]

def debug_render(args):
  #nw=args["nw"]
  #nw("external")
  if not shared.get("nodevis"):return
  global nselected
  disp:pg.Surface=args["surf"]
  pos=args["gpos"]
  #screenRect=pg.Rect()
  sx,sy,sw,sh=-size/2,-size/2,disp.width+size/2,disp.height+size/2
  mx,my=pg.mouse.get_pos()
  selected=nselected
  nselected=None

  dx,dy=Vector(pos)*size-Vector(disp.size)/[2,-2]
  tempgrid:dict[str,list[Node]]={}
  #nw("prepare")
  for node in events.call("get_all_nodes",noreturn=False):
      #nw("iter")
      nx=node.ox-dx
      ny=node.oy+dy
      #nw("set")
      x,y=nx-.5*nodesize,ny-.5*nodesize
      #nw("vectors")
      dn=nodesize
      #nw("nums")
      if not colliderect(x,y,dn,dn,sx,sy,sw,sh):
        #nw("if")
        continue
      #nw("if")
      color=get_color(node.groupId)
      for nbr in node.nbrs:
        if node.owner<nbr.owner:
          continue
        pg.draw.line(disp,color,[nx,ny],[nbr.ox-dx,nbr.oy+dy])
      imgrect=pg.Surface([dn]*2)
      imgrect.fill(color)
      if selected:
        if node.group==selected.group:
          a=.75+math.sin(time.time()*4)*.25
        else:
          a=.2
      else:
        a=.5
      imgrect.set_alpha(a*255)
      disp.blit(imgrect,[x,y])
      #pg.draw.rect(disp,node.group.color,rect)
      if collidepoint(x,y,dn,dn,mx,my):
        nselected=node
      #nw("rendering itself")
    #except IndexError:print(node.owner)
  if selected:
    data=[
      f"ent: {selected.owner}",
      f"pos: {selected.pos}",
      f"groupId: {selected.groupId}",
      f"type: {selected.__class__.__name__}",
    ]
    #for i,text in enumerate(data):

    disp.blit(font.render("\n".join(data),True,[0,0,0]),(Vector(mx,my)+[20,-10]).pos)
  #nw("end")
events.subscribe("overlay",debug_render)