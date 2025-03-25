from Modules.component import BaseComponent,component
from Components.PointLight import PointLight

@component
class LitOnPowered(BaseComponent):
  def __init__(self,entity,comp):
    self.entity=entity
    self.light:PointLight=entity.comp("PointLight")
    if self.light:
      self.light.enabled=True
