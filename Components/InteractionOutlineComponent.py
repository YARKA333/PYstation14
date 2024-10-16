import pygame as pg
import Utils.events as events

convolution_mask=pg.mask.Mask((3,3),fill=True)

class InteractionOutline:
  def __init__(self,entity,args):
    pass

mouse=[0,0]
def update_mouse(arg):
  global mouse
  mouse=pg.mouse.get_pos()
events.subscribe("frame",update_mouse)



def outline(image):
  mask=pg.mask.from_surface(image)
  return mask.convolve(convolution_mask).to_surface(setcolor=[0,255,0,180],unsetcolor=[0,0,0,0])
