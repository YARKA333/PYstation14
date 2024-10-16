from Modules.rsi import *
import pygame as pg
import random
pg.mixer.init()

soundlib={}
def getsound(spec):
  if "path" in spec.keys():
    path=joinpath(ss14_folder,spec["path"])
    if path in soundlib.keys():
      sound=soundlib[path]
    else:
      sound=pg.mixer.Sound(path)
      soundlib.update({path:sound})
    return sound
  elif "collection" in spec.keys():
    paths=allprotos["soundCollection"].get(spec["collection"],[])["files"]
    if paths!=[]:
      return getsound({"path":random.choice(paths)})
  else:return None

def playSound(spec,vol=1):
  sound=getsound(spec)
  if sound!=None:
    sound.set_volume(vol)
    sound.play()



