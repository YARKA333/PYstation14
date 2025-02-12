import Components.TransformComponent
from Modules.rsi import *
import Modules.UInput as mouse
from Utils.vector2 import Vector
from Components.InteractionOutlineComponent import outline
from Modules.component import BaseComponent,component
from Utils.colors import colors
import time
from Utils.watch import catch

#allsprites={}
#allshades={}
#allshadebools={}
readysprites={}
readystates={}
mode="anim"

resolution=32

def addshade(dst:pg.mask,src:pg.Surface,pos:Vector=Vector(),erase:bool=False):
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

class Layer:
  parent:"Sprite"
  _state:str=None
  _visible:bool=True
  sprite:str=None
  map:list[str]=[]
  scale:Vector=Vector.ONE
  offset:Vector=Vector.ZERO
  diroff:int=0
  rotation:float=0
  shader=None
  color:tuple[int,int,int,int]="White"

  image:pg.Surface
  rect:pg.Rect
  rsi:RSI=None

  #inert:bool=False
  ready=False
  directinal:bool


  def __init__(self,parent:"Sprite",args:dict):
    self.initing=True
    self.parent=parent
    if isinstance(args,dict):
      for k,v in args.items():
        setattr(self,k,v)
    elif isinstance(args,str):
      self.state=args
    else:raise ValueError(f"state {args} on {self.parent.sprite} in proto {self.parent.entity.meta.proto}")

    #type check
    self.scale=Vector(self.scale)
    self.offset=Vector(self.offset)
    if isinstance(self.color,str):
      self.color=colors.get(self.color,[255,0,255,255])
    #init
    self.rsi=loadrsi(self.sprite) if self.sprite else None
    self.last_name=""
    if not self.state:
      print("NOSTATE")
      self.rsi=loadrsi("Textures/deprecated.rsi")
      self._state="it doesnt matter now"
    self.checkInert()
    match self.shader:
      case None:
        self.shaded=False
      case "unshaded":
        self.shaded=True
      case _:
        print(f"entity {self.parent.uid} has layer with unknown shader {self.shader}")
        self.shaded=False
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
  @property
  def RSI(self):
    return self.rsi or self.parent.rsi

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
      if value in self.RSI.states or self.initing:
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
    data=[f"  {k}:{repr(v) if not isinstance(v,BaseComponent) else str(v)}\n" for k,v in self.__dict__.items()]
    return "\n"+"".join(data)


  def update(self,force=False):
    self.ready=False
    if not self.visible and not force:
      return
    if not self.state:
      print("nostate")
      return
    self.ready=True

    rsi=self.RSI

    #calculate rotation
    dirs=rsi.getdirs(self.state)

      #TODO КОСТЫЛЬ
    wall=self.parent.entity.hascomp("IconSmooth")
    dir=(self.parent.dir*(not wall)+self.diroff)%4

    angle=self.rotation+self.parent.rot
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
    if self.parent.uid==39:
      print(name)

    if name==self.last_name:return

    if name in readystates:
      self.image=readystates[name]  #get cached image
    else:  #generate new
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
    if self.sprite:
      self.layerMap:dict[str,Layer]={}
      self.color=colors.get(
        comp.get("color","White"),
        (255,255,255,255))
      events.subscribe("setvis",self.setvis,entity.uid)
      events.subscribe("updateMap",self.updateMap,entity.uid)
      events.subscribe("setDepth",self.setdepth,entity.uid)
      self.rsi=loadrsi(self.sprite)
      self.layers=[Layer(self,data) for data in comp.get("layers",[])]
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
    if not self.needs_upd and not force:return
    if self.directional:
      self.rot=(self.realrot+45)%90-45
    else:
      self.rot=self.realrot
    self.rot=0
    self.dctnl=self.directional
    #layer updating5
    for layer in self.layers:
      if layer.needs_upd or not self.ready:
        layer.update(self.dir)
    self.ready=True
    layers=[layer for layer in self.layers if layer.ready and layer.visible]

    defaultrot=not self.rot%90

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
      w,h=self.size
      hr=int(h*abs(cos(self.rot))+w*abs(sin(self.rot)))
      wr=int(h*abs(sin(self.rot))+w*abs(cos(self.rot)))
      rotsize=(max(wr,32),max(hr,32))
      self.final=pg.Surface(rotsize,pg.SRCALPHA)
      self.shaded  =pg.Mask(rotsize)
      self.unshaded=pg.Mask(rotsize)
      #if True:
      #  pg.draw.circle(self.final,[255,0,0],[a/2 for a in self.final.size],min(self.final.size)/2)

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
    centdiff=(Vector(self.rect.size)/2-self.center)
    roff=centdiff.rotate(0)-Vector(self.final.size)/2+self.offset
    self.realrect=pg.Rect(roff,self.final.size)


  def Transform(self,comp:Components.TransformComponent.Transform):
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

  def setdepth(self,args):
    self.depth=args.get("depth",self.depth)
    self.resub()
  @catch
  def render(self,args:dict):
    #w=args["rw"]
    #w("outer")
    #if self.pos==[0,0]:return
    #if not self.visible:return


    sx,sy,sw,sh=args["screenRect"]
    rx,ry,rw,rh=self.realrect
    rx+=self.pos.x*resolution
    ry+=self.pos.y*resolution
    if rx<sx+sw and rx+rw>sx and ry<sy+sh and ry+rh>sy:
    #if self.realrect.move((self.pos*resolution).pos).colliderect(screenRect):
      #w("other")
      self.update(args.get("forcereload",False))
      #w("updating")
      pos: tuple=args["pos"]
      dst: pg.Surface=args["dst"]
      dst_wh: tuple=dst.get_size()
      dpos=Vector(-pos[0]
                  +dst_wh[0]/2
                  +self.pos[0]*32,
                  (-pos[1]
                   -dst_wh[1]/2
                   +(self.pos[1])*32)*-1)
      fpos=dpos+self.realrect.topleft

      if mouse.lasthovered==self.uid and self.entity.hascomp("InteractionOutline"):
        mouse.active=1
        dst.blit(outline(self.final),(fpos-[1,1]).pos)

      smap: pg.Mask=args["smap"]
      smap.draw(self.shaded,fpos)
      smap.erase(self.unshaded,fpos)
      #for i in range(len(self.rotshaders)):
      #  s,b=self.shading[i],self.rotshaders[i]
      #  addshade(smap,s,fpos,b)
      dst.blit(self.final,fpos.pos)
      mouse.checkMouse(self.final,fpos,self.uid)
      #w("other")
    #else:
      #w("decline")