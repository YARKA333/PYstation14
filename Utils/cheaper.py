def colliderect(x1,y1,w1,h1,x2,y2,w2,h2):
  return x1<x2+w2 and x1+w1>x2 and y1<y2+h2 and y1+h1>y2
def colliderect_pg(rect1,rect2):
  x1,y1,w1,h1=rect1
  x2,y2,w2,h2=rect2
  return colliderect(x1,y1,w1,h1,x2,y2,w2,h2)
def collidepoint(x1,y1,w1,h1,x2,y2):
  return x1<x2<x1+w1 and y1<y2<y1+h1
def collidepoint_pg(rect1,x,y):
  x1,y1,w1,h1=rect1
  return collidepoint(x1,y1,w1,h1,x,y)