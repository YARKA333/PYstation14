import os
import re
from Modules.rsi import namelist,joinpath
from tqdm import tqdm
import Utils.shared as shared

def fill_pattern(pattern,args):
  def fill_var(match):
    expr=remspace(match.group(1))
    def var(expr:str)->str:
      if expr.startswith("$"):
        name=expr[1:]
        return args.get(name,name)
      else:
        return Loc(expr)
    def capitalize(match):
      return var(match.group(1)).capitalize()

    pat=r'CAPITALIZE\((.*?)\)'
    expr2=re.sub(pat,capitalize,expr)
    if expr2==expr:
     return var(expr)
    else:
      return expr2

  pat=r'\{(.*?)\}'
  pattern=re.sub(pat,fill_var,pattern)
  return pattern

def remspace(txt:str):
  while 1:
    if txt.startswith(" "):
      txt=txt[1:]
    elif txt.endswith(" "):
      txt=txt[:-1]
    else:return txt
paks={}

def addpak(name,value):
  global paks
  let=getlet(name)
  if not let in paks:
    paks[let]={}
  paks[let][name]=value

def addfile(file:os.PathLike):
  with open(file,"rt",encoding="UTF-8") as raw:
    global packs
    while 1:
      line=raw.readline()
      if not line:break
      if line.endswith("\n"):line=line[:-1]
      sides=[remspace(a) for a in line.split("=")]
      a=None
      for side in sides:
        if side.startswith("#"):
          continue
        if a:
          addpak(a,side)
        else:
          if side.startswith("."):
            a=b+side
          else:
            a=b=side

def getlet(name:str):
  name=name.replace("ent-","")
  try:return name[0].upper()
  except:return "-"

def Loc(name:str,args:dict={}):
  pak=paks.get(getlet(name))
  if not pak:return name
  pat=pak.get(name)
  if not pat:return name
  return fill_pattern(pat,args)

namespace=namelist(joinpath(shared.get("resources"),"Locale/ru-RU/"),full=True)
for path in tqdm(namespace,desc="Translating"):
  addfile(path)

if __name__=="__main__":
  print(Loc("ent-APCBasic.suffix",{"name":"иМя"}))
  while 1:
    print(Loc(input()))