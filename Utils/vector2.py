class Vector:
  def __init__(self,pos:tuple|list[float]|str):
    self.pos=[1488,1488]
    if type(pos)==list and len(pos)==2:
      self.pos=pos
    elif type(pos)==tuple:
      self.pos=pos
    elif type(pos)==str:
      try:
        tup=[float(a) for a in pos.split(",")]
        if len(tup)==2:
          self.pos=tup
        else:self.error(pos)
      except:self.error(pos)
    else:self.error(pos)
  def error(self,pos):
    raise ValueError(f"{pos} is not a coordinate")
  def __sub__(self,other):
    return Vector([self.pos[0]-other.pos[0],self.pos[1]-other.pos[1]])
  def __str__(self):
    return str(self.pos)
  def __add__(self,other):
    return Vector([self.pos[0]+other.pos[0],self.pos[1]+other.pos[1]])
  def __eq__(self,other):
    return self.pos==other.pos
  def __mul__(self,other):
    if type(other) in [float,int]:
      other=Vector([other]*2)
    return Vector([self.pos[0]*other.pos[0],self.pos[1]*other.pos[1]])
  def __divmod__(self,other):
    if type(other) in [float,int]:
      other=Vector([other]*2)
    return Vector([self.pos[0]%other.pos[0],self.pos[1]%other.pos[1]])
  def __truediv__(self,other):
    if type(other) in [float,int]:
      other=Vector([other]*2)
    return Vector([self.pos[0]/other.pos[0],self.pos[1]/other.pos[1]])
