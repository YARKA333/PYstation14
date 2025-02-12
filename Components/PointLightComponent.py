import math
import pygame as pg
import Utils.shared as shared
import Utils.events as events
import random
from tqdm import tqdm
from Modules.component import BaseComponent,component
from Modules.rsi import rotate_vector
from Utils.colors import findcolor
from Utils.watch import watch

#lightchunks={}
lightkake={}

def iss(
    A:tuple[float,float],
    B:tuple[float,float],
    rect:pg.Rect|tuple[int,int,int,int]
    )->tuple[float,float]|None:
  """very scary function
  detects and returns intersection coords of
  ray A-B-> with rect
  """

  #Written by Qwen2.5-72B-Instruct
  x1,y1=A
  x2,y2=B
  x_min,y_min,x_max,y_max=rect
  # Calculate the direction vector of the ray
  dx=x2-x1
  dy=y2-y1
  # Initialize the closest intersection point and its distance
  closest_point=None
  closest_distance=float('inf')
  # Function to check if a point lies on a segment
  def point_on_segment(x,y,x1,y1,x2,y2):
    return (min(x1,x2)<=x<=max(x1,x2)) and (min(y1,y2)<=y<=max(y1,y2))
  # Check intersection with the left side (_x = x_min)
  if dx!=0:
    t=(x_min-x1)/dx
    if 0<=t:
      y=y1+t*dy
      if point_on_segment(x_min,y,x_min,y_min,x_min,y_max):
        distance=(x_min-x1)**2+(y-y1)**2
        if distance<closest_distance:
          closest_distance=distance
          closest_point=(x_min,y)
  # Check intersection with the right side (_x = x_max)
  if dx!=0:
    t=(x_max-x1)/dx
    if 0<=t:
      y=y1+t*dy
      if point_on_segment(x_max,y,x_max,y_min,x_max,y_max):
        distance=(x_max-x1)**2+(y-y1)**2
        if distance<closest_distance:
          closest_distance=distance
          closest_point=(x_max,y)
  # Check intersection with the bottom side (_y = y_max)
  if dy!=0:
    t=(y_max-y1)/dy
    if 0<=t:
      x=x1+t*dx
      if point_on_segment(x,y_max,x_min,y_max,x_max,y_max):
        distance=(x-x1)**2+(y_max-y1)**2
        if distance<closest_distance:
          closest_distance=distance
          closest_point=(x,y_max)
  # Check intersection with the top side (_y = y_min)
  if dy!=0:
    t=(y_min-y1)/dy
    if 0<=t:
      x=x1+t*dx
      if point_on_segment(x,y_min,x_min,y_min,x_max,y_min):
        distance=(x-x1)**2+(y_min-y1)**2
        if distance<closest_distance:
          closest_distance=distance
          closest_point=(x,y_min)
  return closest_point

size=64


def lerp(a,b,x):
  return a+(b-a)*x
def isql(a):
  return 1/(1+a**2)
def sigma(D,M):
  return 1/(1+math.exp((D-M)/(M/10)))
def falloff(x):
  return x
  #return -0.5*(math.cos(math.pi*_x)-1)
def randcirc():
  while 1:
    pos=(random.random()*2-1,random.random()*2-1)
    if math.hypot(abs(pos[0]),abs(pos[1]))<=1:return pos

@component
class Occluder(BaseComponent):
  after = ["Transform"]
  def __init__(self,entity,args):
    self.pos=None
    self.uid=entity.uid
    self.enabled=args.get("enabled",True)
    events.subscribe("setOccluder",self.set,entity.uid)
    events.followcomp("Transform",self.OnTransform,entity)
    if self.enabled:
      events.call("FOV_upd_object",{"uid":self.uid,"pos":self.pos})
      if shared.get("started"):
        self.updLights()
  def OnTransform(self,args):
    if self.enabled:
      if self.pos:
        rect1=self.get_rect()
        self.pos=args.pos
        rect2=self.get_rect()
        events.call("FOV_upd_object",{"uid":self.uid,"pos":self.pos})
        if shared.get("started"):
          events.call("UpdateLights",{"rects":[rect1,rect2]})
      else:
        self.pos=args.pos
        events.call("FOV_upd_object",{"uid":self.uid,"pos":self.pos})
        if shared.get("started"):
          events.call("UpdateLights",{"rect":self.get_rect()})
    else:
      self.pos=args.pos

  def get_rect(self):
    return pg.Rect([(self.pos[0]-.5)*size,(self.pos[1]-.5)*size,size,size])

  def updLights(self):
    events.call("UpdateLights",{"rect":self.get_rect()})

  def set(self,args):
    new=args.get("enabled",self.enabled)
    if new!=self.enabled:
      self.enabled=new
      args2={"uid":self.uid,"pos":self.pos}
      if new:events.call("FOV_upd_object",args2)
      else:  events.call("FOV_del_object",args2)
      events.call("UpdateLights",{"rect":self.get_rect()})

  #def precomp(self):
  #  self.sets=[]
  #  for set in range(4):
  #    match set:
  #      case 0:
  #        beh=[n,v] in objs
  #        lef=not [n-1,v-1] in objs
  #        rig=not [n+1,v-1] in objs
  #      case 1:
  #        beh=[v,n] in objs
  #        lef=not [v-1,n-1] in objs
  #        rig=not [v-1,n+1] in objs
  #      case 2:
  #        beh=[n,v-1] in objs
  #        lef=not [n-1,v] in objs
  #        rig=not [n+1,v] in objs
  #      case 3:
  #        beh=[v-1,n] in objs
  #        lef=not [v,n-1] in objs
  #        rig=not [v,n+1] in objs
  #    self.sets.append((beh,lef,rig))
@component
class PointLight(BaseComponent):
  after = ["Tranform"]
  base_component={
    "color":"#FFFFFF",
    "radius":5,
    "energy":1,
    "enabled":True,
    "castShadows":True,
  }
  def __init__(self,entity,args):
    self.uid=entity.uid
    self.comp=self.base_component.copy()
    self.comp.update(args)
    self.comp["uid"]=entity.uid
    events.followcomp("Transform",self.onTransform,entity)
  def onTransform(self,comp):
    offset=[float(a)*0.75 for a in self.comp.get("offset",'0,0').split(",")]
    self.rot=comp.rot
    self.comp["radius"]=min(self.comp["radius"],16)
    rotoffset=rotate_vector(offset,self.rot)
    self.comp.update({"gpos":[comp.pos[e]+rotoffset[e] for e in [0,1]]})
    if not self.comp["enabled"]:return
    if not self.comp["castShadows"]:return
    n={} if shared.get("started") else {"noupd":None}
    events.call("FOV_upd_light",{"uid":self.uid,"comp":self.comp}|n)

class FOV: #todo тоже почините
  def __init__(self):
    #events.subscribe("UpdateOccluder",self.UpdateObjs)
    #events.subscribe("start",self.UpdateObjs)
    events.subscribe("start",self.UpdateLights)
    events.subscribe("UpdateLights",self.UpdateLights)
    events.subscribe("FOV_upd_light",self.updLight)
    events.subscribe("FOV_upd_object",self.updObject)
    events.subscribe("FOV_del_light",self.delLight)
    events.subscribe("FOV_del_object",self.delObject)
    self.lightsarray={}
    self.init=0
    self.objects={}
  def UpdateObjs(self,args=None):
    self.init=1
    anchors=shared.get("globalgrid")
    entities=shared.get("entities")
    uids=shared.get("uids")
    self.objects={}
    for pos,objs in anchors.dict.items():
      for obj in objs:
        ent=entities[uids.index(obj)]
        if not ent.hascomp("Occluder"): continue
        if not ent.comp("Occluder").enabled: continue
        opos=[float(a) for a in pos[1:-1].split(",")]
        self.objects|={obj:[opos[0]-.5,-.5-opos[1]]}
        break
  def updObject(self,args):
    uid,pos=args["uid"],args["pos"]
    self.objects|={uid:[pos[0]-.5,-.5-pos[1]]}
  def delObject(self,args):
    self.objects.pop(args["uid"])
    #спасибо что выбрали YARtech!
  def updLight(self,args:dict):
    uid,comp=args["uid"],args["comp"]
    self.lightsarray|={uid:comp}
    if "noupd" in args:return
    self.updateLight(comp)

  def delLight(self,args):
    self.lightsarray.pop(args["uid"])

  def UpdateLights(self,args):
    if "rects" in args:
      rects=args["rects"]
    elif "rect" in args:
      rects=[args["rect"]]
    else:rects=[]
    lamps=self.lightsarray.values()
    a=0
    #t=time.time()
    #ts=[t]
    #print(f"started light calc: {t:.3f}")
    for l in tqdm(lamps,desc=f"Calculating light for {len(lamps)} lamps total"):
      self.updateLight(l,rects)
      #a+=b
      #if b:
        #ts.append(time.time())
        #print(f"lamp {a} calculated {time.time():.3f}")
    #print(f"calculated light for {a} lamps: {time.time():.3f}")
    #tss=[ts[i+1]-ts[i] for i in range(len(ts)-1)]
    #if tss:
    #  print(f"min:{min(tss):.3f},mean:{sum(tss)/len(tss):.3f},max:{max(tss):.3f}")

  def updateLight(self,l,rects:list[pg.Rect]=[]):
    global lightkake
    if rects and "rect" in l.keys():
      for rect in rects:
        if rect.colliderect(l["rect"]):break
      else:return False
    gpos=l["gpos"]
    l.update({"pos":[gpos[0],-gpos[1]]})
    rfcolor=findcolor(l["color"])
    smooth=l.get("softness",0)*4*0 #todo somethong
    energy=l["energy"]
    shadow=l.get("castShadows",True)
    if smooth:
      energy/=smooth
    fcolor=[min(rfcolor[i]*energy,255) for i in [0,1,2]]
    l.update({"fcolor":fcolor})
    R=l["radius"]
    l.update({"rect":pg.Rect((gpos[0]-R)*size,(gpos[1]-R)*size,2*R*size,2*R*size)})
    power=R*64
    if l["uid"]==shared.get("thechosenlamp"):
      print("LAMP LOG")
      print(gpos)
      print(R)
      print(l["rect"])
      print()
    kakename=f"{power},{rfcolor}"
    if kakename in lightkake:
      s1=lightkake[kakename]
    else:
      s1=pg.Surface([power*2]*2)
      s1.fill([0,0,0])
      for i in range(100):
        color=[int(lerp(0,l["fcolor"][e],falloff(i/100))) for e in range(3)]
        pg.draw.circle(s1,color,[power,power],power*(1-i/100))

      lightkake[kakename]=s1
    if smooth:
      s3=pg.Surface([(power+smooth)*2]*2)
      a=[]
      for i in range(8):
        s2=s1.copy()
        rpos=randcirc()
        rpos=[rpos[e]*smooth for e in [0,1]]
        if shadow:
          self.draw(s2,[l["pos"][0]*size+rpos[0],l["pos"][1]*size+rpos[1]])
        a.append((s2,[rpos[e]+smooth for e in [0,1]]))
      s3.fblits(a,pg.BLEND_ADD)
    else:
      s3=s1.copy()
      if shadow:
        self.draw(s3,[l["pos"][0]*size,l["pos"][1]*size])
    l.update({"img":pg.transform.invert(s3)})
    return True

  def draw(self,surf,pos,color=(0,0,0),simple=True): #todo optimise "in"
    objs=self.objects.values()
    #print(f"draw started {time.time():.3f}")
    w=watch()
    WIDTH,HEIGHT=surf.get_size()
    hwidth,hheight=WIDTH/2,HEIGHT/2
    sx,sy=pos
    for obj in objs:
      w("inbetween obj")
      for set in [0,1,2,3]:
        w("inbetween set")

        x,y=obj
        if set==0:
          v,n=[y+1,x]
        elif set==1:
          v,n=[x+1,y]
        elif set==2:
          v,n=[y,x]
        else:
          v,n=[x,y]

        w("setdecide")

        c=v*size
        x1=n*size
        x2=(n+1)*size
        if set%2:
          pos1=[hwidth+c-sx,hheight+x1-sy]
          pos2=[hwidth+c-sx,hheight+x2-sy]
        else:
          pos1=[hwidth+x1-sx,hheight+c-sy]
          pos2=[hwidth+x2-sx,hheight+c-sy]
        if pos1[0]<0 and pos2[0]<0: continue
        if pos1[0]>WIDTH and pos2[0]>WIDTH: continue
        if pos1[1]<0 and pos2[1]<0: continue
        if pos1[1]>HEIGHT and pos2[1]>HEIGHT: continue

        w("setdecide2")

        match set:
          case 0:
            vis=sy<c
            if not simple:
              beh=[n,v] in objs
              lef=not [n-1,v-1] in objs and sx<x1
              rig=not [n+1,v-1] in objs and sx>x2
          case 1:
            vis=sx<c
            if not simple:
              beh=[v,n] in objs
              lef=not [v-1,n-1] in objs and sy<x1
              rig=not [v-1,n+1] in objs and sy>x2
          case 2:
            vis=sy>c
            if not simple:
              beh=[n,v-1] in objs
              lef=not [n-1,v] in objs and sx<x1
              rig=not [n+1,v] in objs and sx>x2
          case 3:
            vis=sx>c
            if not simple:
              beh=[v-1,n] in objs
              lef=not [v,n-1] in objs and sy<x1
              rig=not [v,n+1] in objs and sy>x2
          case _:
            raise Exception()
        w("matchcase")

        if simple:
          if vis: continue
        elif not vis or beh and (lef or rig):
          continue  #

        w("simple")

        #pg.draw.line(surf,[[255,0,0],[255,255,0],[0,255,0],[0,100,255]][set],pos1,pos2,5)
        pos3=iss([hwidth,hheight],pos1,[0,0,WIDTH,HEIGHT])
        pos4=iss([hwidth,hheight],pos2,[0,0,WIDTH,HEIGHT])

        if pos3==None or pos4==None:
          print("skip")
          continue
        #pg.draw.polygon(surf,[0,0,0],[pos3,pos1,pos2,pos4])
        add=[]
        edges=[[0,0],[0,1],[1,1],[1,0]]
        if abs(pos4[0]-pos3[0])==WIDTH or abs(pos4[1]-pos3[1])==HEIGHT:
          for i in [[1,0],[0,1],[0,1],[1,0]][(set+simple*2)%4]:
            edge=edges[(set+i+1+simple*2)%4]
            add.append([edge[0]*WIDTH,edge[1]*HEIGHT])
        elif pos4[0]==pos3[0] or pos4[1]==pos3[1]:
          pass
        else:
          #pg.draw.line(surf,[0,0,255],pos3,pos4,5)
          c1=[pos3[0],pos4[1]]
          c2=[pos4[0],pos3[1]]
          if not c1[0] or c1[0]==WIDTH:
            add=[c1]
          else:
            add=[c2]

        pg.draw.polygon(surf,color,[pos3,pos1,pos2,pos4]+add)
        w("post non")

    #print(f"draw finished {time.time():.3f}")
    w.flush()

  def render(self,screen,pos,mode,mask=None): #todo understand...
    if not mode: return

    sx,sy=pos
    WIDTH,HEIGHT=screen.size
    nx,ny=sx-WIDTH/2,sy-HEIGHT/2
    if mode==3:
      screen.fill([255,0,255])
    wallsurf=pg.Surface([WIDTH,HEIGHT],pg.SRCALPHA)
    wallsurf.fill([0,0,0,0])
    wallsurf3=pg.Surface([WIDTH,HEIGHT])
    wallsurf3.fill([255,255,255])
    #wallsurf2.set_colorkey([0,0,0])
    for obj in self.objects.values():
      pos=[obj[0]*size-nx,obj[1]*size-ny,size,size]
      if pos[0]+size<0 or pos[1]+size<0:continue
      if pos[0]>WIDTH or pos[1]>HEIGHT:continue
      pg.draw.rect(wallsurf,[255,255,255,255],pos)
      pg.draw.rect(wallsurf3,[0,0,0],pos)
    s3=pg.Surface([WIDTH,HEIGHT])
    s3.fill([255,255,255])
    lightimgs=[]
    for l in self.lightsarray.values():
      img:pg.Surface=l["img"]
      radius=img.width/2
      pos=[-nx-radius+l["pos"][0]*size,-ny-radius+l["pos"][1]*size]
      if pos[0]+2*radius<0 or pos[1]+2*radius<0:continue
      if pos[0]>WIDTH or pos[1]>HEIGHT:continue
      lightimgs.append((img,pos))

    s3.fblits(lightimgs,pg.BLEND_MULT)
    s3=pg.transform.invert(s3)
    s3=pg.transform.gaussian_blur(s3,5)

    #wallsurf.convert_alpha()
    if mode==2:
      self.draw(s3,[sx,sy])
    if mode!=4:
      s35=s3.copy().convert_alpha()
      s3.blit(wallsurf,[0,0])
        #blank.blit(s3,[0,0],special_flags=pg.BLEND_RGB_MULT)#
      s35.blit(wallsurf,[0,0],special_flags=pg.BLEND_RGBA_SUB)
        #draw(s35,[sx,sy],lines,objs,simple=True)
      s4=pg.transform.box_blur(s35,64)
      s4.blit(s4,[0,0],special_flags=pg.BLEND_ADD)
        #s4=s3
        #wallsurf2.blit(s4,[0,0],special_flags=pg.BLEND_RGB_MULT)
      s4.blit(wallsurf3,[0,0],special_flags=pg.BLEND_RGB_MAX)
      s3.blit(s4,[0,0],special_flags=pg.BLEND_MULT)
    if mask:
      s3.blit(mask.to_surface(),[0,0],special_flags=pg.BLEND_MAX)
    if mode==2:
      self.draw(s3,[sx,sy],simple=False)
    screen.blit(s3,[0,0],special_flags=pg.BLEND_MULT)

    for l in self.lightsarray.values():
      pg.draw.circle(screen,[255,0,0],[-nx+l["pos"][0]*size,-ny+l["pos"][1]*size],5)
      if l["uid"]!=shared.get("thechosenlamp"):continue
      rect:pg.Rect=l["rect"]
      img:pg.Surface=l["img"]
      radius=img.width/2
      #print((rect._x+.5*rect.w)/size,(rect._y+.5*rect.h)/size)
      pg.draw.rect(screen,[0,128,255],[-nx+rect.x,-ny-rect.y-rect.h+size,rect.w,rect.h],10)
      pg.draw.circle(screen,[0,128,255],[-nx+(rect.x+.5*rect.w),-ny-rect.y-.5*rect.h+size],10)
      #pg.draw.rect(screen,[255,0,0],[-nx+(l["pos"][0])*size-radius,-ny+(l["pos"][1])*size-radius,2*radius,2*radius],5)
      pg.draw.circle(screen,[255,0,0],[-nx+l["pos"][0]*size,-ny+l["pos"][1]*size],radius,5)

    #rect= shared.get("testrect")
    #if rect:
    #  print((rect._x+.5*rect.w)/size,(rect._y+.5*rect.h)/size)
    #  pg.draw.rect(screen,[0,128,255],[-nx+rect._x,-ny-rect._y-rect.h+size,rect.w,rect.h],5)
    #  pg.draw.circle(screen,[0,128,255],[-nx+(rect._x+.5*rect.w),-ny-rect._y-.5*rect.h+size],5)

    return screen

shared.set("thechosenlamp",1696)