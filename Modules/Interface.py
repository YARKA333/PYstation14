import pygame as pg

import Components.MetaDataComponent
import Modules.rsi as rsi
import random
import math
import time
import Modules.Verbs as Verbs
import Modules.entityModule as eMod
import Utils.shared as shared

resources=shared.get("resources")

#font class
font=pg.font.Font(rsi.joinpath(resources,"Fonts/NotoSansDisplay/NotoSansDisplay-Regular.ttf"),size=16)
bold_font=pg.font.Font(rsi.joinpath(resources,"Fonts/NotoSansDisplay/NotoSansDisplay-Bold.ttf"),size=16)

#size properties
line_size=15
item_space=4
max_width=360

#colors
border1_color=[50,52,70]
border2_color=[36,36,43]
item_colors=[[26,26,30],[29,49,49]]
scroll_colors=[[84,84,85],[90,90,92],[102,102,104]]

#audio
pg.init()
pg.mixer.init()
hover_sound=pg.mixer.Sound(rsi.joinpath(resources,"Audio/UserInterface/hover.ogg"))
hover_sound.set_volume(0.02)

#cursors
cursors=[
  pg.cursors.Cursor(pg.SYSTEM_CURSOR_ARROW),
  pg.cursors.Cursor(pg.SYSTEM_CURSOR_HAND),]

#default context arrow
more_arrow_name=rsi.joinpath(resources,"Textures/Interface/VerbIcons/group.svg.192dpi.png")
more_arrow=pg.Surface([32,32],pg.SRCALPHA)
more_arrow.blit(pg.transform.smoothscale_by(pg.image.load(more_arrow_name),0.5),[8,8])


def remspace(txt:str):
  while 1:
    if txt.startswith(" "):
      txt=txt[1:]
    elif txt.endswith(" "):
      txt=txt[:-1]
    else:return txt

def wrap_text(text,max_width):
  lines=[]
  line=""
  words=[]
  for word in [a+" " for a in text.split()]:
    if font.size(remspace(word))[0]>max_width:
      words+=list(word)
    else:
      words.append(word)
  for word in words:
    if font.size(remspace(line+word))[0]>max_width:
      lines.append(remspace(line))
      line=""
    line+=word
  lines.append(line)
  return lines

def split_text(text,max_width):
  lines=wrap_text(text,max_width)
  max_lines=len(lines)
  testing_scale=int(math.log2(max_width))-1
  testing=2**(testing_scale+1)
  while 1:
    lines=wrap_text(text,testing)
    dif=2**max(testing_scale,0)
    if len(lines)>max_lines:
      testing+=dif
    else:
      if testing_scale<=0: return lines,testing
      testing-=dif
    testing_scale-=1





class ContextMenu:
  def __init__(self,args):
    self.mouse=None
    self.total_scroll=0
    self.pos=args["pos"]
    self.uid=args.get("uid")
    self.name=args.get("name","DefaultStupidName")
    self.type=args.get("type","Custom")
    self.scroll_queue=0
    self.elements=[]
    self.hovered=None
    self.pressed=False
    self.timer=None
    self.scroll=None
    self.child=None
    self.childActive=False
    self.stableHovered=None
  def addelement(self,element):
    self.elements.append(element)
  def calculate(self):
    strings=[]
    self.width=0
    for i in range(len(self.elements)):
      item=self.elements[i]
      item["submenu"]=[32,32] if "hover" in item else [0,0]
      hv=32 if "hover" in item else 0
      local_border=(48+hv)
      local_max_width=(max_width-local_border)
      lines,local_width=split_text(item["name"],local_max_width)
      self.width=max(self.width,local_width+local_border)
      item["lines"]=lines
      item["text_h"]=len(lines)*22
      item["height"]=max(
        item["text_h"],
        32,
        hv)
    self.total_height=sum([a["height"]+4 for a in self.elements])+4
    self.height=min(self.total_height,364)
    self.twidth=self.width
    if self.total_height>364:
      self.scroll=0

      self.twidth+=10
    self.subsurf=pg.Surface((-4+self.twidth,self.total_height-4))
    self.cook()
  def cook(self):
    self.subsurf.fill(border2_color)
    summ=0
    self.rects:list[pg.Rect]=[]
    for i in range(len(self.elements)):
      item=self.elements[i]
      rect=pg.Rect(2,summ+2,self.width-8,item["height"])
      pg.draw.rect(self.subsurf,item_colors[i==self.hovered],rect)
      self.rects.append(rect)
      img=item["img"]
      simg=pg.transform.scale_by(img,32/max(img.size))
      self.subsurf.blit(simg,[2+(32-simg.get_width())/2,summ+2+(item["height"]-32)/2+(32-simg.get_height())/2])
      for l in range(len(item["lines"])):
        self.subsurf.blit(font.render(item["lines"][l],True,[255,255,255]),
                          [6+32,summ+2+(item["height"]-item["text_h"])/2+l*22])
      if "hover" in item:
        self.subsurf.blit(more_arrow,[self.width-6-32,summ+2+(item["height"]-32)/2])
      item["fall"]=summ
      summ+=item["height"]+4
  def render(self,surf:pg.Surface,active=True):
    windowRect=pg.Rect(self.pos[0],self.pos[1],self.twidth,self.height)
    pg.draw.rect(surf,border1_color,windowRect)
    surf.blit(self.subsurf,[self.pos[0]+2,self.pos[1]+2],[0,self.total_scroll,self.twidth-4,self.height-4])

    pressed=pg.mouse.get_pressed(num_buttons=3)[0]
    #self.mouse=pressed
    mouse_pos=pg.mouse.get_pos()
    active=active and windowRect.collidepoint(mouse_pos)
    if not active:
      mouse_pos=[-1,-1]

    hovered=self.stableHovered if self.childActive else None
    updated=0
    element=None
    uid=self.uid
    for i in range(len(self.rects)):
      buttonRect=self.rects[i]
      if buttonRect.collidepoint([mouse_pos[0]-self.pos[0]-2,mouse_pos[1]-self.pos[1]-2+self.total_scroll]):
        hovered=i
    if hovered!=None:
      element=self.elements[hovered]
      uid=element.get("uid",uid)
      if (pressed
      and not self.pressed
      and "click" in element):
        element["click"](uid)
    if self.hovered!=hovered:
      if self.child:
        self.timer=time.time()
      if hovered!=None:
        if "hover" in element:
          self.timer=time.time()
        hover_sound.play()
      self.hovered=hovered
    updated=1
    #print(time.time()-self.timer)
    if self.timer and time.time()-self.timer>0.25:
      self.timer=None
      self.stableHovered=hovered
      if hovered!=None:
        menu1=ContextMenu({"uid":uid,"pos":[self.pos[0]+self.twidth,self.pos[1]+element["fall"]]})
        menu1.elements=element["hover"](uid)
        menu1.calculate()
        self.child=menu1
      else:
        self.child=None
    hover=0
    if self.scroll!=None:
      size=(self.height-4)**2/self.total_height
      prop=(self.height-4-size)
      scrollRect=pg.Rect(self.pos[0]+self.width-2,self.pos[1]+2+self.scroll,10,size)
      if scrollRect.collidepoint(mouse_pos) or self.mouse!=None:
        hover=1
        if pressed:
          hover=2
          if self.mouse==None:
            self.mouse=mouse_pos[1]-self.scroll
          self.scroll=pg.math.clamp((mouse_pos[1]-self.mouse),0,prop)
        else:
          self.mouse=None
      self.scroll=pg.math.clamp(self.scroll+self.scroll_queue*prop/(self.total_height-self.height)*-50,0,prop)
      self.scroll_queue=0
      self.total_scroll=self.scroll/prop*(self.total_height-self.height)
      pg.draw.rect(surf,scroll_colors[hover],scrollRect)
    self.pressed=pressed
    if updated:self.cook()
    iscursor=bool(hovered!=None or hover)
    if self.child:
      cout=self.child.render(surf,not active)
      self.childActive=bool(cout[0])
      active+=cout[0]
      iscursor+=cout[1]
    return active,iscursor

  def mscr(self,direcrtion):
    self.scroll_queue+=direcrtion

class ExaMenu:
  def __init__(self,args):
    self.pos=args["pos"]
    self.uid=args.get("uid")
    calculate()
  def calculate(self):
    meta:Components.MetaDataComponent.MetaData=eMod.getEcomp(self.uid,"MetaData")
    lines=wrap_text(meta.desc,274)
    title_lines=wrap_text(f"{meta.name} ({meta.proto})",278)
    surf


def getimg(ind,i=False):
  global rimages
  while not ind in rimages:
    path=random.choice(namespace)
    if i and not "Interface/VerbIcons" in path:continue
    rimg=pg.image.load(path)
    if rimg.get_size()==(32,32):
      rimages[ind]=rimg
    elif i and rimg.get_size()==(64,64):
      rimg2=pg.transform.smoothscale_by(rimg,0.5)
      rimages[ind]=rimg2
  return rimages[ind]

if __name__=="__main__":
  screen=pg.display.set_mode((1000,1000))
  pg.init()


  namespace=rsi.namelist("C:/Servers/SS14 c2/Resources/Textures",full=True)
  i=0
  while 1:
    if i>=len(namespace):break
    if namespace[i].endswith(".png"):
      i+=1
    else:
      namespace.pop(i)
  rimages={}



  menu1=ContextMenu("Test",[20,10])
  menus=[]
  menus.append(menu1)

  def test(line):print(line)

  def test2(line:str,pos:list):
    print(1)
    menu2=ContextMenu("test2",pos)
    for word in line.split():
      menu2.addelement({
        "name":word,
        "priority":10,
        "img":getimg(random.random(),i=1),
      })
    menu2.calculate()
    menus.append(menu2)


  with open("../test.txt","rt",encoding="UTF-8") as sud:
    while 1:
      line=sud.readline()
      if not line:break
      menu1.addelement({
        "name":line,
        "priority":10,
        "img_l":getimg(random.random(),i=1),
        "img_r":more_arrow,
        "click":(test,line),
        "hover":(test2,line),
      })




  menu1.calculate()

  while 1:
    screen.fill([20,20,20])
    for menu in menus:
      menu.render(screen)
    pg.display.update()
    for event in pg.event.get():  #event handler
      if event.type==pg.QUIT:
        pg.quit()
        quit(1488)
      if event.type==pg.MOUSEWHEEL:
        menu1.mscr(event.y)


