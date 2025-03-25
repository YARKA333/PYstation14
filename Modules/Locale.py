import os
import re
from Modules.rsi import namelist,joinpath
from tqdm import tqdm
from Utils.hasher import check
import Utils.shared as shared
import pickle as pk
from os.path import exists


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
    lines=[]
    a=None
    cur_line=0
    while 1:
      cur_line+=1
      line=raw.readline()
      if "=" in line or not line:
        if lines:
          if not a:
            print(f"Locale error in file {file}:{cur_line}")
            return
          parsed=parse_text("".join(lines))
          addpak(a,parsed)
        if not line:break
        lines=[]
      if not line:break
      if line.startswith("#"):continue
      if line.endswith("\n"): line=line[:-1]
      if remspace(line)=="":continue
      if "=" in line:
        lines=[]
        #print("definitive:",line)
        sides=[remspace(a) for a in line.split("=")]
        c=sides[0]
        if c.startswith("."):
          a=b+c
        else:
          a=b=c
        lines.append(sides[1])
      else:
        #print("additional:",line)
        lines.append(remspace(line))

functions={"CAPITALIZE":str.capitalize}

class Text:
  def __init__(self, value):
    self.value = value
  def __repr__(self):
    return f'Text("{self.value}")'
  def __call__(self,args):
    #print(f"called text block {self.__repr__()}")
    return self.value

class Var:
  def __init__(self, name):
    self.name = remspace(name.replace("$",""))
  def __repr__(self):
    return f'Var("{self.name}")'
  def __call__(self,args):
    #print(f"called var {self.__repr__()}")
    #if self.name in args:
      return args.get(self.name)
    #return Loc(self.name,args)

class Selector:
  def __init__(self,s:str):
    try:
      var,forms=(s.split("->",1))
    except:raise ValueError(s)
    self.var=parse_var(var)
    froms=re.sub(r"\n\s*","",forms)
    self.dict={}
    key=None
    self.default=None
    current=""
    for char in forms:
      if char=="[":
        if key:self.dict|={key:parse_text(current[1:])}
        key=None
        current=""
      elif char=="]":
        key=current
        if self.default=="P":
          self.default=key
        current=""
      elif char=="*":
        self.default="P"
      elif char=="\n":pass
      else:
        current+=char
    self.dict|={key:parse_text(current[1:])}
  def __repr__(self):
    return f"Selector({self.var} -> {self.dict})"
  def __call__(self,args):
    #print(f"called selector {self.__repr__()}")
    var=self.var(args)
    pak=None
    #print(var)
    #print(self.dict)
    #print("var",repr(var))
    #print("isint",isinstance(var,int))
    #print("isbool",isinstance(var,bool))
    if isinstance(var,bool):
      var2="true" if var else "false"
      #print("var2",var2)
      pak=self.dict.get(var2)
      #print("pak v2",pak)
    elif isinstance(var,int):
      var2=abs(var)
      var=str(var)
      ntn=not 10<var2<20
      if var2%10==1 and ntn:
        var2="one"
      elif 1<var2%10<5 and ntn:
        var2="few"
      else:
        var2="other"
      pak=self.dict.get(var2)
    if not pak:
      pak=self.dict.get(var)
      #print("pak",pak)
    if not pak:
      pak=self.dict[self.default]
      #print("reserve",pak)

    return fill(pak,args)

class Function:
  def __init__(self,s):
    current=""
    arg=False
    self.args=[]
    self.func=""
    for char in s:
      match char:
        case "(":
          arg=0
          self.func=current
          current=""
        case ",":
          arg+=1
          self.args.append(parse_var(current))
          current=""
        case ")":
          arg=False
          self.args.append(parse_var(current))
        case " ":
          pass
        case _:
          current+=char
    self.function=functions.get(self.func)
  def __repr__(self):
    return f'{self.func}({",".join(str(a) for a in self.args)})'
  def __call__(self,args):
    formargs=[a(args) for a in self.args]
    rpd=f'{self.func}({",".join(repr(a) for a in formargs)})'
    if not self.function:
      self.function=functions.get(self.func)
    if self.function:
      return self.function(*formargs)
    else:
      return rpd

class Link:
  def __init__(self,name):
    self.name=remspace(name)
  def __repr__(self):
    return f'Link("{self.name}")'
  def __call__(self,args):
    return Loc(self.name,args)


def parse_var(s):
  s=remspace(s)
  if "->" in s:
    return Selector(s)
  elif "(" in s:
    return Function(s)
  elif "$" in s:
    return Var(s)
  else:
    return Link(s)

def parse_text(s:str):
  result=[]
  current=""
  level=0
  for char in s:
    if char=="{":
      if level==0:
        if current!="":
          result.append(Text(current))
        current=""
      else:current+=char
      level+=1
    elif char=="}":
      level-=1
      if level==0:
        result.append(parse_var(current))
        current=""
      else:current+=char
    else:
      current+=char
  if current!="":
    result.append(Text(current))
  return result


def fill(pak:list,args:dict={}):
  parts=""
  #print(pak)
  for a in pak:
    result=str(a(args))
    parts+=result

  return parts


  #return str(pak)+"".join(str(a(args)) for a in pak)

def getlet(name:str):
  name=name.replace("ent-","")
  try:return name[0].upper()
  except:return "-"

def Loc(name:str,args:dict={}):
  pak=paks.get(getlet(name))
  if not pak:return name
  pat=pak.get(name)
  if not pat:return name
  return fill(pat,args)

def load(ldr):
  global paks
  res=shared.get("resources")
  if not res: res="C:/Servers/SS14 c2/Resources/"
  kake_path="kake/loc.pk"
  path=joinpath(res,"Locale")
  #old_hash=hasher.get_hash("Locale")
  #new_hash=hasher.hash_path(path)

  if exists(kake_path) and check(path):
    with open(kake_path,"rb") as file:
      paks=pk.load(file)
  else:
    namespace=namelist(joinpath(res,"Locale/ru-RU/"),full=True)
    for path in tqdm(ldr.iter(namespace),desc="Translating"):
      addfile(path)
    with open(kake_path,"wb") as file:
      pk.dump(paks,file)
    #hasher.set_hash("Locale",new_hash)


if __name__=="__main__":
  print(Loc("ent-APCBasic.suffix",{"name":"иМя"}))

  class Player:
    def __init__(self,name,gender="neuter"):
      self.name=name
      self.gender=gender
    def __str__(self):
      return self.name
    def __repr__(self):
      return f'(Player {self.gender} {self.name})'
  def GENDER(ent:Player):
    return ent.gender
  functions|={"GENDER":GENDER}

  p1=Player("ОНО")
  p2=Player("ОНИ","epicene")
  p3=Player("ОНА","female")
  p4=Player("ОН","male")
  for p in [p1,p2,p3,p4]:
    print(Loc("cream-pied-component-on-hit-by-message",{"thrower":p}))

  while 1:
    inp=input()
    print(Loc(input()))