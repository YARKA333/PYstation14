shared={}
def set(var,val):
  shared.update({var:val})
def get(var):
  if var in shared.keys():
    return shared.get(var)
  else:
    shared.update({var:None})
    print(f"REQUESTED NOT EXISTING SHARED VAR {var}")
    return
def delete(var):
  if var in shared.keys():
    return shared.pop(var)