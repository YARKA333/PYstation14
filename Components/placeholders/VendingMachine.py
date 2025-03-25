from Modules.component import BaseComponent,component
from Components.Sprite import Sprite

@component
class VendingMachine(BaseComponent):
  after=["Sprite"]
  def __init__(self,entity,comp):
    self.normalState=comp.get("normalState")
    self.screenState=comp.get("screenState")
    self.entity=entity
    self.sprite: Sprite=entity.comp("Sprite")
    layer=self.sprite.get("enum.VendingMachineVisualLayers.BaseUnshaded")
    if layer:
      layer.visible=True
      layer.state=self.normalState
    layer=self.sprite.get("enum.VendingMachineVisualLayers.Screen")
    if layer:
      layer.visible=True
      layer.state=self.screenState