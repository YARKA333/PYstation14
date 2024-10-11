import pygame as pg
import Utils.events as events

convolution_mask=pg.mask.Mask((3,3),fill=True)
mouse_mask=pg.mask.Mask((5,5),fill=True)
class InteractionOutline:
  def __init__(self,entity,args):
    pass

mouse=[0,0]
def update_mouse(arg):
  global mouse
  mouse=pg.mouse.get_pos()
events.subscribe("frame",update_mouse)

def check_col(image:pg.Surface,pos:list):
  size=image.get_size()
  if max(abs(pos[0]+16-mouse[0]/2),abs(pos[1]+16-mouse[1]/2))>16:return False
  mask=pg.mask.from_surface(image)
  if not mask.overlap(mouse_mask,[(mouse[i])/2-pos[i] for i in [0,1]]):return False
  return True

def outline(image):
  mask=pg.mask.from_surface(image)
  return mask.convolve(convolution_mask).to_surface(setcolor=[0,255,0,180],unsetcolor=[0,0,0,0])
