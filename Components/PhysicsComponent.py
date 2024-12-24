from enum import Enum
import math
import pymunk as munk
import pymunk.pygame_util as munkgame
import Utils.events as events
import pygame as pg
from Modules.rsi import rotate_vector
from Modules.Verbs import icon
import Utils.shared as shared

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


space=munk.Space()
space.damping=0.8

hrenico=icon("fist.svg.192dpi.png")
debugico=icon("VerbIcons/debug.svg.192dpi.png")

def toscreen(bpos,dpos,wh):
  return [-dpos[0]*2
          +wh[0]/2
          +bpos[0]*2,
         (-dpos[1]*2
          -wh[1]/2
          +(bpos[1]-1)*2)*-1+64]

class Fixtures:
  def __init__(self,entity,args):
    self.fixtures=args.get("fixtures",{})
    events.call("Fixtures",self,entity.uid)

class Physics:
  def __init__(self,entity,args):
    self.map=shared.get("layerMap")
    self.can_collide=args.get("canCollide",True)
    self.transforming=False
    self.uid=entity.uid
    self.args=args
    self.bodyType=args.get("bodyType","Static")
    events.subscribe("update physics",self.update)
    self.body=munk.Body()
    self.body.mass=1
    self.body.__setattr__("uid",self.uid)
    self.body.body_type=self.body.STATIC
    events.followcomp("Transform",self.Transform,entity)
    events.followcomp("Fixtures",self.Fixtures,entity)
    events.subscribe("P_DR",self.render)
    events.subscribe("Set_collidable",self.Set_collidable,self.uid)
    events.subscribe("getVerbs",self.getVerbs,self.uid)
    space.add(self.body)

  def update(self,args):
    if self.body.is_sleeping or self.body.velocity==munk.Vec2d(0,0):return
    if self.body.body_type==munk.Body.STATIC:return
    self.transforming=True
    events.call("teleport",{
      "pos":self.body.position/32,
      "rot":self.body.angle,
    },self.uid)
    self.transforming=False
    #tile: Modules.Tiles.Floor
    pos=self.body.position
    tile=self.map.getTile([int(pos[0]/32-.5),int(pos[1]/32-.5)])
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
    self.body.apply_force_at_local_point([2,0],[0,0])

  def print_data(self,args):
    body=self.body
    print("pos",body.position)
    print("mode",body.body_type)
    print("mask",self.mask)
    print("layer",self.layer)

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
      shape.__setattr__("collidable",args.get("state",shape.collidable))

  def Transform(self,args):
    if self.transforming:
      self.transforming=False
      return
    self.body.position=[args.pos[e]*32 for e in [0,1]]
    self.body.angle=math.radians(args.rot)
  def Fixtures(self,args:Fixtures):
    for name,fix in args.fixtures.items():
      fis=fix.get("shape",{})
      shape=None
      self.mask=fix.get("mask")
      self.layer=fix.get("layer")
      if "bounds" in fis:
        bounds=list(map(float,fis["bounds"].split(",")))
        shape=munk.Poly(self.body,[[bounds[i//2*2]*32,bounds[(i+1)%4//2*2+1]*32] for i in range(4)])
      elif "vertices" in fis:
        shape=munk.Poly(self.body,[[float(b)+1 for b in a.split(",")] for a in fis["vertices"]])
      elif "radius" in fis:
        shape=munk.Circle(self.body,fis["radius"]*32)
      else:
        print(fis)
      if shape:
        shape.elasticity=0
        shape.mass=1
        shape.__setattr__("mask",self.get(self.mask))
        shape.__setattr__("layer",self.get(self.layer))
        shape.__setattr__("collidable",self.can_collide)
        space.add(shape)
      self.body.body_type={
        "DYNAMIC":munk.body.Body.DYNAMIC,
        "STATIC":munk.body.Body.STATIC,
        "KINEMATICCONTROLLER":munk.body.Body.DYNAMIC}[self.bodyType.upper()]


  def render(self,args):
    surf=args["surf"]
    for shape in self.body.shapes:
      if not shape.shapes_collide(ssh):return
      if isinstance(shape,munk.shapes.Poly):
        pg.draw.polygon(surf,[100,200,100],[toscreen([rotate_vector(v,math.degrees(self.body.angle))[e]+self.body.position[e]+[0,1][e] for e in [0,1]],args["dpos"],surf.get_size()) for v in shape.get_vertices()])
      elif isinstance(shape,munk.shapes.Circle):
        pg.draw.circle( surf,[100,200,100],toscreen(self.body.position,args["dpos"],surf.get_size()),shape.radius*2)
      else:print(shape)



allb=[]
bodies=[]

def spawn_ball(args):
  s=pg.mouse.get_pos()
  w=pg.display.get_window_size()
  w=[w[e]/2 for e in [0,1]]
  pos=[(s[0]/2+args["dpos"][0]-w[0]/2),-(s[1]/2-args["dpos"][1]-w[1]/2)+32]
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

  p=mouse_body.position
  print(p)
  hit=space.point_query_nearest(p,0,munk.ShapeFilter())
  print(hit)
  if hit:
    print(hit.shape.body.uid)
    print(hit.shape.body.body_type)
  if hit is not None and hit.shape.body.body_type==munk.Body.DYNAMIC:
    print("grib")
    shape=hit.shape
    # Use the closest point on the surface if the click is outside
    # of the shape.
    if hit.distance>0:
      nearest=hit.point
    else:
      nearest=p
    mouse_joint=munk.PivotJoint(
      mouse_body,
      shape.body,
      (0,0),
      shape.body.world_to_local(nearest),
    )
    mouse_joint.max_force=1000
    mouse_joint.error_bias=(1-0.15)**60
    space.add(mouse_joint)

cd=False
def tcd(args):
  global cd
  cd=~cd

events.subscribe("mousegrib",mousegrib)
events.subscribe("mouseungrib",mouseungrib)
events.subscribe("toggle collision debug",tcd)


def pre_solve(arbiter:munk.Arbiter,space,data):
  try:
    shape1,shape2=arbiter.shapes
    a=bool(shape1.layer&shape2.mask)
    b=bool(shape2.layer&shape1.mask)
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

scol=munk.Body(body_type=munk.Body.KINEMATIC)
space.add(scol)
ssh=None


def render(args):
  global draw_options,ssh
  wh=args["surf"].get_size()
  if not ssh:
    bounds=[-wh[0]/4,-wh[1]/4,wh[0]/4,wh[1]/4]
    ssh=munk.Poly(scol,[[bounds[i//2*2]*32,bounds[(i+1)%4//2*2+1]*32] for i in range(4)])
    ssh.sensor=True
    space.add(ssh)

  s=pg.mouse.get_pos()
  pos=args["dpos"]
  #mouse_body.update_velocity(mouse_body,(0,0),0,dt)
  #mouse_body.update_position(mouse_body,dt)
  mouse_body.position=[(s[0]/2+pos[0]-wh[0]/4),-(s[1]/2-pos[1]-wh[1]/4)+32]
  #space.


  scol.position=pos


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
