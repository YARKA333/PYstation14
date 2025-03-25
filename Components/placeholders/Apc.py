from Modules.component import BaseComponent,component
from Components.Sprite import Sprite

@component
class Apc(BaseComponent):
  after=["Sprite"]
  def __init__(self,entity,comp):
    self.entity=entity
    self.sprite: Sprite=entity.comp("Sprite")
    layer=self.sprite.get("enum.ApcVisualLayers.ChargeState")
    if layer:
      layer.state="display-full"