from Modules.component import BaseComponent,component
from Components.Appearance import Appearance

@component
class GasVentPump(BaseComponent):
  after = ["Appearance"]
  def __init__(self,entity,comp):
    self.entity=entity
    self.appearance:Appearance=entity.comp("Appearance")
    if self.appearance:
      self.appearance.set({"enum.VentPumpVisuals.State":"Out"})
    else:
      print("noap",repr(entity))