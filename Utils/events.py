#from threading import Thread
from tqdm import tqdm
eventdata={}
entity_eventdata={}
eventorders={}
counter=0
removed=[]

def subscribe(name:str,function:classmethod,entity:int=None)->int:
  global eventdata,entity_eventdata,counter
  if entity:
    collection=dict.get(entity_eventdata,entity,{})
  else:
    collection=eventdata
  events=dict.get(collection,name,[])
  counter+=1
  events.append((function,counter))
  collection.update({name:events})
  if entity:
    entity_eventdata.update({entity:collection})
  else:
    eventdata=collection
  return counter

def unsubscribe(token):
  if token:
    removed.append(token)

def subscribeorder(name,function,order=None):
  global eventorders
  events=dict.get(eventorders,name,{})
  orderevents=dict.get(events,order,[])
  events.append(function)
  events.update({order:orderevents})
  eventorders.update({name:events})

def unsubscribe_deprecated(name=None,function=None,entity=None):
  global eventdata,entity_eventdata
  if entity:
    collection=dict.get(entity_eventdata,entity,{})
  else:
    collection=eventdata
  if name:
    if not name in collection.keys():
      print(f"No event called \"{name}\"")
    elif function:
      events=dict.get(collection,name,[])
      if function in events:
        events.remove(function)
        collection.update({name:events})
      #else:print(f"No function {function} in {name}")
    else:
        collection.update({name:[]})
  elif function:
    a=0
    for n,f in collection.items():
      if function in f:
        a=1
        f.remove(function)
        collection.update({n,f})
    if not a:print(f"there was no {function} in events")
  else:raise BaseException("unsubscrive w/o arguments!")


  events.append(function)
  collection.update({name:events})
  if entity:
    entity_eventdata.update({entity:collection})
  else:
    eventdata=collection

def sortorder(name):
  global eventdata,eventorders
  eventorder=dict.get(eventorders,name,{})
  events=[v for k in sorted(sorted(eventorder)) for v in eventorder[k]]
  eventdata.update({name:events})

def rcall(name,args=None):
  namespace=dict.get(eventdata,name,[])
  for func in namespace:
    if func[1] in removed: #lag?
      removed.remove(func[1])
      namespace.remove(func)
      continue
    func[0](args)

def call(name,args=None,entity:int|None=None,noreturn:bool=True,bar:str=None):
  if entity:
    collection=dict.get(entity_eventdata,entity,{})
  else:
    collection=eventdata
  returns=[]
  namespace=dict.get(collection,name,[])
  if bar==None:
    namespace=dict.get(collection,name,[])
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

threadc=1

def asynccall(name,args=None):
  global eventdata
  funcs=dict.get(eventdata,name,[])
  size=len(funcs)//threadc+1
  threads=[Thread(target=asyncbatch,args=(funcs[i*size:min((i+1)*size,len(funcs))],name,args)) for i in range(threadc)]
  for t in threads:
    t.start()
  #for t in threads:
  #  t.join()

def asyncbatch(funcs,name,args=None):
  for func in funcs:
    #if j>=len(eventdata):return
    func(args)
def followcomp(name,func,entity):
  subscribe(name,func,entity.uid)
  if name in entity.components.keys():
    func(entity.components[name])
