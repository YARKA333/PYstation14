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

import Modules.entityModule as entityModule
import Modules.map as map
from Modules.rsi import *
from Modules.parallax import Parallax
from Modules.entityModule import Entity
import hashlib as sha
import cProfile


def optc(c,d):return math.floor((c+d/64)/16)
def optc2(c,d):return range(optc(c,-d),optc(c,d)+1)

clock=pg.time.Clock()
speed=0.2
pg.init()
WIDTH,HEIGHT=1024,512
disp=pg.display.set_mode([WIDTH,HEIGHT],pg.RESIZABLE)

map_file=map.loadmap("Reach")

tilemap=map_file["tilemap"]
cmap,grid=map.loadfloor(map_file)


def topdict(input_dict:dict)->list:
  return "{"+",".join([f'{item[0]}:{item[1]}' for item in sorted(input_dict.items(),key=lambda item:item[1],reverse=True)])+"}"

entities=[]
uids=[]
shared.set("entities",entities)
shared.set("uids",uids)
for entitype in tqdm(map_file["entities"],desc="loading entities"):
  if entitype["proto"]=="":continue
  basecomps=parents.parent(entitype["proto"])
  if not basecomps:
    continue
  for entity in entitype["entities"]:
    entities.append(Entity(entity["uid"],components=basecomps+entity["components"]))
    uids.append(entity["uid"])
    if len(entities)!=len(uids):raise BaseException(f"uids:{len(uids)} ents:{len(entites)}")
print("pinging...")
events.call("pingpos")
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

tiledict=dict([(a,Floor(b)) for a,b in tqdm(tilemap.items(),desc="Ordering tiles")])

map_decals=findict(map_file["entities"],
  "type","DecalGrid",5)["chunkCollection"]["nodes"]
drawdepths=[
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

#entity=Entity("AirlockEngineering")
#etexture=RSI(joinpath("Textures",entity.components[0]["sprite"]))
#scrubber=RSI("Textures/Structures/Piping/Atmospherics/scrubber.rsi/")
#suscrubber=RSI("Textures/Structures/Piping/Atmospherics/Portable/portable_scrubber.rsi/")
#vent=RSI("Textures/Structures/Piping/Atmospherics/vent.rsi/")
mapsize=[0,0,0,0]
for o in cmap:
  if o[0]<mapsize[0]:mapsize[0]=o[0]
  if o[0]>mapsize[1]:mapsize[1]=o[0]
  if o[1]<mapsize[2]:mapsize[2]=o[1]
  if o[1]>mapsize[3]:mapsize[3]=o[1]
sx=sy=px=py=0
chunks=[]
surf=pg.Surface([512,512],pg.SRCALPHA)
for c in grid:
  surf.fill([0,0,0,0])
  for x in range(16):
    for y in range(16):
      tile=tiledict[map.decode(c[y][x])]
      if tile.sprite:
        surf.blit(tile(),[32*x,32*(15-y)])
  chunks.append(surf.copy())
for dec in decals:
  dec.prebake(chunks,cmap)

print("cycle startred")
def run():
  global sx,sy,WIDTH,HEIGHT,px,py
  while 1:
    #disp.fill([0,0,0])
    parallax.draw(disp,px,py)
    xr,yr=optc2(sx,WIDTH),optc2(sy,HEIGHT)
    for y in yr:
      for x in xr:
        cpos=[x,y]
        if cpos in cmap:
          dpos=[512*x-px+WIDTH//2,-480-512*y+py+HEIGHT//2]
          disp.blit(chunks[cmap.index(cpos)],dpos)
    for depth in drawdepths:
      events.call("render",{"dst":disp,"pos":[px,py],"depth":depth})
    pg.display.flip()
    clock.tick(60)  #fps limiter
    for event in pg.event.get():  #event handler
      if event.type==pg.QUIT:
        pg.quit()
        quit(1488)
      if event.type==pg.VIDEORESIZE:
        WIDTH,HEIGHT=event.w,event.h
        pg.display.set_mode([WIDTH,HEIGHT],pg.RESIZABLE)
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