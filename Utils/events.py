eventdata={}
entity_eventdata={}

def subscribe(name,function,entity=None):
  global eventdata,entity_eventdata
  if entity:
    collection=dict.get(entity_eventdata,entity,{})
  else:
    collection=eventdata
  events=dict.get(collection,name,[])
  events.append(function)
  collection.update({name:events})
  if entity:
    entity_eventdata.update({entity:collection})
  else:
    eventdata=collection

def call(name,args=None,entity=None):
  global eventdata,entity_eventdata
  if entity:
    collection=dict.get(entity_eventdata,entity,{})
  else:
    collection=eventdata
  returns=[]
  for func in dict.get(collection,name,[]):
    ret=func(args)
    if ret!=None:
      returns.append(ret)
  #if not name in ["scanpos","render"]:
  #  print(f'called {name} in {entity} with {args} and {returns}')
  return returns

def followcomp(name,func,entity):
  subscribe(name,func,entity.uid)
  if name in entity.components.keys():
    func(entity.components[name])
