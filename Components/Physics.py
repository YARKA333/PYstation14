from enum import Enum
import math
import pymunk as munk
import pymunk.pygame_util as munkgame
import Utils.events as events
import pygame as pg
from yaml_tag import tag
from Modules.Verbs import icon
import Utils.shared as shared
from Modules.component import BaseComponent,component
from Utils.vector2 import Vector
import Modules.entityModule as eMod

dt=32/60

class CollisionGroup(Enum):
  Opaque=1<<0  # 1 Blocks light, can be hit by lasers
  Impassable=1<<1  # 2 Walls, objects impassable by any means
  MidImpassable=1<<2  # 4 Mobs, players, crabs, etc
  HighImpassable=1<<3  # 8 Things on top of tables and things that block tall/large mobs.
  LowImpassable=1<<4  # 16 For things that can fit under a table or squeeze under an airlock
  GhostImpassable=1<<5  # 32 Things impassible by ghosts/observers, ie blessed tiles or forcefields
  BulletImpassable=1<<6  # 64 Can be hit by bullets
  InteractImpassable=1<<7  # 128 Blocks interaction/InRangeUnobstructed
  DoorPassable=1<<8  # 256 Allows door to close over top, Like blast doors over conveyors for disposals rooms/cargo.

  MapGrid=1<<9  # Map grids, like shuttles. This is the actual grid itself, not the walls or other entities connected to the grid.

  # 32 possible groups
  AllMask=-1
  NoneMask=0

  # Humanoids, etc.
  MobMask=Impassable|HighImpassable|MidImpassable|LowImpassable
  MobLayer=Opaque|BulletImpassable
  # Mice, drones
  SmallMobMask=Impassable|LowImpassable
  SmallMobLayer=Opaque|BulletImpassable
  # Birds/other small flyers
  FlyingMobMask=Impassable|HighImpassable
  FlyingMobLayer=Opaque|BulletImpassable

  # Mechs
  LargeMobMask=Impassable|HighImpassable|MidImpassable|LowImpassable
  LargeMobLayer=Opaque|HighImpassable|MidImpassable|LowImpassable|BulletImpassable

  # Machines, computers
  MachineMask=Impassable|MidImpassable|LowImpassable
  MachineLayer=Opaque|MidImpassable|LowImpassable|BulletImpassable
  ConveyorMask=Impassable|MidImpassable|LowImpassable|DoorPassable

  # Crates
  CrateMask=Impassable|HighImpassable|LowImpassable

  # Tables that SmallMobs can go under
  TableMask=Impassable|MidImpassable
  TableLayer=MidImpassable

  # Tabletop machines, windoors, firelocks
  TabletopMachineMask=Impassable|HighImpassable
  # Tabletop machines
  TabletopMachineLayer=Opaque|HighImpassable|BulletImpassable

  # Airlocks, windoors, firelocks
  GlassAirlockLayer=HighImpassable|MidImpassable|BulletImpassable|InteractImpassable
  AirlockLayer=Opaque|GlassAirlockLayer

  # Airlock assembly
  HumanoidBlockLayer=HighImpassable|MidImpassable

  # Soap, spills
  SlipLayer=MidImpassable|LowImpassable
  ItemMask=Impassable|HighImpassable
  ThrownItem=Impassable|HighImpassable|BulletImpassable
  WallLayer=Opaque|Impassable|HighImpassable|MidImpassable|LowImpassable|BulletImpassable|InteractImpassable
  GlassLayer=Impassable|HighImpassable|MidImpassable|LowImpassable|BulletImpassable|InteractImpassable
  HalfWallLayer=MidImpassable|LowImpassable

  # Statue, monument, airlock, window
  FullTileMask=Impassable|HighImpassable|MidImpassable|LowImpassable|InteractImpassable
  # FlyingMob can go past
  FullTileLayer=Opaque|HighImpassable|MidImpassable|LowImpassable|BulletImpassable|InteractImpassable

  SubfloorMask=Impassable|LowImpassable


table=CollisionGroup.__dict__
@tag("PhysShapeAabb")
def ps_aabb(bounds="-.5,-.5,.5,.5",**kvargs):
  if kvargs: print(kvargs)
  bounds=list(map(float,bounds.split(",")))
  return munk.Poly(None,[[bounds[i//2*2]*32,bounds[(i+1)%4//2*2+1]*32] for i in range(4)])
@tag("PhysShapeCircle")
def ps_circle(radius,position="0,0",**kvargs):
  if kvargs: print(kvargs)
  return munk.Circle(None,radius*32,Vector(position).pos)
@tag("PolygonShape")
def ps_poly(vertices,**kvargs):
  if kvargs:print(kvargs)
  return munk.Poly(None,[(Vector(a)+[1,1]).pos for a in vertices])


space=munk.Space()
space.damping=0.3

hrenico=icon("fist.svg.192dpi.png")
debugico=icon("VerbIcons/debug.svg.192dpi.png")

def toscreen(bpos,dpos,wh):
  return [-dpos[0]*2
          +wh[0]/2
          +bpos[0]*2,
        -(-dpos[1]*2
          -wh[1]/2
          +(bpos[1]-1)*2)]

@component
class Fixtures(BaseComponent):
  def __init__(self,entity,args):
    self.fixtures=args.get("fixtures",{})
    events.call("Fixtures",self,entity.uid)

@component
class Physics(BaseComponent):
  after = ["Transform"]
  staticjoint=None
  def __init__(self,entity,args):
    if entity.xform.maingrid:
      self.map=shared.get("layerMap")
      self.can_collide=args.get("canCollide",True)
      self.transforming=False
      self.uid=entity.uid
      self.args=args
      self.bodyType=args.get("bodyType","Static")
      self.body=munk.Body()
      self.body.mass=1
      self.body.__setattr__("uid",self.uid)
      self.body.body_type=self.body.STATIC
      events.followcomp("Transform",self.Transform,entity)
      events.subscribe("P_DR",self.render)
      events.subscribe("Set_collidable",self.Set_collidable,self.uid)
      events.subscribe("getVerbs",self.getVerbs,self.uid)
      space.add(self.body)
      events.followcomp("Fixtures",self.Fixtures,entity)
      events.subscribe("update physics",self.update)

  def update(self,args):
    if self.body.is_sleeping or self.body.velocity==munk.Vec2d(0,0):return
    if self.body.body_type==munk.Body.STATIC:return
    self.transforming=True
    events.call("teleport",{
      "pos":self.body.position/32,
      "rot":math.degrees(self.body.angle),
    },self.uid)
    self.transforming=False
    #tile: Modules.Tiles.Floor
    pos=self.body.position
    tile=self.map.getTile([int(pos[e]/32-.5) for e in [0,1]]) #no Vectors
    friction=tile.friction
    #self.body.update_velocity(self.body,[0,0],1-friction,dt)
    #self.body.update_position(self.body,dt)


  def getVerbs(self,args):
    c=[{
      "name":"Physics.",
      "priority":10,
      "img":debugico,
      "click":self.print_data,
      }]
    if not self.body.body_type:
      c.append({
        "name":"Нахрен",
        "priority":10,
        "img":hrenico,
        "click":self.nahren,
        })
    return c

  def nahren(self,args):
    print("nahren!")
    print(self.body.body_type)
    self.body.apply_force_at_local_point([20,0],[0,0])

  def print_data(self,args):

    body=self.body
    print("pos",body.position)
    print("rot",body.angle)
    print("mode",body.body_type)
    for shape in self.body.shapes:
      print("mask",f"{shape.mask:08b}")
      print("layer",f"{shape.layer:08b}")

  @staticmethod
  def get(key):
    if key is None: return 0
    if not isinstance(key,list):
      key=[key]
    result=0
    for k in key:
      if k in table:
        result|=table[k].value
      else:
        print("уэээ",k)
    return result

  def Set_collidable(self,args):
    for shape in self.body.shapes:
      shape.collidable=args.get("state",shape.collidable)

  def Transform(self,args):
    if self.transforming:
      self.transforming=False
      return
    self.body.position=(args.pos*32).pos
    self.body.angle=math.radians(args.rot)
    if args.noRot and not self.staticjoint:
      self.staticjoint=munk.RotaryLimitJoint(
      self.body,screenbody,0,0)
      space.add(self.staticjoint)
  def Fixtures(self,args:Fixtures):
    for name,fix in args.fixtures.items():
      shape:munk.Shape=fix.get("shape",{})
      if shape:
        self.body.shapes.add(shape)
        shape.body=self.body
        shape.elasticity=0
        shape.friction=0.2
        shape.mass=1
        shape.mask=self.get(fix.get("mask","NoneMask"))
        shape.layer=self.get(fix.get("layer","NoneMask"))
        shape.collidable=self.can_collide
        space.add(shape)
      self.body.body_type={
        "DYNAMIC":munk.body.Body.DYNAMIC,
        "STATIC":munk.body.Body.STATIC,
        "KINEMATICCONTROLLER":munk.body.Body.DYNAMIC}[self.bodyType.upper()]


  def render(self,args):
    surf:pg.Surface=args["surf"]
    for shape in self.body.shapes:
      if not shape.mask:return
      if not shape.shapes_collide(screenshape):return
      #hsurf=pg.Surface(surf.get_size())
      #hsurf.set_colorkey([0,0,0])
      #hsurf.set_alpha(100)
      if isinstance(shape,munk.shapes.Poly):
        pg.draw.polygon(surf,
        [100,200,100],[toscreen((Vector(v).rotate(self.body.angle,True)+self.body.position+[0,1]).pos,args["dpos"],surf.get_size()) for v in shape.get_vertices()])
      elif isinstance(shape,munk.shapes.Circle):
        pg.draw.circle(surf,
        [100,200,100],toscreen(self.body.position,args["dpos"],surf.get_size()),shape.radius*2)
      else:print("shape incorrect",shape)
      #surf.blit(hsurf)



allb=[]
bodies=[]

def spawn_ball(args):
  s=pg.mouse.get_pos()
  w=pg.display.get_window_size()
  w=[w[e]/2 for e in [0,1]] #no Vectors
  pos=[(s[0]/2+args["dpos"][0]-w[0]/2),-(s[1]/2-args["dpos"][1]-w[1]/2)] #no Vectors
  body=munk.Body()
  body.position=pos
  body.velocity=[0,10]
  shape=munk.Circle(body,0.2*32)
  space.add(body,shape)
  shape.__setattr__("mask",CollisionGroup.ThrownItem.value)
  shape.__setattr__("layer",0)
  shape.__setattr__("collidable",True)
  shape.mass=1
  shape.elasticity=1

  bodies.append(body)


mouse_body=munk.Body(body_type=munk.Body.KINEMATIC)
mouse_joint=None

def mouseungrib(args):
  global mouse_joint
  if mouse_joint is not None:
    space.remove(mouse_joint)
    mouse_joint=None
def mousegrib(args):
  global mouse_joint
  if mouse_joint is not None:
    space.remove(mouse_joint)
    mouse_joint=None
  ent:eMod.Entity=args.get("hover")
  if not ent:
    print("noent")
    return
  if not ent.hascomp("Physics"):
    print("nophys")
    return
  comp:Physics=ent.comp("Physics")
  body=comp.body
  if not body.body_type==body.DYNAMIC:
    print("static")
    return
  print("success")
  p=mouse_body.position
  print(f"mouse: {p}")
  b=body.position
  dist=math.hypot(p[0]-b[0],p[1]-b[1])
  mouse_joint=munk.SlideJoint(
    mouse_body,
    body,
    (0,0),
    (0,0),
    0,dist
  )
  mouse_joint.max_force=100
  mouse_joint.error_bias=(1-0.15)**60
  space.add(mouse_joint)

cd=False
def tcd(args):
  global cd
  cd=not cd

events.subscribe("mousegrib",mousegrib)
events.subscribe("mouseungrib",mouseungrib)
events.subscribe("toggle collision debug",tcd)


def pre_solve(arbiter:munk.Arbiter,space,data):
  try:
    shape1,shape2=arbiter.shapes
    a=bool(shape1.layer&shape2.mask)
    b=bool(shape2.layer&shape1.mask)
    if "a"=="a":
      return (a or b) and shape1.collidable and shape2.collidable
    #print("m1 ",shape1.mask)
    #print("m2 ",shape2.mask)
    #print("l1 ",shape1.layer)
    #print("l2 ",shape2.layer)
    if not ((a or b) and shape1.collidable and shape2.collidable):
      return False
    elif a or b:
      return True

    elif a:
      s1=shape1
      s2=shape2
    else:
      s1=shape2
      s2=shape1
    impulse=-arbiter.total_impulse*1
    p:munk.ContactPoint=arbiter.contact_point_set.points[0]
    s2.body.apply_impulse_at_world_point(impulse,[p.point_a.x,p.point_a.y])
    return False
  except:return False

space.add_default_collision_handler().begin=pre_solve

debugsurf=pg.Surface([1000,1000],pg.SRCALPHA)
draw_options=munkgame.DrawOptions(debugsurf)

screenbody=munk.Body(body_type=munk.Body.KINEMATIC)
space.add(screenbody)
screenshape=None

def render(args):
  global draw_options,screenshape
  wh=args["surf"].get_size()
  if not screenshape:
    bounds=[-wh[0]/4,-wh[1]/4,wh[0]/4,wh[1]/4]
    screenshape=munk.Poly(screenbody,[[bounds[i//2*2]*32,bounds[(i+1)%4//2*2+1]*32] for i in range(4)])
    screenshape.sensor=True
    space.add(screenshape)
  s=pg.mouse.get_pos()
  pos=args["dpos"]
  #mouse_body.update_velocity(mouse_body,(0,0),0,dt)
  #mouse_body.update_position(mouse_body,dt)
  mouse_body.position=[(s[0]/2+pos[0]-wh[0]/4),-(s[1]/2-pos[1]-wh[1]/4)]
  #space.


  screenbody.position=pos


  #debugsurf.fill([0,0,0,0])
  space.step(32/60)
  #space.debug_draw(draw_options)
  #args["surf"].blit(pg.transform.scale_by(pg.transform.flip(debugsurf,False,True),1),[w/2,-h/2])
  events.call("update physics")
  if cd:
    events.call("P_DR",args)
  for body in bodies:
    bpos=body.position
    dpos=toscreen(bpos,pos,wh)
    pg.draw.circle(args["surf"],[255,0,0],dpos,64*0.2)
    #print(dpos)

events.subscribe("overlay",render)
events.subscribe("spawn_ball",spawn_ball)
