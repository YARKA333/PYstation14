from Modules.Locale import Loc
import Modules.Verbs as verbs
import Utils.events as events
import yaml

icoknow=verbs.icon("VerbIcons/vv.svg.192dpi.png")

class MetaData:
  def __init__(self,entity,args):
    self.uid=entity.uid
    self.proto=args.get("proto")
    self.data=args.get("comps")
    self.name=Loc(f"ent-{self.proto}")
    self.desc=Loc(f"ent-{self.proto}.desc")
    events.subscribe("getVerbs",self.verbs,self.uid)
  def verbs(self,args):
    return [{
      "name":"Know.",
      "priority":10,
      "img":icoknow,
      "click":self.printdata,
      }]
  def printdata(self,args):
    print(yaml.dump(self.data))