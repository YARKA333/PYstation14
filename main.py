import threading

import pygame as pg
import Utils.shared as shared
from Utils.multidict import Multidict
from Utils.fileutils import joinpath
from threading import Thread as Thread_old
import sys
import signal

sharedgrid=Multidict()
shared.set("globalgrid",sharedgrid)
shared.set("started",False)

ss14_folder="C:/Servers/SS14 c2/Resources/"
shared.set("resources",ss14_folder)

pg.init()
clock=pg.time.Clock()
font=pg.font.Font()
WIDTH,HEIGHT=960,540
screen=pg.display.set_mode([WIDTH,HEIGHT],pg.RESIZABLE)
pg.display.set_caption("PyStation 14")
pg.display.set_icon(pg.image.load(joinpath(ss14_folder,"Textures/Logo/icon/icon-256x256.png")))
alive=True

# region Loading Screen
import ctypes
class Thread(Thread_old):
  def stop(self):
    ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(self.ident), ctypes.py_object(SystemExit))
  def ensure_stop(self):
    if self.is_alive():self.stop()

def sigint_handler(sig,frame):
  print("Thread 1 exit")
  sys.exit(0)
signal.signal(signal.SIGINT,sigint_handler)

class Loading:
  class LoaderStack:
    def __init__(self,length=0,default_desc="..."):
      self.length=length
      self.index=0
      self.desc=default_desc
      self.d_desc=default_desc
      self.dirty=True
      self.ended=False
    def __call__(self,desc=None):
      self.dirty=True
      if desc is not None:
        self.desc=desc
      else:
        self.desc=self.d_desc
      self.index+=1
    def exit(self):
      self.dirty=True
      self.ended=True
  class LoaderIterator:
    def __init__(self,iterable):
      self.index=0
      self.iterator=iter(iterable)
      try:
        self.length=len(iterable)
      except AttributeError:
        self.length=0
      self.dirty=True
      self.ended=False
    def __next__(self):
      self.dirty=True
      try:
        self.index+=1
        return next(self.iterator)
      except StopIteration:
        self.ended=True
        raise
    def __iter__(self):
      return self

  def __init__(self):
    self.stack:list[Loading.LoaderStack|Loading.LoaderIterator]=[]
    self.loading=True

  def run(self):
    global alive

    bar_h=50
    bar_ofs=10+bar_h
    bar_w=500
    lfont=pg.Font(size=40)

    w_ofs=(screen.width-bar_w)/2

    while alive and self.loading:
      screen.fill([100,0,0])
      if any(a.dirty for a in self.stack):
        screen.fill([0,0,0])
        offset=0
        for load in self.stack:
          if load.ended:
            self.stack.remove(load)
            continue
          pg.draw.rect(screen,[50,50,50],[w_ofs,offset,bar_w,bar_h])
          if load.length:
            w=load.index/load.length*bar_w
            pg.draw.rect(screen,[100,200,100],[w_ofs,offset,w,bar_h])
          else:
            w=(time.time()%2-1)*bar_w
            if w>0:
              pg.draw.rect(screen,[100,200,100],[w_ofs,offset,w,bar_h])
            else:
              pg.draw.rect(screen,[100,200,100],[w_ofs+bar_w+w,offset,-w,bar_h])

            if load.desc:
              text=lfont.render(load.desc,True,[255,255,255])
              screen.blit(text,[(bar_w-text.width)/2+w_ofs,(bar_h-text.height)/2+offset])


          offset+=bar_ofs
        pg.display.update()
      clock.tick(60)
      for event in pg.event.get():  #event handler
        if event.type==pg.QUIT:
          alive=False

  def exit(self):
    self.loading=False

  def load(self,length=0):
    ldr=self.LoaderStack(length)
    self.stack.append(ldr)
    return ldr
  def iter(self,iterable):
    ldr=self.LoaderIterator(iterable)
    self.stack.append(ldr)
    return ldr



# endregion


import Modules.entityModule as entityModule
from Modules.rsi import *
from Modules.component import load_components
load_components()
import Modules.UInput as UInput
from Components.PointLight import FOV
import Components.Sprite as Render

lmode=0
fov=FOV()
speed=0.2

disp=pg.Surface((WIDTH/2,HEIGHT/2),pg.SRCALPHA)
smap=pg.mask.Mask((WIDTH/2,HEIGHT/2))


shared.set("nodevis",False)
shared.set("dirvis",False)

def load_game(loading):
  try:
    ldg=loading.load()
    ldg("initializing")
    from Modules.map import Grid
    from Modules.parallax import Parallax
    from Modules.Locale import load as load_locale
    ldg("loading localization")
    load_locale(loading)


    load_protos(loading,ldg)

    ldg("preloading RSI")
    preload_rsi(loading)

    ldg("loading map...")
    map_inst=Grid("Reach")
    shared.set("layerMap",map_inst)
    map_file=map_inst.raw

    ldg("loading entities...")
    # region Entities
    class wdict(dict):
      def add(self,name,value):
        if name not in self:
          self[name]=[]
        self[name].append(value)

      def display(self):
        summ=sum([sum(a) for a in self.values()])*1000
        for name,times in self.items():
          total=sum(times)*1000 #all loadings of that type summed
          count=len(times)      #how many timews this type loaded
          tmax=max(times)*1000  #max time single load took
          tmean=total/count     #mean loading time
          pot=total/summ        #part taken from overall loading
          print(f"{count} {name} with T={total:.0f}ms,M={tmax:.0f}ms,S={tmean:.0f}ms taking {pot:.1%}")

    entities=[]
    uids=[]
    shared.set("entities",entities)
    shared.set("uids",uids)
    watches=wdict()

    for entitype in tqdm(loading.iter(map_file["entities"]),desc="loading entities"):
      if entitype["proto"]=="":continue
      for entity in entitype["entities"]:
        entities.append(entityModule.Entity(entity["uid"],entitype["proto"],entity["components"],watches=watches))
        uids.append(entity["uid"])
        if len(entities)!=len(uids):raise Exception(f"uids:{len(uids)} ents:{len(entities)}")
    watches.display()
    # endregion
    ldg("starting entities")

    events.call("pingpos",bar="Pinging")
    events.call("start")

    # region Parallax
    ldg("creating parallax")
    try:
      parallax_id=map_inst.mapcomps["Parallax"]["parallax"]
    except:
      parallax_id="Default"

    shared.set("parallax",Parallax(parallax_id,loading))
    print("set!")
    # endregion

    ldg("baking chunks")
    Render.bake_chunks(map_inst)
    loading.exit()
    print("gut")
  except Exception as e:
    loading.exit()
    raise e


loading=Loading()
t=Thread(target=load_game,args=(loading,))
t.start()
loading.run()
t.ensure_stop()

sx=sy=px=py=0

parallax=shared.get("parallax")
shared.set("started",True)
print("cycle startred")

def run():
  global sx,sy,WIDTH,HEIGHT,px,py,disp,lmode,smap,alive

  while alive:
    hover:entityModule.Entity=2
    for ret in events.call("frame",{"dpos":[px,py],"gpos":[sx,sy]},noreturn=False):
      if not isinstance(ret,dict):continue
      if not "hover" in ret:continue
      hover=ret["hover"]
    assert hover!=2

    disp.fill([0,0,0,0])
    smap.fill()
    parallax.draw(screen,sx*256,sy*256)

    screenRect=pg.Rect((sx*64-WIDTH/2)/2,(sy*64-HEIGHT/2)/2,WIDTH/2,HEIGHT/2)

    Render.render(disp,smap,[sx,sy],screenRect)

    screen.blit(pg.transform.scale_by(disp,2),(0,0))
    fov.render(screen,[px*2,-py*2],mode=lmode,mask=smap.scale((WIDTH,HEIGHT)))
    screenRect=pg.Rect(sx*64-WIDTH,sy*64-HEIGHT,WIDTH,HEIGHT)
    events.rcall("overlay",{
      "surf":screen,
      "dpos":[px,py],
      "gpos":[sx,sy],
      "screenRect":screenRect,
      "delta":1/pg.math.clamp(clock.get_fps(),1,75),
      "hover":hover
    })
    name="None"
    mpos=pg.mouse.get_pos()
    screen.blit(font.render(str(hover),True,[255,0,0]),[10,10])
    screen.blit(font.render(f"{sx+(mpos[0]-WIDTH/2)/64:.1f},{sy-(mpos[1]-HEIGHT/2)/64:.1f}",True,[255,0,0]),[10,20])
    screen.blit(font.render(f"{clock.get_fps():.0f}",True,[255,0,0]),[10,0])
      #frame end
    pg.display.update()
    clock.tick(60)  #fps limiter
    for event in pg.event.get():  #event handler
      if event.type==pg.QUIT:
        alive=False
      elif event.type==pg.VIDEORESIZE:
        WIDTH,HEIGHT=event.w,event.h
        disp=pg.Surface((WIDTH/2,HEIGHT/2),pg.SRCALPHA)
        smap=pg.mask.Mask((WIDTH/2,HEIGHT/2))
        pg.display.set_mode([WIDTH,HEIGHT],pg.RESIZABLE)
        events.call("resize",{"real":[WIDTH,HEIGHT],"render":[WIDTH/2,HEIGHT/2]})
      elif event.type==pg.KEYDOWN:
        match event.key:
          case pg.K_l:
            lmode=(lmode+1)%5
          case pg.K_k:
            events.call("spawn_ball",{"gpos":[sx,sy],"dpos":[px,py]})
          case pg.K_F5:
            UInput.spawn.start()
          case pg.K_g:
            events.call("mousegrib",{"hover":hover})
          case pg.K_c:
            events.call("toggle collision debug")
          case pg.K_i:
            shared.set("thechosenlamp",hover.uid)
          case pg.K_n:
            shared.set("nodevis",not shared.get("nodevis"))
          case pg.K_u:
            shared.set("dirvis",not shared.get("dirvis"))
          case pg.K_r:
            sprite:Render.Sprite=hover.comp("Sprite")
            sprite.update(True)
      if event.type==pg.KEYUP:
        if event.key==pg.K_g:
          events.call("mouseungrib")
      elif event.type==pg.MOUSEWHEEL:
        events.call("scroll",{"delta":event.y})
    key=pg.key.get_pressed()
    if key:
      if key[pg.key.key_code("w")]: sy+=speed
      if key[pg.key.key_code("a")]: sx-=speed
      if key[pg.key.key_code("s")]: sy-=speed
      if key[pg.key.key_code("d")]: sx+=speed
    px=int(sx*32)
    py=int(sy*32)
  pg.quit()
#cProfile.run("run()","test.prof")
run()
