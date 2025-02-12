#from threading import Thread
from tqdm import tqdm
eventdata={}
#entity_eventdata={}
#eventorders={}
tokens={}
dependata={}
counter=0
removed=set()

def subscribe(name:str,function:classmethod,entity:int=0,before:str|list|set=None,after:str|list|set=None)->int:
  global eventdata,dependata,counter,tokens
  entdata=eventdata.get(entity,{})
  if not entdata:
    eventdata|={entity:entdata}
  namespace=entdata.get(name,[])
  if not namespace:entdata|={name:namespace}
  def depdata(depends,cname):
    dep=depends.get(cname,set())
    if not dep: depends|={cname:dep}
    return dep

  def toset(n):
    if isinstance(n,str):
      return {n}
    elif isinstance(n,list):
      return set(n)
    elif isinstance(n,set):
      return n
    else:
      return set()

  classname=function.__qualname__.split('.')[0]
  if before or after:
    entdep=dependata.get(entity,{})
    if not entdep: dependata|={entity:entdep}
    depends=entdep.get(name,{})
    if not depends: entdep|={name:depends}
    depends[0]=True
    for dep in toset(before):
      data=depdata(depends,dep).add(classname)
    for dep in toset(after):
      depdata(depends,classname).add(dep)

  counter+=1

  namespace.append((function,counter,classname))
  tokens[counter]=(entity,name)
  return counter

def unsubscribe(token):
  #if token:
  #  removed.add(token)
  if token in tokens:
    ent,name=tokens[token]
    namespace=eventdata[ent][name]
    for i,n in enumerate(namespace):
      if n[1]==token:
        namespace.pop(i)


#def subscribeorder(name,function,order=None):
#  global eventorders
#  events=dict.get(eventorders,name,{})
#  orderevents=dict.get(events,order,[])
#  events.append(function)
#  events.update({order:orderevents})
#  eventorders.update({name:events})

def delentity(uid:int):
  if uid in eventdata:
    eventdata.pop(uid)

#def sortorder(name):
#  global eventdata,eventorders
#  eventorder=dict.get(eventorders,name,{})
#  events=[v for k in sorted(sorted(eventorder)) for v in eventorder[k]]
#  eventdata.update({name:events})
#from Utils.watch import watch
def rcall(name,args=None):
  #=args.get("cw",watch())
  namespace=dict.get(eventdata[0],name,[])
  #w("namespace")
  for func in namespace:
    #w("cycling")
    #if func[1] in removed: #lag?
    #  removed.remove(func[1])
    #  namespace.remove(func)
    #  print("deleted sth")
    #  continue
    func[0](args)
    #w("THE FUNCTION")

def call(name,args:dict={},entity:int=0,noreturn:bool=True,bar:str=None):
  namespace=eventdata.get(entity,{}).get(name,[])
  if not namespace:
    #print(f"NO ONE's LISTENING TO {name}")
    return []
  depends=dependata.get(entity,{}).get(name,{})
  returns=[]
  done=set()
  if depends.get(0):
    depends[0]=False
    for i in range(len(namespace)):
      for a in range(len(namespace)-i):
        classname=namespace[i]
        if not classname in depends:break
        dep=depends[classname]
        if done>=dep:
          break
        else:
          namespace.append(namespace.pop(i))
      else:
        print("depends error")
        break

  if bar==None:
    for func in namespace:
      if func[1] in removed: #lag?
        removed.remove(func[1])
        namespace.remove(func)
        continue
      ret=func[0](args)
      if not noreturn and ret!=None:
        returns.append(ret)
  else:
    for func in tqdm(namespace,desc=bar):
      if func[1] in removed:
        removed.remove(func[1])
        namespace.remove(func)
        continue
      ret=func[0](args)
      if not noreturn and ret!=None:
        returns.append(ret)
  return returns


def followcomp(name,func,entity):
  subscribe(name,func,entity.uid)
  if name in entity.components.keys():
    func(entity.components[name])
