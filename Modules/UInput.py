import pygame as pg
import Utils.events as events
import tkinter.simpledialog as tk
import Modules.entityModule as eMod
from Modules.rsi import *
import Modules.Interface as iFace
import Modules.Verbs as Verbs

class Spawn:
  def __init__(self):
    self.spawning=None
  def start(self):
    global windows
    proto=tk.askstring("Spawn","Enter prototype ID:")
    if not proto in allp.keys():
      print(f"No proto \"{proto}\"")
      return
    windows|={"contextmenu":None}
    self.spawning=proto
  def click(self,button,pos):
    if button==0:
      eMod.spawn(self.spawning,[{"type":"Transform","pos":pos}])
      print(f"{self.spawning} spawned at {pos}")
    if button==2:
      self.spawning=None
spawn=Spawn()
def getName(uid):

  try:
    comp=eMod.getEcomp(uid,"MetaData")
  except:return "ERR 1"
  return (comp.name if comp else "ERR 0")


mouse_mask=pg.mask.Mask((3,3),fill=True)

pos=[0,0]
gpos=[0,0]
hovered=None
holding=None
ishovered=0
lasthovered=0
buttons=[False]*3
uiactive=0
scanRect=None
windows:{str:iFace.ContextMenu}={}
active=0

class ScanRect:
  def __init__(self,gpos):
    self.pos=[gpos[0]-8,gpos[1]-8]
    self.rect=pg.Rect(self.pos,[16,16])
    self.mask=pg.Mask([16,16],True)
    self.result=[]

cursors=[
  pg.cursors.Cursor(pg.SYSTEM_CURSOR_ARROW),
  pg.cursors.Cursor(pg.SYSTEM_CURSOR_HAND),]

def update(args):
  global ishovered,hovered,lasthovered,buttons,pos,scanRect,gpos,windows,uiactive
  if scanRect:
    objs=scanRect.result
    windows|={"contextmenu":None}
    if len(objs):
      menu=iFace.ContextMenu({"pos":pos,"type":"context"})
      for obj in objs:
        objSprite=eMod.getEcomp(obj,"Sprite")
        if objSprite and hasattr(objSprite,"final"):
          icon=objSprite.final
        else:
          icon=pg.Surface([1,1],pg.SRCALPHA)
        menu.addelement({
          "name":f"{getName(obj)} ({obj}, {eMod.getEcomp(obj,"MetaData").proto})",
          "uid":obj,
          "hover":Verbs.getVerbs,
          "img":icon,
          })
      menu.calculate()
      windows|={"contextmenu":menu}
    scanRect=None
  pos=pg.mouse.get_pos()
  gpos=[pos[0]/2,pos[1]/2]
  pressed=pg.mouse.get_pressed(num_buttons=3)
  for i in range(3):
    if not buttons[i] and pressed[i]:
      if not uiactive:
        windows|={"contextmenu":None}
        if spawn.spawning:
          s=args["gpos"]
          w=pg.display.get_window_size()
          spawn.click(i,[s[0]+(pos[0]-w[0]/2)/64,s[1]-(pos[1]-w[1]/2)/64+1])
        elif i==0:
          if holding:
            events.call("use",{"target":hovered,"pos":[pos[0]/2,pos[1]/2]},entity=holding)
          else:
            events.call("use",entity=hovered)
        elif i==2:
          scanRect=ScanRect(gpos)
  buttons=pressed
  if not ishovered:
    hovered=None

  lasthovered=hovered
  ishovered=0
  return {"hover":hovered}

def drowerlay(args):
  global uiactive,active
  surf=args["surf"]
  uiactive=0
  for w in windows.values():
    if not w:continue
    cout=w.render(surf,not uiactive)
    uiactive+=cout[0]
    active+=cout[1]
  pg.mouse.set_cursor(cursors[bool(active)])
  active=0
events.subscribe("overlay",drowerlay)

def checkMouse(image,imagepos,uid):
  """
  check if @image in @imagepos is under mouse, and if it is set hovered id to @uid
  """
  global ishovered,hovered,scanRect
  size=image.get_size()
  rect=pg.Rect(imagepos,size)
  if spawn.spawning:return
  if uiactive:return
  scanRectSus=scanRect and rect.colliderect(scanRect)
  if not(rect.collidepoint(gpos) or scanRectSus): return
  mask=pg.mask.from_surface(image,1)
  if scanRectSus and mask.overlap(scanRect.mask,[scanRect.pos[i]-imagepos[i] for i in [0,1]]):
      scanRect.result.append(uid)
  if mask.overlap(mouse_mask,[gpos[i]-imagepos[i] for i in [0,1]]):
    hovered=uid
    ishovered=1



def setholding(args):
  global holding
  holding=args.get("uid",holding)
events.subscribe("setholding",setholding)

events.subscribe("frame",update)



