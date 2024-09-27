shared={}
def set(var,val):
  shared.update({var:val})
def get(var):
  return dict.get(shared,var)
def delete(var):
  if var in shared.keys():
    return shared.pop(var)