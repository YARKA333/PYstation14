from Modules.component import BaseComponent,component
from Components.Sprite import Sprite
import Utils.events as events
from Modules.soundModule import PathSound
from Modules.Verbs import icon

iconlock=icon("VerbIcons/lock.svg.192dpi.png")
iconunlock=icon("VerbIcons/unlock.svg.192dpi.png")


@component
class WiresPanel(BaseComponent):
  _state=True
  after=['Sprite']
  def __init__(self,entity,comp):
    self.entity=entity
    self.sprite:Sprite=entity.comp("Sprite")
    self.layer=self.sprite.get("enum.WiresVisualLayers.MaintenancePanel")
    events.subscribe("getVerbs",self.getVerbs,entity.uid)
    self.closeSound=PathSound(comp.get("screwdriverCloseSound","/Audio/Machines/screwdriverclose.ogg"))
    self.openSound =PathSound(comp.get("screwdriverOpenSound" ,"/Audio/Machines/screwdriveropen.ogg" ))
    self.openSound.set_volume(0.3)
    self.closeSound.set_volume(0.3)
    self.state=False

  @property
  def state(self):return self._state
  @state.setter
  def state(self,value):
    value=bool(value)
    if self._state!=value:
      self._state=value
      if self.layer:
        self.layer.visible=value
  def open(self,args):
    self.openSound.play()
    self.state=True
  def close(self,args):
    self.closeSound.play()
    self.state=False

  def getVerbs(self,args):
    return [{
      "name":"Close panel",
      "img":iconlock,
      "click":self.close,
    }] if self.state else [{
      "name":"Open panel",
      "img":iconunlock,
      "click":self.open,
    }]
