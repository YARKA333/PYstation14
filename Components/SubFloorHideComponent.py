import Utils.shared as shared
import Utils.events as events

class SubFloorHide:
  def __init__(self,entity,args):
    self.pos=None
    self.map=shared.get("layerMap")
    self.uid=entity.uid
    events.followcomp("Transform",self.Transform,entity)
    events.followcomp("Sprite",self.Sprite,entity)
  def Transform(self,args):
    self.pos=args.pos
    self.calc()
  def Sprite(self,args):
    if self.pos!=None:
      self.calc()
  def calc(self):
    tile=self.map.getTile([self.pos[0]-.5,self.pos[1]-.5])
    if not tile:print(f"no tile {self.pos}?")
    else:
      #self.visible=tile.isSubfloor
      events.call("setvis",tile.isSubfloor,self.uid)