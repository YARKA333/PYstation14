class Multidict(dict):
  def add(self,key,value):
    values=dict.get(self,key,[])
    values.append(value)
    self.update({key:values})
  def get(self,key,gen=True):
    a=super().get(key)
    if not a:
      a=[]
      if gen:
        self[key]=a
    return a
  def remove_value(self,key,value):
    values=dict.get(self,key,[])
    if value in values:
      values.remove(value)
      self|={key:values}
      return True
    return False
