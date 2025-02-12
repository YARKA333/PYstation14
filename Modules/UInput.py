import pygame as pg
import Utils.events as events
import tkinter.simpledialog as tk
import Modules.entityModule as eMod
from Modules.rsi import *
import Modules.Interface as iFace
import Modules.Verbs as Verbs
from Utils.vector2 import Vector

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

popups=[]
mouse_mask=pg.mask.Mask((3,3),fill=True)

pos=Vector()
gpos=Vector()
hovered=None
holding=None
ishovered=0
lasthovered=0
buttons=[False]*3
uiactive=0
scanRect:"ScanRect"=None
windows:dict[str:iFace.ContextMenu]={}
active=0


  #popup
popup_font=pg.Font(joinpath(shared.get("resources"),"/Fonts/NotoSans/NotoSans-Italic.ttf"),13)
MinimumPopupLifetime=0.7
MaximumPopupLifetime=5
PopupLifetimePerCharacter=0.04

class ScanRect:
  def __init__(self,gpos:Vector):
    self.pos=gpos-[8,8]
    self.rect=pg.Rect(self.pos.pos,[16,16])
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
  pos=Vector(pg.mouse.get_pos())
  gpos=pos/2
  pressed=pg.mouse.get_pressed(num_buttons=3)
  for i in range(3):
    if not buttons[i] and pressed[i]:
      if not uiactive:
        windows|={"contextmenu":None}
        if spawn.spawning:
          s=args["gpos"]
          w=pg.display.get_window_size()
          spawn.click(i,[s[0]+(pos[0]-w[0]/2)/64,s[1]-(pos[1]-w[1]/2)/64])
        elif i==0:
          if holding:
            events.call("use",{"target":hovered,"pos":gpos},entity=holding)
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
from Utils.watch import watch
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
  for popup in popups.copy():
    popup["time"]+=args["delta"]
    lifetime=popup["lifetime"]
    total_time=popup["time"]
    vis=min(1.0,1.0-max(0.0,total_time-lifetime/2)*2/lifetime)*255
    img=popup_font.render(popup["message"],True,[255,255,255])
    img.set_alpha(vis)
    dpos=transpose(popup["pos"],args["dpos"],args["surf"])
    dpos=[dpos[0]-img.width/2,dpos[1]-img.height/2-min(8.0,12.0*(total_time**2+total_time))]
    surf.blit(img,dpos)
    if not vis:
      popups.remove(popup)



events.subscribe("overlay",drowerlay)

def transpose(gpos,spos,surf:pg.Surface):
  return (-spos[0]*2
   +surf.size[0]/2
   +gpos[0]*64,
   (-spos[1]*2
    -surf.size[1]/2
    +gpos[1]*64)*-1)

def PopupPos(message,pos):
  popup={
    "message":message,
    "pos":pos,
    "lifetime":pg.math.clamp(len(message)*PopupLifetimePerCharacter,MinimumPopupLifetime,MaximumPopupLifetime),
    "time":0
  }
  popups.append(popup)

def PopupEntity(message,entity):
  if isinstance(entity,int):entity=eMod.find(entity)
  pos=entity.comp("Transform").pos
  PopupPos(message,pos)




def checkMouse(image,imagepos:Vector,uid):
  """
  check if @image in @imagepos is under mouse, and if it is set hovered id to @uid
  """
  global ishovered,hovered,scanRect
  size=image.get_size()
  rect=pg.Rect(imagepos.pos,size)
  if spawn.spawning:return
  if uiactive:return
  scanRectSus=scanRect and rect.colliderect(scanRect.rect)
  if not(rect.collidepoint(gpos.pos) or scanRectSus): return
  mask=pg.mask.from_surface(image,1)
  if scanRectSus and mask.overlap(scanRect.mask,(scanRect.pos-imagepos).pos):
      scanRect.result.append(uid)
  if mask.overlap(mouse_mask,(gpos-imagepos).pos):
    hovered=uid
    ishovered=1



def setholding(args):
  global holding
  holding=args.get("uid",holding)
events.subscribe("setholding",setholding)

events.subscribe("frame",update)



