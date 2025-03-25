import Components.Transform
from Modules.rsi import *
import Modules.UInput as mouse
from Utils.vector2 import Vector
from Components.InteractionOutline import outline
from Modules.component import BaseComponent,component
from Utils.colors import colors,findcolor
import time
from Utils.watch import catch
import Utils.events as events
from Modules.Decal import Decal
from Modules.map import decode,Grid
from Utils.mathutils import sin,cos

#allsprites={}
#allshades={}
#allshadebools={}
readysprites={}
readystates={}
mode="anim"

resolution=32

def addshade(dst:pg.Mask,src:pg.Surface,pos:Vector=Vector(),erase:bool=False):
  #mask=pg.mask.from_surface(src)
  pos=pos.pos
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

dirbias=0.05
def getdir(angle):
  mod = (math.floor(angle / 90) % 2) - 0.5
  modTheta = angle + mod * dirbias
  return round(modTheta / 90)%4

def getdir8(angle):
  return (angle+45/2)//45

def composename(*args):
  return ":".join([str(a) for a in args])
import random
class Layer:
  parent:"Sprite"
  _state:str=None
  _visible:bool=True
  _sprite:str=None
  map:list[str]=[]
  scale:Vector=Vector.ONE
  offset:Vector=Vector.ZERO
  diroff:int=0
  rotation:float=0
  shader=None
  _color:tuple[int,int,int,int]=(255,255,255,255)

  image:pg.Surface
  rect:pg.Rect
  RSI:RSI=None

  #inert:bool=False
  ready=False
  directinal:bool


  def __init__(self,parent:"Sprite",args:dict):
    self.initing=True
    self.parent=parent
    self.RSI=parent.rsi
    if isinstance(args,dict):
      for k,v in args.items():
        setattr(self,k,v)
    elif isinstance(args,str):
      self.state=args
    else:raise ValueError(f"state {args} on {self.parent.sprite} in proto {self.parent.entity.meta.proto}")

    #type check
    self.scale=Vector(self.scale)
    self.offset=-Vector(self.offset)
    #init
    self.last_name="not inited"
    if not self.state:
      print("NOSTATE")
      #if random.random()<0.1:
      #  self.rsi=loadrsi("Textures/deprecated.rsi")
      self._state="NOSTATE"
    self.checkInert()
    match self.shader:
      case None:
        self.shaded=False
      case "unshaded":
        self.shaded=True
      case _:
        print(f"entity {self.parent.uid} has layer with unknown shader {self.shader}")
        self.shaded=None
    self.initing=False

  def checkInert(self):
    pass
  #  print(f"found {self.RSI.getstateframes(self.state)} frames")
  #  self.inert=self.RSI.getstateframes(self.state)<=1
  @property
  def inert(self):
    return self.RSI.getstateframes(self.state)<=1
  @property
  def needs_upd(self):
    return not (self.inert and self.ready)
  #@property
  #def RSI(self):
  #  return self.rsi or self.parent.rsi
  @property
  def color(self):return self._color
  @color.setter
  def color(self,value):
    print(findcolor(value))
    self._color=findcolor(value)
  @property
  def sprite(self):return self._sprite
  @sprite.setter
  def sprite(self,value):
    self._sprite=value
    self.RSI=loadrsi(self.sprite) if self.sprite else self.parent.rsi
  @property
  def state(self):
    return self._state

  @property
  def visible(self):
    return self._visible
  @visible.setter
  def visible(self,value):
    self._visible=bool(value)
    self.parent.ready=False
  @state.setter
  def state(self,value):
    if value!=self._state:
      if value in self.RSI.states or self.initing or self.RSI.path=="Textures/deprecated.rsi":
        self._state=value
        self.parent.time=time.time()
        self.ready=False
        #print(f"sprite state set to {value}")
      else:
        print(f"{self.parent.uid} tried to set state to {value} but {self.RSI.path} dont have one")

  @property
  def directional(self):
    if not self.state:
      return False
    return 1!=self.RSI.getdirs(self.state)

  def __repr__(self):
    #data=[f"  {k}:{repr(v) if not isinstance(v,BaseComponent) else str(v)}\n" for k,v in self.__dict__.items()]
    #return "\n"+"".join(data)
    return self.last_name


  def update(self,force=False):
    self.ready=False
    if not self.visible and not force:
      return
    if self.shaded is None:return
    if self.state=="NOSTATE":return
    self.ready=True

    rsi=self.RSI

    #calculate rotation
    dirs=rsi.getdirs(self.state)

      #TODO КОСТЫЛЬ
    wall=self.parent.entity.hascomp("IconSmooth")
    dir=(self.parent.dir*(not wall)+self.diroff)%4

    angle=self.rotation+self.parent.rot*(not self.parent.noRot)
    match dirs:
      case 1:
        dir=0
      case 4|8:
        dir=[0,2,1,3][dir]
        #angle+=(self.rotation+45)%90-45
      case _:raise
    color=[a*b/255 for a,b in zip(self.color,self.parent.color)]

    #find name of image
    frame=rsi.getframe(state=self.state,dir=dir,otime=self.parent.time)
    name=composename(self.RSI.path,self.state,frame,color,self.scale,angle,dir)
    #if self.parent.uid==39:
    #  print(name)

    if name==self.last_name:return

    self.image=readystates.get(name)  #get cached image
    if not self.image:  #generate new
      self.image=rsi(state=self.state,dir=dir,frame=frame)
      if color!=(255,255,255,255):
        self.image.fill(color[0:3],special_flags=pg.BLEND_RGB_MULT)
      scale=self.RSI.size*self.scale*resolution/32
      if scale!=Vector.ONE:
        self.image=pg.transform.scale(self.image,scale)
      if angle:
        self.image=pg.transform.rotate(self.image,angle)
      readystates[name]=self.image
    self.rect=pg.Rect(self.offset*resolution-Vector(self.image.size)/2,self.image.size)
    self.last_name=name

class rdict(dict):
  def __repr__(self):
    return "{\n"+"\n".join(f"  {repr(k)}:{repr(v)}" for k,v in self.items())+"\n}"

class rlist(list):
  def __repr__(self):
    return "[\n"+"\n".join(f"  {repr(e)}" for e in self)+"\n]"

@component
class Sprite(BaseComponent):
  after=["Transform","MetaData"]
  rot=0
  pos=Vector()
  visible=True
  time=0
  offset=Vector()

  dir=0
  ready=False

  def __init__(self,entity,comp):
    from Utils.colors import hsv
    self.debug_color=hsv(random.randint(0,359),1,1)

    self.scale=Vector(comp.get("scale",[1,1]))
    self.entity=entity
    self.depth=comp.get("drawdepth","Objects")
    self.uid=entity.uid
    self.noRot=comp.get("noRot",False)
    self.snapCardinals=comp.get("snapCardinals",False)
    self.sprite=comp.get("sprite")
    self.pos=entity.xform.pos
    self.offset=Vector(comp.get("offset")) #None is 0,0
    self.renderevent=None
    self.last_name="100% real sprite name"
    #self.edges=[0,0,0,0]
    if not self.sprite:
      self.sprite="deprecated.rsi"
    self.layerMap:rdict[str,Layer]=rdict()
    self.color=colors.get(
      comp.get("color","White"),
      (255,255,255,255))
    events.subscribe("setvis",self.setvis,entity.uid)
    events.subscribe("updateMap",self.updateMap,entity.uid)
    events.subscribe("setDepth",self.setdepth,entity.uid)
    self.rsi=loadrsi(self.sprite)
    self.layers=rlist(Layer(self,data) for data in comp.get("layers",[]))
    if not self.layers:
      state=comp.get("state")
      if state:
        self.layers=[Layer(self,state)]
    #base_offset=Vector(comp.get("offset"))*32
    #self.offsets=[-Vector(_state.get("offset"))*32-base_offset for _state in self.layers]
    for layer in self.layers:
      for m in layer.map:
        self.layerMap|={m:layer}
    #  layer.update({"shaded":False if layer.get("shader",None)=="unshaded" else True})
    #  map=layer.get("map",[])
    #  for m in map:
    #    self.layerMap|={m:layer}
    #self.dirs=[None]*len(self.layers)
    self.cpos=Vector(100,100)
    #events.subscribe(f"render:{self.depth}:{self.cpos}",self.render)
    events.followcomp("Transform",self.Transform,entity)
    self.update(force=True)
    events.call("Sprite",self,self.uid)

  @property
  def inert(self):
    return all([layer.inert for layer in self.layers])

  @property
  def needs_upd(self):
    return not self.inert or not self.ready or not all(layer.ready for layer in self.layers)

  @property
  def directional(self):
    return any((layer.directional for layer in self.layers))
  def unready(self):
    self.ready=False
    for layer in self.layers:
      layer.ready=False

  def update(self,force=False):
    if not (self.needs_upd or force):return
    if self.directional:
      self.rot=(self.realrot+45)%90-45
    else:
      self.rot=self.realrot
    #self.rot=0
    #layer updating5
    for layer in self.layers:
      if layer.needs_upd or not self.ready:
        layer.update(self.dir)
    self.ready=True
    layers=[layer for layer in self.layers if layer.ready and layer.visible]

    defaultrot=not self.rot%90
    self.rot=0

    #size parameters
    self.rect=pg.Rect(-16,-16,32,32).unionall([layer.rect for layer in layers])
    self.center=-Vector(self.rect.topleft)
    self.size=Vector(self.rect.size)

    #naming
    name=";".join([layer.last_name for layer in layers])
    if name==self.last_name and not force:return
    self.last_name=name

    #sprite
    if defaultrot and name in readysprites: #get from cache
      self.final,self.shaded,self.unshaded=readysprites[name]
    else:

      #if not (self.directional or self.noRot):
      #  print(f"{self.entity.meta.proto} rotating")

      w,h=self.size
      hr=int(h*abs(cos(self.rot))+w*abs(sin(self.rot)))
      wr=int(h*abs(sin(self.rot))+w*abs(cos(self.rot)))
      rotsize=(max(wr,32),max(hr,32))
      self.final=pg.Surface(rotsize,pg.SRCALPHA)
      self.shaded  =pg.Mask(rotsize)
      self.unshaded=pg.Mask(rotsize)
      #if False:
      #pg.draw.circle(self.final,[255,0,0],[a/2 for a in self.final.size],min(self.final.size)/2)

      for layer in layers:
        roff=(layer.offset*resolution).rotate(self.rot)
        pos=self.center-Vector(layer.image.size)/2+roff
        image=pg.transform.rotate(layer.image,-self.rot)
        mask=pg.mask.from_surface(image,200)
        if layer.shaded:
          self.unshaded.erase(mask,roff)
          self.shaded.draw(mask,roff)
        else:
          self.shaded.erase(mask,roff)
          self.unshaded.draw(mask,roff)


        self.final.blit(image,pos)
      if defaultrot:
        readysprites[name]=(self.final,self.shaded,self.unshaded)

    centdiff=(Vector(self.rect.size)/2-self.center)
    roff=centdiff.rotate(0)-Vector(self.final.size)/2+self.offset
    self.realrect=pg.Rect(roff,self.final.size)

    if self.scale!=[1,1]:
      origsize=Vector(self.final.size)
      newsize=origsize*self.scale
      self.final=pg.transform.scale(self.final,newsize)
      diff=newsize-origsize
      self.realrect.inflate_ip(diff.pos)


    if shared.get("dirvis"):
      self.final=self.final.copy()
      def e(*args):
        return (Vector(args)*min(self.final.size)).rotate(-self.rot)/2
      b=(e(0,0),e(0,1))
      r=(e(0,1),e(0.25,0.75))
      l=(e(0,1),e(-0.25,0.75))
      for a,b, in [b,r,l]:
        pg.draw.aaline(self.final,[255,0,0],
                     Vector(self.final.size)/2+a,
                     Vector(self.final.size)/2+b)




  def Transform(self,comp:Components.Transform.Transform):
    #self.visible=comp.parent==shared.get("layerMap").uid
    self.pos=comp.pos
    cpos=self.pos//16
    if cpos!=self.cpos:
      #events.unsubscribe(f"render:{self.depth}:{self.cpos}",self.render)
      self.cpos=cpos
      #print(f"render:{self.depth}:{self.cpos}")
      self.resub()
    self.realrot=comp.rot
    if self.snapCardinals:
      self.realrot=(self.realrot+45)%90-45
    self.dir=getdir(self.realrot)
    self.unready()
  def resub(self):
    events.unsubscribe(self.renderevent)
    self.renderevent=events.subscribe(f"render:{self.depth}:{self.cpos}",self.render)
  def setvis(self,args):
    self.visible=args

  def updateMap(self,args):
    for k,v in args.items():
      layer=self.layerMap.get(k)
      if not layer:
        print(f"no requested layer {k}")
        continue
      layer.visible=v
  def __setitem__(self,name:str|int,value:Layer):
    if isinstance(name,str):
      oldlayer:Layer=self.layerMap.get(name)
      if oldlayer:
        idx=self.layers.index(oldlayer)
        maps=oldlayer.map
        self.layers[idx]=value
        for mapid in maps:
          self.layerMap[mapid]=value
        del oldlayer
      else:
        self.layerMap[name]=value
        self.layers.append(value)
    elif isinstance(name,int):
      oldlayer=self.layers[name]
      maps=oldlayer.map
      self.layers[name]=value
      for mapid in maps:
        self.layerMap[mapid]=value
    else:raise
  def __getitem__(self, item:str|int):
    if isinstance(item,str):
      return self.layerMap[item]
    elif isinstance(item,int):
      return self.layers[item]
    else:raise
  def get(self,item:str|int,default=None):
    if isinstance(item,str):
      if item in self.layerMap:
        return self.layerMap[item]
      else:return default
    elif isinstance(item,int):
      if item<len(self.layers):
        return self.layers[item]
      else:
        return default
    else:raise

  def setdepth(self,args):
    self.depth=args.get("depth",self.depth)
    self.resub()
  @catch
  def render(self,args:dict):
    if not self.visible:return
    sx,sy,sw,sh=args["screenRect"]
    rx,ry,rw,rh=self.realrect
    rx2=rx+self.pos.x*resolution
    ry2=ry+self.pos.y*resolution
    if rx2<sx+sw and rx2+rw>sx and ry2<sy+sh and ry2+rh>sy:

      self.update(args.get("forcereload",False))

      pos: tuple=args["pos"]
      dst: pg.Surface=args["dst"]
      dst_wh: tuple=dst.get_size()
      fpos=(-pos[0]
            +dst_wh[0]/2
            +self.pos[0]*32
            +rx,
           (-pos[1]
            -dst_wh[1]/2
            +(self.pos[1])*32)*-1
            +ry)

      if mouse.lasthovered==self.entity and self.entity.hascomp("InteractionOutline"):
          mouse.active=1
          dst.blit(outline(self.final),(Vector(fpos)-[1,1]).pos)

      smap: pg.Mask=args["smap"]
      smap.draw(self.shaded,fpos)
      smap.erase(self.unshaded,fpos)
      dst.blit(self.final,fpos)
      mouse.checkMouse(self.final,fpos,self.entity)

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
chunks: list[pg.Surface]=[]
chunkmasks: list[pg.mask.Mask]=[]
decals:list[Decal]=[]
def bake_chunks(grid:"Grid"):
  """
  Initialize tiles and decals on grid
  :param grid:Grid object
  """
  global cmap,chunks,chunkmasks
  cmap,chunkGrid=grid.chunkMap,grid.chunkGrid
  map_decals=grid.gridcomps["DecalGrid"]["chunkCollection"]["nodes"]
  for decal in map_decals:
    decals.append(Decal(decal))
  surf=pg.Surface([512,512],pg.SRCALPHA)
  for c in chunkGrid:
    surf.fill([0,0,0,0])
    for x in range(16):
      for y in range(16):
        num,var=decode(c[y][x])
        tile=grid.tiledict[num]
        if tile.sprite:
          surf.blit(tile(var),[32*x,32*(15-y)])
    chunks.append(surf.copy())

  for dec in decals:
    dec.prebake(chunks,cmap)
  for c in chunks:
    chunkmasks.append(pg.mask.from_surface(c))
def optc(c,d):return math.floor((c+d/64)/16)
def optc2(c,d):return range(optc(c,-d),optc(c,d)+1)
def render(
    disp:pg.Surface,
    smap:pg.Mask,
    pos:tuple[float,float],
    screenRect:pg.Rect):
  """
  render all SpriteComponent
  :param disp: surface to render on
  :param smap: global shadowmap
  :param pos: eye position
  :param screenRect: Rect representing screen area
  :return:
  """
  sx,sy=pos
  px=int(sx*32)
  py=int(sy*32)
  w,h=disp.size
  xr,yr=optc2(sx,w),optc2(sy,h)
  for depth in drawdepths:
    for y in yr:
      for x in xr:
        cpos=Vector(x,y)
        if depth=="Dno":
          if cpos in cmap:
            dpos=[512*x-px+w//2,-512*(y+1)+py+h//2]
            ind=cmap.index(cpos)
            chunk=chunks[ind]
            disp.blit(chunk,dpos)
            smap.erase(chunkmasks[ind],dpos)
        else:
          events.rcall(f"render:{depth}:{cpos}",{"dst":disp,"smap":smap,"pos":[px,py],"screenRect":screenRect})

#events.subscribe("render",render)

def debugslicer(args):
  ent=args["hover"]
  if not ent:return
  dst=args["surf"]
  layers=ent.comp("Sprite").layers
  x=0
  y=0
  for i,layer in enumerate(layers):
    if not (layer.ready and layer.visible): continue
    img=pg.transform.scale_by(layer.image,2)
    x+=img.width
    pg.draw.rect(dst,[20,20,25],(dst.width-x,y)+img.size)
    dst.blit(img,[dst.width-x,y])
    if x+64>dst.width:
      x=0
      y+=64

events.subscribe("overlay",debugslicer)