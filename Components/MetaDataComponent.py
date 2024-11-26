from Modules.Locale import Loc

class MetaData:
  def __init__(self,entity,args):
    self.proto=args.get("proto")
    self.name=Loc(f"ent-{self.proto}")
    self.desc=Loc(f"ent-{self.proto}.desc")
