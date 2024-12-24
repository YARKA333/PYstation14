import os
import sys
import pygame as pg
import random
import math
import pickle
from tqdm import tqdm
import Utils.events as events
import Utils.parents as parents
import Utils.shared as shared
from Utils.multidict import Multidict

sharedgrid=Multidict()
shared.set("globalgrid",sharedgrid)

ss14_folder="C:/Servers/SS14 c2/Resources/"
shared.set("resources",ss14_folder)

pg.init()

import Modules.entityModule as entityModule
import Modules.map as map
from Modules.rsi import *
from Modules.parallax import Parallax
from Modules.entityModule import Entity
import Modules.UInput as UInput
from Components.OccluderComponent import FOV
#import cProfile


def optc(c,d):return math.floor((c+d/64)/16)
def optc2(c,d):return range(optc(c,-d),optc(c,d)+1)

lmode=0
fov=FOV()
clock=pg.time.Clock()
speed=0.2
pg.init()
load_protos()

WIDTH,HEIGHT=1024,512
screen=pg.display.set_mode([WIDTH,HEIGHT],pg.RESIZABLE)
pg.display.set_caption("PyStation 14")
pg.display.set_icon(pg.image.load(joinpath(ss14_folder,"Textures/Logo/icon/icon-256x256.png")))
disp=pg.Surface((WIDTH/2,HEIGHT/2))
smap=pg.mask.Mask((WIDTH/2,HEIGHT/2))


map_inst=map.Grid("Dev")
shared.set("layerMap",map_inst)

map_file=map_inst.raw

cmap,grid=map_inst.chunkMap,map_inst.chunkGrid


def topdict(input_dict:dict)->list:
  return "{"+",".join([f'{item[0]}:{item[1]}' for item in sorted(input_dict.items(),key=lambda item:item[1],reverse=True)])+"}"



entities=[]
uids=[]
shared.set("entities",entities)
shared.set("uids",uids)
for entitype in tqdm(map_file["entities"],desc="loading entities"):
  if entitype["proto"]=="":continue
  for entity in entitype["entities"]:
    entities.append(Entity(entity["uid"],entitype["proto"],entity["components"]))
    uids.append(entity["uid"])
    if len(entities)!=len(uids):raise BaseException(f"uids:{len(uids)} ents:{len(entites)}")
#print("pinging...")
events.call("pingpos",bar="Pinging")
events.call("start")
print(topdict(entityModule.wanted_comps))

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
  "WhinPipe",
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
font=pg.font.Font()
print("cycle startred")
def run():
  global sx,sy,WIDTH,HEIGHT,px,py,disp,lmode,smap
  while 1:
    hover="Erro"
    for ret in events.call("frame",{"dpos":[px,py],"gpos":[sx,sy]},noreturn=False):
      if type(ret)!=dict:continue
      if not "hover" in ret.keys():continue
      hover=ret["hover"]
    #disp.fill([0,0,0,0])
    smap.fill()
    parallax.draw(disp,px,py)
    xr,yr=optc2(sx,WIDTH),optc2(sy,HEIGHT)
    for depth in drawdepths:
      for y in yr:
        for x in xr:
          cpos=[x,y]
          if depth=="Dno":
            if cpos in cmap:
              dpos=[512*x-px+WIDTH//4,-480-512*y+py+HEIGHT//4]
              ind=cmap.index(cpos)
              disp.blit(chunks[ind],dpos)
              smap.erase(chunkmasks[ind],dpos)
          else:
            events.call(f"render:{depth}:{cpos}",{"dst":disp,"smap":smap,"pos":[px,py],"depth":depth})
    screen.blit(pg.transform.scale_by(disp,2),(0,0))
    fov.draw(screen,[px*2,-py*2],mode=lmode,mask=smap.scale((WIDTH,HEIGHT)))
    screen.blit(font.render(str(hover),True,[255,0,0]),[10,10])
    name="None"
    events.call("overlay",{"surf":screen,"dpos":[px,py],"gpos":[sx,sy]})
    if hover in uids:
      comp=entityModule.getEcomp(hover,"MetaData")
      if comp:
        name=comp.name
    screen.blit(font.render(name,True,[255,0,0]),[10,20])
    pg.display.flip()
    clock.tick(60)  #fps limiter
    for event in pg.event.get():  #event handler
      if event.type==pg.QUIT:
        pg.quit()
        quit(1488)
      if event.type==pg.VIDEORESIZE:
        WIDTH,HEIGHT=event.w,event.h
        disp=pg.Surface((WIDTH/2,HEIGHT/2))
        smap=pg.mask.Mask((WIDTH/2,HEIGHT/2))
        pg.display.set_mode([WIDTH,HEIGHT],pg.RESIZABLE)
        events.call("resize",{"real":[WIDTH,HEIGHT],"render":[WIDTH/2,HEIGHT/2]})
      if event.type==pg.KEYDOWN:
        if event.key==pg.K_l:
          lmode=(lmode+1)%4
        elif event.key==pg.K_k:
          events.call("spawn_ball",{"gpos":[sx,sy],"dpos":[px,py]})
        elif event.key==pg.K_F5:
          UInput.spawn.start()
        elif event.key==pg.K_g:
          events.call("mousegrib")
        elif event.key==pg.K_c:
          events.call("toggle collision debug")
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
#cProfile.run("run()","test.prof")
run()