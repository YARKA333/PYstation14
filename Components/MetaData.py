from Modules.Locale import Loc
import Modules.Verbs as verbs
import Utils.events as events
from Modules.component import BaseComponent,component
from Modules.rsi import allp

icoknow=verbs.icon("VerbIcons/vv.svg.192dpi.png")

@component
class MetaData(BaseComponent):
  def __init__(self,entity,args):
    entity.meta=self
    self.entity=entity
    self.uid=entity.uid
    self.proto=args.get("proto")
    self.data=args.get("comps")
      #name
    name=f"ent-{self.proto}"
    self.name=Loc(name)
    if self.name==name:self.name=allp.get("name")
    if not self.name:self.name="НОУНЕЙМ!"
      #descriprion
    desc=Loc(f"ent-{self.proto}.desc")
    self.desc=Loc(desc)
    if self.desc==desc:self.desc=allp.get("desc")
    if not self.desc:self.desc="no"
      #verbs
    events.subscribe("getVerbs",self.verbs,self.uid)
  def verbs(self,args):
    return [{
      "name":"Know.",
      "priority":10,
      "img":icoknow,
      "click":self.printdata,
      }]
  def printdata(self,args):
    #print(yaml.dump(self.data))
    print(self.name)
    print(self.desc)
    for name,comp in self.entity.components.items():
      print(f"  "+name)
      print("    "+repr(comp).replace("\n","\n    "))
  def __repr__(self):
    return "\n".join([
      "proto: "+self.proto,
      "name: "+self.name,
      "desc: "+self.desc,])
