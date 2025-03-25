from Components.Sprite import Sprite,Layer
from Utils.mathutils import vec
import Utils.events as events
import Utils.shared as shared
from Modules.component import BaseComponent,component
from Utils.vector2 import Vector
grid=shared.get("globalgrid")



@component
class IconSmooth(BaseComponent):
  after = ["Sprite"]
  def __init__(self,entity,args):
    self.sprite:Sprite=entity.comp("Sprite")
    self.pos=Vector()
    self.uid=entity.uid
    self.ctype=dict.get(args,"key")
    self.mode=dict.get(args,"mode","Corners")
    if self.mode=="Corners":
      self.dstate=dict.get(args,"base")
      state0=self.dstate+"0"
      for i in range(4):
        layer=Layer(self.sprite,state0)
        layer.diroff=i
        self.sprite.layers.append(layer)
        self.sprite.layerMap|={i:layer}
      self.calcsprite()
      events.subscribe("pingpos",self.OnPing)
    events.followcomp("Transform",self.OnTransform,entity)

  def scan(self):
    self.nbrs=[]
    for i in range(8):
      dif=Vector(vec(4-i))
      pos=dif+self.pos
      for entity in grid.get(str(pos)):
        if not entity:continue
        comp=entity.comp("IconSmooth")
        if not comp:continue
        if comp.ctype!=self.ctype:continue
        self.nbrs.append(1)
        break
      else:
        self.nbrs.append(0)
    #print(f'scanned {self.pos} with results {self.nbrs}')


  def OnTransform(self,comp):
    #events.call("pingpos",{"pos":self.pos,"ctype":self.ctype,"uid":self.uid})
    self.pos=comp.pos
    if self.mode=="Corners":
      self.calcsprite()

  def calcsprite(self):
    self.scan()
    for i in range(4):
      j=i*2
      state=f"{self.dstate}{
         self.nbrs[j%8]*4+
         self.nbrs[(j+1)%8]*2+
         self.nbrs[(j+2)%8]}"
      self.sprite.layerMap[i].state=state
  def OnPing(self,args):
    self.calcsprite()
