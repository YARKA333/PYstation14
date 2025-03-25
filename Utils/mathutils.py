import math
def sin(a):return math.sin(math.radians(a))
def cos(a):return math.cos(math.radians(a))
def vec(a):
  return [max(-1,min(1,abs(4-(a+i)%8)-2)) for i in [-2,0]]
def svec(a,l=1):
  return [l*sin(a),l*cos(a)]

def rotate_vector(vector:list[float,float],angle:float):
  if vector==[0,0]:return vector
  angle_rad=math.radians(angle)
  return [
    vector[0]*math.cos(angle_rad)-vector[1]*math.sin(angle_rad),
    vector[0]*math.sin(angle_rad)+vector[1]*math.cos(angle_rad)]