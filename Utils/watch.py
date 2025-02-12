import time
class watch:
  def __init__(self):
    self.t=time.time()
    self.dict={}
  def __call__(self,desc="-"):
    if desc not in self.dict:
      self.dict[desc]=0
    self.dict[desc]+=time.time()-self.t
    self.t=time.time()
  def flush(self):
    print(f'''
-------------------
{"\n".join([f"{k} {v:.3f}" for k,v in self.dict.items()])}
SUMMARY:{sum(self.dict.values()):.3f}
-------------------''')
import sys
def catch(func):
  def wrapper(self,*args,**kvargs):
    try:
      return func(self,*args,**kvargs)
    except:
      print(f"An error occurred in uid {self.uid}",file=sys.stderr)
      raise
  return wrapper


