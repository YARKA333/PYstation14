import os
import hashlib
import json

data_path="kake/hash.json"
def ensuredir(path):
  dirs=path.split("/")[:-1]
  cpath=""
  for i in range(len(dirs)):
    cpath="/".join(dirs[:i+1])
    if os.path.isdir(cpath): continue
    os.mkdir(cpath)
ensuredir(data_path)

def hash_path(path):
  hasher=hashlib.sha256()

  if os.path.isfile(path):
    with open(path,"rb") as f:
      for chunk in iter(lambda:f.read(4096),b""):
        hasher.update(chunk)
  elif os.path.isdir(path):
    for root,dirs,files in os.walk(path):
      for file in files:
        file_path=os.path.join(root,file)
        with open(file_path,"rb") as f:
          for chunk in iter(lambda:f.read(4096),b""):
            hasher.update(chunk)
  else:
    raise ValueError("Указанный путь не является файлом или директорией")

  return hasher.hexdigest()

def get_data()->dict:
  if os.path.isfile(data_path):
    with open(data_path,"rt") as file:
      return json.load(file)
  else:
    return {}

def set_data(data:dict):
  with open(data_path,"wt") as file:
    json.dump(data,file)

def update_data(new_data:dict):
  data = get_data()
  data|=new_data
  set_data(data)

def get_hash(key):
  return get_data().get(key)

def set_hash(key,hash):
  update_data({key:hash})

def check_path_hash(key,path,update:bool=False)->bool:
  new_hash=hash_path(path)
  old_hash=get_hash(key)
  if new_hash==old_hash:
    return True
  else:
    if update:
      set_hash(key,new_hash)
    return False

def getmtime(path):
  if os.path.isfile(path):
    return os.path.getmtime(path)
  elif os.path.isdir(path):
    return max(os.path.getmtime(os.path.join(root, file)) for root, dirs, files in os.walk(path) for file in files)
  else:raise FileNotFoundError(path)

def ismod(path:str,db_path:str="kake/mtime.json")->bool:
  """
  checks if file or folder were modified since last check
  :param path: path to file or floder to check
  :param db_path: path to DB, "kake/mtime.json" by default
  :return: False if file is in DB and is not modified
  """
  try:
    with open(db_path,'r') as f:
      db=json.load(f)
  except:
    db={}
  current_date = getmtime(path)
  if current_date!=db.get(path):
    db[path] = current_date
    ensuredir(db_path)
    print(db)
    with open(db_path,'w') as f:
      json.dump(db,f,indent=2)
    return True
  return False

def check(path:str,db_path:str="kake/mtime.json")->bool:
  """
  checks if file or folder were modified since last check
  :param path: path to file or floder to check
  :param db_path: path to DB, "kake/mtime.json" by default
  :return: True if file is in DB and is not modified
  """
  return not ismod(path,db_path)