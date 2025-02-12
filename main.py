import time
from Utils.watch import watch
import pygame as pg
from tqdm import tqdm
import Utils.shared as shared
from Utils.multidict import Multidict
from Utils.vector2 import Vector

sharedgrid=Multidict()
shared.set("globalgrid",sharedgrid)
shared.set("started",False)

ss14_folder="C:/Servers/SS14 c2/Resources/"
shared.set("resources",ss14_folder)

pg.init()

import Modules.entityModule as entityModule
import Modules.map as map
from Modules.rsi import *
from Modules.parallax import Parallax
from Modules.Decal import Decal
import Modules.UInput as UInput
from Modules.component import load_components
load_components()
from yaml_tag import classdb

from Components.PointLightComponent import FOV
#import cProfile


def optc(c,d):return math.floor((c+d/64)/16)
def optc2(c,d):return range(optc(c,-d),optc(c,d)+1)
a=classdb.copy()
a[0]=None
#print("classDB",a)

lmode=0
fov=FOV()
clock=pg.time.Clock()
speed=0.2
pg.init()
load_protos()

WIDTH,HEIGHT=960,540
screen=pg.display.set_mode([WIDTH,HEIGHT],pg.RESIZABLE)
pg.display.set_caption("PyStation 14")
pg.display.set_icon(pg.image.load(joinpath(ss14_folder,"Textures/Logo/icon/icon-256x256.png")))
disp=pg.Surface((WIDTH/2,HEIGHT/2),pg.SRCALPHA)
smap=pg.mask.Mask((WIDTH/2,HEIGHT/2))
font=pg.font.Font()
preload_rsi()

shared.set("nodevis",False)
shared.set("dirvis",False)

map_inst=map.Grid("Reach")
shared.set("layerMap",map_inst)

map_file=map_inst.raw

cmap,grid=map_inst.chunkMap,map_inst.chunkGrid


def topdict(input_dict:dict)->list:
  return "{"+",".join([f'{item[0]}:{item[1]}' for item in sorted(input_dict.items(),key=lambda item:item[1],reverse=True)])+"}"



entities=[]
uids=[]
shared.set("entities",entities)
shared.set("uids",uids)
class wdict(dict):
  def add(self,name,value):
    if name not in self:
      self[name]=[]
    self[name].append(value)

  def display(self):
    summ=sum([sum(a) for a in self.values()])*1000
    for name,times in self.items():
      total=sum(times)*1000
      count=len(times)
      tmax=max(times)*1000
      tmean=total/count
      pot=total/summ
      print(f"{count} {name} with T={total:.0f}ms,M={tmax:.0f}ms,S={tmean:.0f}ms taking {pot:.1%}")

watches=wdict()
for entitype in tqdm(map_file["entities"],desc="loading entities"):
  if entitype["proto"]=="":continue
  for entity in entitype["entities"]:
    entities.append(entityModule.Entity(entity["uid"],entitype["proto"],entity["components"],watches=watches))
    uids.append(entity["uid"])
    if len(entities)!=len(uids):raise Exception(f"uids:{len(uids)} ents:{len(entities)}")
watches.display()
#print("pinging...")
events.call("pingpos",bar="Pinging")


#print("ну стартовало же")
events.call("start")

#cProfile.run("start()","text.prof")
#print(topdict(entityModule.wanted_comps))

try:
  parallax_id=findict(map_file["entities"],
  "type","Parallax",
  5)["parallax"]
except:
  parallax_id="Default"
parallax=Parallax(parallax_id)
decals=[]



map_decals=map_inst.comps["DecalGrid"]["chunkCollection"]["nodes"]
drawdepths=[
  "Dno",
  "LowFloors",
  "ThickPipe",
  "ThickWire",
  "ThinPipe",
  "ThinWire",
  "BelowFloor",
  "FloorTiles",
  "FloorObjects",
  "DeadMobs",
  "SmallMobs",
  "Walls",
  "WallTops",
  "Objects",
  "SmallObjects",
  "WallMountedItems",
  "Items",
  "Mobs",
  "OverMobs",
  "Doors",
  "BlastDoors",
  "OverDoors",
  "Effects",
  "Ghosts",
  "Overlays"]

for decal in map_decals:
  decals.append(Decal(decal))

mapsize=[0,0,0,0]
for o in cmap:
  if o[0]<mapsize[0]:mapsize[0]=o[0]
  if o[0]>mapsize[1]:mapsize[1]=o[0]
  if o[1]<mapsize[2]:mapsize[2]=o[1]
  if o[1]>mapsize[3]:mapsize[3]=o[1]
sx=sy=px=py=0
chunks=[]
chunkmasks:list[pg.mask.Mask]=[]
surf=pg.Surface([512,512],pg.SRCALPHA)
for c in grid:
  surf.fill([0,0,0,0])
  for x in range(16):
    for y in range(16):
      num,var=map.decode(c[y][x])
      tile=map_inst.tiledict[num]
      if tile.sprite:
        surf.blit(tile(var),[32*x,32*(15-y)])
  chunks.append(surf.copy())

for dec in decals:
  dec.prebake(chunks,cmap)
for c in chunks:
  chunkmasks.append(pg.mask.from_surface(c))

shared.set("started",True)
print("cycle startred")
def run():
  global sx,sy,WIDTH,HEIGHT,px,py,disp,lmode,smap
  while 1:
    #w=watch()
    hover="Erro"
    for ret in events.call("frame",{"dpos":[px,py],"gpos":[sx,sy]},noreturn=False):
      if type(ret)!=dict:continue
      if not "hover" in ret.keys():continue
      hover=ret["hover"]
      #render
    disp.fill([0,0,0,0])
    smap.fill()
    parallax.draw(screen,sx*256,sy*256)
    xr,yr=optc2(sx,WIDTH),optc2(sy,HEIGHT)
    screenRect=pg.Rect((sx*64-WIDTH/2)/2,(sy*64-HEIGHT/2)/2,WIDTH/2,HEIGHT/2)
    #w("other")
    #rw=watch()
    #cw=watch()
    for depth in drawdepths:
      for y in yr:
        for x in xr:
          cpos=Vector(x,y)
          if depth=="Dno":
            if cpos in cmap:
              dpos=[512*x-px+WIDTH//4,-512*(y+1)+py+HEIGHT//4]
              ind=cmap.index(cpos)
              chunk=chunks[ind]
              disp.blit(chunk,dpos)
              smap.erase(chunkmasks[ind],dpos)
          else:
            events.rcall(f"render:{depth}:{cpos}",{"dst":disp,"smap":smap,"pos":[px,py],"depth":depth,"screenRect":screenRect}) #,"rw":rw,"cw":cw
    #rw.flush()
    #cw.flush()
    #w("draw")
    screen.blit(pg.transform.scale_by(disp,2),(0,0))
    #w("resize")
    fov.render(screen,[px*2,-py*2],mode=lmode,mask=smap.scale((WIDTH,HEIGHT)))
    #w("shader")
    #nw=watch()
    screenRect=pg.Rect(sx*64-WIDTH,sy*64-HEIGHT,WIDTH,HEIGHT)
    events.rcall("overlay",{"surf":screen,"dpos":[px,py],"gpos":[sx,sy],"screenRect":screenRect,"delta":1/pg.math.clamp(clock.get_fps(),1,75)})#,"nw":nw
    #nw.flush()
    #w("overlay")
    name="None"
    if hover in uids:
      comp=entityModule.getEcomp(hover,"MetaData")
      if comp:
        name=comp.name
    screen.blit(font.render(name,True,[255,0,0]),[10,20])
    mpos=pg.mouse.get_pos()
    screen.blit(font.render(str(hover),True,[255,0,0]),[10,10])
    screen.blit(font.render(f"{sx+(mpos[0]-WIDTH/2)/64:.1f},{sy-(mpos[1]-HEIGHT/2)/64:.1f}",True,[255,0,0]),[10,30])
    screen.blit(font.render(f"{clock.get_fps():.0f}",True,[255,0,0]),[10,0])
      #frame end
    pg.display.update()
    clock.tick(60)  #fps limiter
    for event in pg.event.get():  #event handler
      if event.type==pg.QUIT:
        pg.quit()
        quit()
      if event.type==pg.VIDEORESIZE:
        WIDTH,HEIGHT=event.w,event.h
        disp=pg.Surface((WIDTH/2,HEIGHT/2),pg.SRCALPHA)
        smap=pg.mask.Mask((WIDTH/2,HEIGHT/2))
        pg.display.set_mode([WIDTH,HEIGHT],pg.RESIZABLE)
        events.call("resize",{"real":[WIDTH,HEIGHT],"render":[WIDTH/2,HEIGHT/2]})
      if event.type==pg.KEYDOWN:
        match event.key:
          case pg.K_l:
            lmode=(lmode+1)%5
          case pg.K_k:
            events.call("spawn_ball",{"gpos":[sx,sy],"dpos":[px,py]})
          case pg.K_F5:
            UInput.spawn.start()
          case pg.K_g:
            events.call("mousegrib")
          case pg.K_c:
            events.call("toggle collision debug")
          case pg.K_i:
            shared.set("thechosenlamp",hover)
          case pg.K_n:
            shared.set("nodevis",not shared.get("nodevis"))
          case pg.K_u:
            shared.set("dirvis",not shared.get("dirvis"))
          case pg.K_r:
            sprite=entityModule.getEcomp(hover,"Sprite")
            sprite.update(True)
      if event.type==pg.KEYUP:
        if event.key==pg.K_g:
          events.call("mouseungrib")
      if event.type==pg.MOUSEWHEEL:
        events.call("scroll",{"delta":event.y})
    key=pg.key.get_pressed()
    if key:
      if key[pg.key.key_code("w")]: sy+=speed
      if key[pg.key.key_code("a")]: sx-=speed
      if key[pg.key.key_code("s")]: sy-=speed
      if key[pg.key.key_code("d")]: sx+=speed
    px=int(sx*32)
    py=int(sy*32)
    #w("other")
    #w.flush()
#cProfile.run("run()","test.prof")
run()