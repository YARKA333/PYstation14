class Multidict:
  def __init__(self):
    self.dict={}
  def add(self,key,value):
    values=dict.get(self.dict,key,[])
    values.append(value)
    self.dict.update({key:values})
  def get(self,key):
    return dict.get(self.dict,key,[])
  def remove(self,key,value):
    values=dict.get(self.dict,key,[])
    if value in values:
      values.remove(value)
      self.dict.update({key:values})
      return True
    return False
  def delete(self,key):
    if key in self.dict.keys():
      return self.dict.pop(key)
    return None
  def __str__(self):
    return str(self.dict)
