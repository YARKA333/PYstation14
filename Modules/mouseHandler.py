import pygame as pg
import Utils.events as events

names=["LMB","RMB","MMB"]

mouse_mask=pg.mask.Mask((3,3),fill=True)

r=False
l=False
m=False
pos=[0,0]
hovered=0
ishovered=0
lasthovered=0
buttons=[False,False,False]
active=0

carrow=pg.cursors.Cursor(pg.SYSTEM_CURSOR_ARROW)
chand=pg.cursors.Cursor(pg.SYSTEM_CURSOR_HAND)

def update(args):
  global ishovered,hovered,lasthovered,r,l,m,buttons,pos,active
  pressed=pg.mouse.get_pressed(num_buttons=3)
  for i in range(3):
    if not buttons[i] and pressed[i]:
      events.call(names[i],entity=hovered)
  buttons=pressed
  l,r,m=buttons
  pos=pg.mouse.get_pos()
  if not ishovered:
    hovered=None
  if active:
    pg.mouse.set_cursor(chand)
  else:
    pg.mouse.set_cursor(carrow)
  active=0
  lasthovered=hovered
  ishovered=0
  return {"hover":hovered}

def check(image,imagepos,uid):
  """
  check if @image in @imagepos is under mouse, and if it is set hovered id to @uid
  """
  global ishovered,hovered
  size=image.get_size()
  if max(abs(imagepos[0]+16-pos[0]/2),abs(imagepos[1]+16-pos[1]/2))>16: return
  mask=pg.mask.from_surface(image)
  if not mask.overlap(mouse_mask,[(pos[i])/2-imagepos[i] for i in [0,1]]): return
  hovered=uid
  ishovered=1

events.subscribe("frame",update)



