import os
import Utils.shared as shared
import io
from zipfile import ZipFile
from pathlib import Path

def joinpath(*paths:str|os.PathLike):
  result=""
  for path in paths:
    if path=="":continue
    path=path.replace("\\","/")
    if path[0]=="/":
      path=path[1:]
    if path[-1]=="/":
      path=path[0:-1]
    if result:result+="/"
    result+=path
  return result

def listdir(path,source=None):
  if not source: source=shared.get("resources")
  assert os.path.isdir(source)
  try:
    return os.listdir(joinpath(source,path))
  except:pass
  try:
    with ZipFile(joinpath(source,"Content.Client.zip")) as archive:
       return[f.split("/")[-1] for f in archive.namelist() if f.startswith(path)]
  except:raise Exception("incorrect path: "+path)

def openfile(path,source=None):
  if not source:source=shared.get("resources")
  assert os.path.isdir(source)
  #try:
  jpath=Path(joinpath(source,path))
  return io.BytesIO(jpath.read_bytes())
  #except:pass
  #try:
  #  with ZipFile(joinpath(source,"Content.Client.zip")) as archive:
  #    return io.BytesIO(archive.read(joinpath(path)))
  #except:raise Exception("incorrect path: "+path)

def ensuredir(path):
  dirs=path.split("/")[:-1]
  cpath=""
  for i in range(len(dirs)):
    cpath="/".join(dirs[:i+1])
    if os.path.isdir(cpath): continue
    os.mkdir(cpath)

def namelist(path:str,source=None,full=False):
  if not path.startswith("C:/"):
    if source=="Project": fpath=path
    else:
      if not source: source=shared.get("resources")
      fpath=joinpath(source,path)
  else:fpath=path
  #try:
  e=[]
  for a,b,c in os.walk(fpath):
    a=a.replace(fpath,"")
    for d in c:
      try:
        e.append(
          joinpath(path,a,d)
          if full else
          joinpath(a,d))
      except IndexError:print(f'a:{a},d:{d}')
  return e