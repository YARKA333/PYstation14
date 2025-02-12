import math
from typing import overload
import collections
import re

class Vector:
  @overload
  def __init__(self,pos: tuple[float|int,float|int]):...
  @overload
  def __init__(self,x: float|int,y: float|int):...
  @overload
  def __init__(self):...
  def __init__(self,*args):
    if len(args)==0:
      self.pos=[0,0]
    elif len(args)==1:
      self.pos=args[0]
    elif len(args)==2:
      self.pos=args
    else:raise ValueError(f"invalid Vector args count:\n{repr(args)}")
  @classmethod
  @property
  def ONE(cls):
    return cls(1,1)

  @classmethod
  @property
  def ZERO(cls):
    return cls(0,0)

  @staticmethod
  def resolve_coord(value):
    if isinstance(value,int|float):
      return float(value)
    elif isinstance(value,str):
      try:
        return float(value)
      except:raise ValueError(f"invalid coord string: {value}")
    else:raise ValueError(f"invalid coord: {value}")

  def __getitem__(self, item):
    if item in [0,"0","x","X"]:
      return self._x
    elif item in [1,"1","y","Y"]:
      return self._y
    else:raise IndexError(f"Vector index error: {item}")
  def __setitem__(self, key, value):
    val=self.resolve_coord(value)
    if key in [0,"0","x","X"]:
      self._x=val
    elif key in [1,"1","y","Y"]:
      self._y=val
    else:raise IndexError(f"Vector index error: {key}")
  @property
  def x(self):
    return self._x
  @property
  def y(self):
    return self._y
  @x.setter
  def x(self,value):
    self._x=self.resolve_coord(value)
  @y.setter
  def y(self,value):
    self._y=self.resolve_coord(value)
  @property
  def pos(self):
    return self._x,self._y
  @pos.setter
  def pos(self,arg):
    if isinstance(arg,str):
      try:
        match=re.match(r"[\[{(\"' ]*([\d.-]+)[\"',;: ]+([\d.-]+)[]})\"' ]*",arg)
        self.pos=match.groups()
      except:
        raise ValueError(f"invalid Vector string:\n{repr(arg)}")
    elif isinstance(arg,collections.abc.Sequence):
      assert len(arg)==2,ValueError("invalid Vector sequence length")
      self.x,self.y=arg
    elif arg is None:
      self.pos=0,0
    elif isinstance(arg,Vector):
      self.pos=arg.pos
    else:
      raise ValueError(f"Vector recieved 1 parameter:\n{arg}")
  @staticmethod
  def vecmod(other,single=True):
    orig=other
    if isinstance(other,float|int) and single:
      other=[other]*2
    if not isinstance(other,Vector):
      try:
        other=Vector(other)
      except:raise ValueError(f"invalid vector{" modifier" if single else ""}:{orig}")
    return other
  def max(self,*others):
    others=[self.vecmod(other,False) for other in others]
    x=max([other.x for other in others])
    y=max([other.y for other in others])
    return Vector(x,y)
  def __iter__(self):
    return iter(self.pos)
  def __len__(self):
    return 2
  def __iadd__(self, other):
    other=self.vecmod(other,False)
    self._x+=other._x
    self._y+=other._y
    return self
  def __isub__(self, other):
    other=self.vecmod(other,False)
    self._x-=other._x
    self._y-=other._y
    return self
  def __imul__(self, other):
    other=self.vecmod(other)
    self._x*=other._x
    self._y*=other._y
    return self
  def __itruediv__(self, other):
    other=self.vecmod(other)
    self._x/=other._x
    self._y/=other._y
    return self
  def __imod__(self, other):
    other=self.vecmod(other)
    self._x%=other._x
    self._y%=other._y
    return self
  def __ifloordiv__(self, other):
    other=self.vecmod(other)
    self._x//=other._x
    self._y//=other._y
    return self
  def __str__(self):
    return f"{self._x:g},{self._y:g}"
  def __repr__(self):
    return f"Vector({self._x},{self._y})"

  def angle(self,radians=False): #angle from (0,1)
    a=math.copysign(math.acos(self._y/self.length()),self._x)
    if radians:
      return a
    else:
      return math.degrees(a)

  def length(self):
    return math.hypot(self._x,self._y)
  def normalize(self):
    self/=self.length()

  def rotate_ip(self,angle,radians=False):
    if not radians:
      angle=math.radians(angle)
    x=self._x*math.cos(angle)-self._y*math.sin(angle)
    y=self._x*math.sin(angle)+self._y*math.cos(angle)
    self._x=x
    self._y=y

  def rotate(self,angle,radians=False):
    if not radians:
      angle=math.radians(angle)
    x=self._x*math.cos(angle)-self._y*math.sin(angle)
    y=self._x*math.sin(angle)+self._y*math.cos(angle)
    return Vector(x,y)

  def __sub__(self,other):
    other=self.vecmod(other,False)
    return Vector(self._x-other._x,self._y-other._y)

  def __add__(self,other):
    other=self.vecmod(other,False)
    return Vector(self._x+other._x,self._y+other._y)

  def __eq__(self,other):
    try:
      other=self.vecmod(other,False)
    except:return False
    return self.pos==other.pos
  def __ne__(self, other):
    return not self==other
  def __ge__(self, other):
    other=self.vecmod(other,False)
    return self.length()>=other.length()
  def __gt__(self, other):
    other=self.vecmod(other,False)
    return self.length()>other.length()
  def __le__(self, other):
    other=self.vecmod(other,False)
    return self.length()<=other.length()
  def __lt__(self, other):
    other=self.vecmod(other,False)
    return self.length()<other.length()
  def __neg__(self):
    return Vector(-self.x,-self.y)
  def __bool__(self):
    return bool(self.pos)

  def __mul__(self,other):
    other=self.vecmod(other)
    return Vector(self._x*other._x,self._y*other._y)

  def __floordiv__(self,other):
    other=self.vecmod(other)
    return Vector(self._x//other._x,self._y//other._y)

  def __mod__(self,other):
    other=self.vecmod(other)
    return Vector(self._x%other._x,self._y%other._y)

  def __truediv__(self,other):
    other=self.vecmod(other)
    return Vector(self._x/other._x,self._y/other._y)

  def __floor__(self):
    return Vector(math.floor(self._x),math.floor(self._y))

class CVector(Vector):
  def __get__(self,instance,cls):
    print(f"Getting")
    return self
  def __set__(self,instance,value):
    print(f"Setting to {value}")
    self.__init__(value)