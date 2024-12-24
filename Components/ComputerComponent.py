import Utils.events as events

class Computer:
  def __init__(self,entity,args):
    print("computer",args)
    self.uid=entity.uid
    events.subscribe("start",self.start)
  def start(self,args):
    events.call("set_appearance",{"enum.ComputerVisuals.Powered":True},self.uid)

#no functionality yet