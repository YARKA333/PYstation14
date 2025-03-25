import Components.Sprite as sprsys
from Modules.rsi import allprotos
from Modules.component import BaseComponent,component
import Utils.events as events

LAYER_PREFIX="enum.HumanoidVisualLayers."

@events.listen("proto_ready")
def init_protos(args):
  global species_protos,species_sprites,parts_sprites,markingPoints,markings
  species_protos=allprotos["species"]
  species_sprites=allprotos["speciesBaseSprites"]
  parts_sprites=allprotos["humanoidBaseSprite"]
  markingPoints=allprotos["markingPoints"]
  markings=allprotos["marking"]


@component
class HumanoidAppearance(BaseComponent):
  after = ["Sprite"]
  def __init__(self,entity,args):
    self.entity=entity
    self.sprite:sprsys.Sprite=entity.comp("Sprite")
    self.species=args["species"]
    species_class=species_protos[self.species]
    sprite_proto=species_class["sprites"]
    layers={}

    for layer_id,base_id in species_sprites[sprite_proto]["sprites"].items():
      if layer_id=="Special":
        continue
      mapid=LAYER_PREFIX+layer_id
      data=parts_sprites[base_id]
      spritedata=data.get("baseSprite")
      layers[mapid]=spritedata

    for mark in markingPoints[species_class["markingLimits"]]["points"].values():
      if not mark["required"]:continue
      markid=mark["defaultMarkings"][0]
      for layer in markings[markid]["sprites"]:
        map=markid+layer["state"]
        layers[map]=layer

    for map,data in layers.items():
      oldlayer=self.sprite.layerMap.get(map)
      if data:
        print(data)
        if oldlayer:
          for k,v in data.items():
            oldlayer.__setattr__(k,v)
        else:
          newlayer=sprsys.Layer(self.sprite,data)
          self.sprite[map]=newlayer
      elif oldlayer:
        oldlayer.visible=False

      #eyez
    eyelayer=self.sprite.get(LAYER_PREFIX+"Eyes")
    if eyelayer:eyelayer.color=[0,0,0]

    self.sprite.ready=False





