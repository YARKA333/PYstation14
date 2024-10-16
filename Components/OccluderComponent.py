import math

import pygame as pg
import Utils.shared as shared
import Utils.events as events
from tqdm import tqdm
#from Modules.rsi import findcolor

def hextorgb(hex:str,nowarn=False)->list:
  """Converts hex color string to rgb(a) format
  \n For example:
  \n   '#FF2AB5EC' -> [255,42,181,236]"""

  hex2=hex.replace("#","")
  try:
    return [int(hex2[i*2:i*2+2],16) for i in range(len(hex2)//2)]
  except:
    if not nowarn:
      print(f"hextorgb failed: {hex}")

def findcolor(color:str):
  if type(color)==list:return color
  new=hextorgb(color,True)
  if new:return new
  new=colors.get(color.capitalize())
  if new:return new
  print(f"color not found: {color}")
  return [255,0,255]

def get(grid,x,y):
  if y<0 or y>=len(grid):return 0
  if x<0 or x>=len(grid[0]):return 0
  return grid[y][x]

def linify(grid):
  lines=[[],[],[],[]]
  for y in range(len(grid)+1):
    lines[0].append([])
    lines[2].append([])
    for x in range(len(grid[0])):
      a=get(grid,x,y-1)
      b=get(grid,x,y)
      if a: lines[0][-1].append(x)
      if b: lines[2][-1].append(x)
  for x in range(len(grid[0])+1):
    lines[1].append([])
    lines[3].append([])
    for y in range(len(grid)):
      a=get(grid,x-1,y)
      b=get(grid,x,y)
      if a: lines[1][-1].append(y)
      if b: lines[3][-1].append(y)
  return lines

def objlinify(objs):
  lines=[[],[],[],[]]
  for obj in objs:
    x,y=obj
    lines[0].append([y+1,x])
    lines[1].append([x+1,y])
    lines[2].append([y,x])
    lines[3].append([x,y])
  return lines

def iss(A,B,rect):#Written by Qwen2.5-72B-Instruct, not yarka
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
  # Check intersection with the left side (x = x_min)
  if dx!=0:
    t=(x_min-x1)/dx
    if 0<=t:
      y=y1+t*dy
      if point_on_segment(x_min,y,x_min,y_min,x_min,y_max):
        distance=(x_min-x1)**2+(y-y1)**2
        if distance<closest_distance:
          closest_distance=distance
          closest_point=(x_min,y)
  # Check intersection with the right side (x = x_max)
  if dx!=0:
    t=(x_max-x1)/dx
    if 0<=t:
      y=y1+t*dy
      if point_on_segment(x_max,y,x_max,y_min,x_max,y_max):
        distance=(x_max-x1)**2+(y-y1)**2
        if distance<closest_distance:
          closest_distance=distance
          closest_point=(x_max,y)
  # Check intersection with the bottom side (y = y_max)
  if dy!=0:
    t=(y_max-y1)/dy
    if 0<=t:
      x=x1+t*dx
      if point_on_segment(x,y_max,x_min,y_max,x_max,y_max):
        distance=(x-x1)**2+(y_max-y1)**2
        if distance<closest_distance:
          closest_distance=distance
          closest_point=(x,y_max)
  # Check intersection with the top side (y = y_min)
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

def draw(surf,pos,objs,color=[0,0,0],simple=False):
  WIDTH,HEIGHT=surf.get_size()
  hwidth,hheight=WIDTH/2,HEIGHT/2
  sx,sy=pos
  for obj in objs:
    for set in range(4):
      x,y=obj
      if set==0:
        v,n=[y+1,x]
      elif set==1:
        v,n=[x+1,y]
      elif set==2:
        v,n=[y,x]
      elif set==3:
        v,n=[x,y]

      c=v*size
      x1=n*size
      x2=(n+1)*size
      if set%2:
        pos1=[hwidth+c-sx,hheight+x1-sy]
        pos2=[hwidth+c-sx,hheight+x2-sy]
      else:
        pos1=[hwidth+x1-sx,hheight+c-sy]
        pos2=[hwidth+x2-sx,hheight+c-sy]
      if pos1[0]<0 and pos2[0]<0:continue
      if pos1[0]>WIDTH and pos2[0]>WIDTH: continue
      if pos1[1]<0 and pos2[1]<0: continue
      if pos1[1]>HEIGHT and pos2[1]>HEIGHT: continue
      if set==0:
        vis=sy<c
        beh=[n,v] in objs
        #pg.draw.line(surf,[255,255,255],[c,x1+8],[c+8,x1+8])
        lef=not [n-1,v-1] in objs and sx<x1
        rig=not [n+1,v-1] in objs and sx>x2
      elif set==1:
        vis=sx<c
        beh=[v,n] in objs
        #pg.draw.line(surf,[255,255,255],[c,x1+8],[c+8,x1+8])
        lef=not [v-1,n-1] in objs and sy<x1
        rig=not [v-1,n+1] in objs and sy>x2
      elif set==2:
        vis=sy>c
        beh=[n,v-1] in objs
        #pg.draw.line(surf,[255,255,255],[c,x1+8],[c+8,x1+8])
        lef=not [n-1,v] in objs and sx<x1
        rig=not [n+1,v] in objs and sx>x2
      elif set==3:
        vis=sx>c
        beh=[v-1,n] in objs
        #pg.draw.line(surf,[255,255,255],[c,x1+8],[c+8,x1+8])
        lef=not [v,n-1] in objs and sy<x1
        rig=not [v,n+1] in objs and sy>x2
      if simple:
        if vis:continue
      elif not vis or beh and (lef or rig):continue #

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


def lerp(a,b,x):
  return a+(b-a)*x

def isql(a):
  return 1/(1+a**2)

def sigma(D,M):
  return 1/(1+math.exp((D-M)/(M/10)))

def falloff(x):
  return -0.5*(math.cos(math.pi*x)-1)


class Occluder:
  def __init__(self,entity,args):
    self.enabled=args.get("enabled",True)
    events.subscribe("setOccluder",self.set,entity.uid)

  def set(self,args):
    new=args.get("enabled",self.enabled)
    if new!=self.enabled:
      self.enabled=new
      events.call("UpdateOccluder")


class FOV:
  def __init__(self):
    events.subscribe("UpdateOccluder",self.UpdateObjs)
    events.subscribe("start",self.UpdateObjs)
    events.subscribe("start",self.UpdateLights)
    events.subscribe("addLightSource",self.addLight)
    self.lightsarray=[]
    self.init=0
  def UpdateObjs(self,args=None):
    self.init=1
    anchors=shared.get("globalgrid")
    entities=shared.get("entities")
    uids=shared.get("uids")
    self.objects=[]
    for pos,objs in anchors.dict.items():
      for obj in objs:
        ent=entities[uids.index(obj)]
        if not ent.hascomp("Occluder"): continue
        if not ent.comp("Occluder").enabled: continue
        opos=[float(a) for a in pos[1:-1].split(",")]
        self.objects.append([opos[0]-.5,.5-opos[1]])
        break
  def addLight(self,args:dict):
    self.lightsarray.append(args)
    if self.init:
      self.updateLight(args)
  def UpdateLights(self,args):
    rect=args.get("rect",None) if args else None
    for l in self.lightsarray:
      self.updateLight(l,rect)
  def updateLight(self,l,rect:pg.Rect|None=None):
    if (rect and "rect" in l.keys() and not
       rect.colliderect(l["rect"])):return
    gpos=l["gpos"]
    l.update({"pos":[gpos[0],1-gpos[1]]})
    fcolor=findcolor(l["color"])
    energy=l["energy"]
    l.update({"fcolor":[min(fcolor[i]*energy,255) for i in [0,1,2]]})
    R=l["radius"]
    power=R*64
    s1=pg.Surface([power*2]*2)
    s1.fill([0,0,0])
    for i in range(100):
      pg.draw.circle(s1,[int(lerp(0,l["fcolor"][e],falloff(i/100))) for e in range(3)],[power,power],
                     power*(1-i/100))
    s2=pg.Surface([power*2]*2)
    s2.fill([255,255,255])
    draw(s2,[l["pos"][0]*size,l["pos"][1]*size],self.objects,simple=True)
    s1.blit(s2,[0,0],special_flags=pg.BLEND_RGB_MULT)
    l.update({"rect":pg.Rect(gpos[0]-R,gpos[1]-R,2*R,2*R)})
    l.update({"img":s1})
  def draw(self,surf,pos,mode,mask=None):
    #draw(surf,pos,self.lines,self.objects)
    if mode:
      easy(surf,pos,self.objects,self.lightsarray,mode,mask)

def calclights(lightarray,objs):
  for l in lightarray:
    gpos=l["gpos"]
    l.update({"pos":[gpos[0],1-gpos[1]]})
    fcolor=findcolor(l["color"])
    energy=l["energy"]/2
    l.update({"fcolor":[min(fcolor[i]*energy,255) for i in [0,1,2]]})
    power=l["radius"]/100*64
    s1=pg.Surface([power*200]*2)
    s1.fill([0,0,0])
    for i in range(100):
      pg.draw.circle(s1,[int(lerp(0,l["fcolor"][e],i/100)) for e in range(3)],
                     [power*100,power*100],power*(100-i))
    s2=pg.Surface([power*200]*2)
    s2.fill([255,255,255])
    draw(s2,[l["pos"][0]*size+1,l["pos"][1]*size],objs,simple=True)
    s1.blit(s2,[0,0],special_flags=pg.BLEND_RGB_MULT)
    l.update({"img":s1})

def easy(screen,pos,objs,lights,mode,mask=None):
  sx,sy=pos
  WIDTH,HEIGHT=screen.size
  wallsurf=pg.Surface([WIDTH,HEIGHT],pg.SRCALPHA)
  wallsurf.fill([0,0,0,0])
  wallsurf3=pg.Surface([WIDTH,HEIGHT])
  wallsurf3.fill([255,255,255])
  #wallsurf2.set_colorkey([0,0,0])
  for obj in objs:
    pos=[WIDTH/2+obj[0]*size-sx,HEIGHT/2+obj[1]*size-sy,size,size]
    if pos[0]+size<0 or pos[1]+size<0:continue
    if pos[0]>WIDTH or pos[1]>HEIGHT:continue
    pg.draw.rect(wallsurf,[255,255,255,255],pos)
    pg.draw.rect(wallsurf3,[0,0,0],pos)
  s3=pg.Surface([WIDTH,HEIGHT])
  s3.fill([5,5,5])
  lightimgs=[]
  for l in lights:
    power=l["radius"]*64
    pos=[WIDTH/2-sx-power+l["pos"][0]*size,HEIGHT/2-sy-power+l["pos"][1]*size]
    if pos[0]+2*power<0 or pos[1]+2*power<0:continue
    if pos[0]>WIDTH or pos[1]>HEIGHT:continue
    lightimgs.append((l["img"],pos))
  s3.fblits(lightimgs,pg.BLEND_RGB_ADD)
  #wallsurf.convert_alpha()
  if mode==2:
    draw(s3,[sx,sy],objs,simple=True)
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
    draw(s3,[sx,sy],objs)
  screen.blit(s3,[0,0],special_flags=pg.BLEND_MULT)
  #for l in lights:
  #  pg.draw.circle(screen,[255,0,0],[WIDTH/2-sx+l["pos"][0]*size,HEIGHT/2-sy+l["pos"][1]*size],5)
  return screen


if __name__=="__main__":
  # Инициализация Pygame
  pg.init()

  # Размеры окна
  WIDTH=640
  HEIGHT=480
  screen=pg.display.set_mode((WIDTH,HEIGHT),pg.RESIZABLE)
  sx,sy=288,96


  grid=[
    [1,1,1,1,1,1,1,0,0,0,0,0],
    [1,0,0,0,0,0,0,0,0,0,0,0],
    [1,0,1,1,1,1,0,0,0,0,1,0],
    [1,0,1,0,0,1,0,0,0,1,1,1],
    [1,0,1,0,0,1,0,0,0,0,1,0],
    [1,0,1,0,0,1,0,0,0,0,0,0],
    [1,0,0,0,0,0,0,0,0,0,0,0],
    [1,1,1,1,1,1,1,0,0,0,0,0],
  ]
  objarray=[
  [0, 0], [1, 0], [2, 0], [3, 0], [4, 0], [5, 0], [6, 0],
  [0, 1], [0, 2], [2, 2], [3, 2], [4, 2], [5, 2], [10, 2],
  [0, 3], [2, 3], [5, 3], [9, 3], [10, 3], [11, 3], [0, 4],
  [2, 4], [5, 4], [10, 4], [0, 5], [2, 5], [5, 5], [0, 6],
  [0, 7], [1, 7], [2, 7], [3, 7], [4, 7], [5, 7], [6.5, 7]
  ]
  lightarray=[{"gpos":[4,-4.1],"color":[255,220,160],"energy":1,"radius":5},
              {"gpos":[8,-4.1],"color":[255,0,0],"energy":1,"radius":5},
              {"gpos":[4.5,-0.5],"color":[0,255,0],"energy":1,"radius":5},
              {"gpos":[1.5,-3],"color":[0,0,255],"energy":1,"radius":5}]




  speed=10
  lit_color=[255,220,160]
  unlit_color=[10,20,30]
  unlit_color=[0,0,0]

  calclights(lightarray,objarray)

  # Цикл игры
  while True:
    for event in pg.event.get():
      if event.type == pg.QUIT:
        pg.quit()
        1/0
      if event.type==pg.VIDEORESIZE:
        WIDTH,HEIGHT=event.w,event.h
        pg.display.set_mode([WIDTH,HEIGHT],pg.RESIZABLE)
    key=pg.key.get_pressed()
    if key:
      if key[pg.key.key_code("w")]: sy-=speed
      if key[pg.key.key_code("a")]: sx-=speed
      if key[pg.key.key_code("s")]: sy+=speed
      if key[pg.key.key_code("d")]: sx+=speed
    screen.fill((255,255,255))
    #lightarray[4].update({"pos":[sx/size,sy/size]})
    #for y in range(len(grid)):
    #  for x in range(len(grid[0])):
    #    if grid[y][x]:
    #      pg.draw.rect(screen,[150,150,150],[WIDTH/2+x*size-sx,HEIGHT/2+y*size-sy,size,size])

    easy(screen,[sx,sy],objarray,lightarray)
    pg.draw.circle(screen,[255,0,0],[WIDTH/2,HEIGHT/2],5)

    # Обновление экрана
    pg.display.flip()
    pg.time.Clock().tick(60)