import Components.SpriteComponent
import Utils.events as events

class Appearance:
  def __init__(self,entity,args):
    self.uid=entity.uid
    self.data={}
    events.subscribe("set_appearance",self.set,self.uid)
    events.subscribe("get_appearance",self.get,self.uid)
  def set(self,args):
    self.data|=args
    print(f"appearance changed:{self.data}")
    events.call("AppearanceChanged",self.data,self.uid)
  def get(self,args):
    return self.data

class GenericVisualizer:
  def __init__(self,entity,args):

    self.uid=entity.uid
    self.data=args.get("visuals")
    print("GenVis:",self.data)
    if not self.data:print("genvis empty")
    self.sprite:Components.SpriteComponent.Sprite=None
    events.followcomp("Sprite",self.setsprite,entity)
    events.subscribe("AppearanceChanged",self.update,self.uid)
  def setsprite(self,args):
    self.sprite=args
  def update(self,args:dict):
    if not self.sprite:
      return
    for param,subdata in self.data.items():
      if not param in args:
        continue
      value=args[param]
      #if isinstance(value,bool):
      #  value=str(value).lower()
      #elif not isinstance(value,str):
      #  print("Gviz serializer unknown type:",value)
      #  value=str(value)
      for map,actions in subdata.items():
        def reformat():
          action=actions.get(value)
          if action:return action
          action=actions.get(str(value).lower())
          if action:return action
          print(f"no action to {value} in {actions}")
        action=reformat()
        print(action)
        layer=self.sprite.layerMap.get(map)
        if not layer:
          print(f"genvis cant find layer map {map}")
          continue
        print(f"applying layer {map} data {action}")
        layer|=action


