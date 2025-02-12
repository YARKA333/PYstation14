import yaml
import random
trewoga=False


class TagPlaceholder:
  def __init__(self,loader,node:yaml.MappingNode):
    self.tag=node.tag.replace("!type:","")
    self.value=node.value
  def __call__(self,classes:dict):
    if self.tag in classes:
      try:
      #expected_args=cls.__init__.__code__.co_varnames[1:]


        return classes[self.tag](**mapconstruct(self.value,classes))
      except TypeError as e:
        global trewoga
        trewoga=e
        return None
    else:
      if 0 in classes:
        no=classes[0]
        no[self.tag]=1+no.get(self.tag,0)
      else:
        ...
        #print(f"tag {self.tag} is not defined")
      return None

yaml.CLoader.add_constructor(None,TagPlaceholder)
classdb={1:{}}


def tag(name=None,*args,**kvargs):
  def decorator(cls:type):
    if name is None:
      cls_name=cls.__name__
    else:
      cls_name=name
    classdb[cls_name]=cls
    return cls
  return decorator

def mapconstruct(value,classes:dict):
  return dict([(construct(p[0],classes),construct(p[1],classes)) for p in value])
def construct(node:yaml.Node,classes:dict):
  tag:str=node.tag
  value=node.value
  if tag.startswith("tag:yaml.org,2002:"):
    match tag.replace("tag:yaml.org,2002:",""):
      case "str":return value
      case "int":return int(value)
      case "float":return float(value)
      case "seq":return [construct(n,classes) for n in value]
      case "map":return mapconstruct(value,classes)
      case None:
        print("!!ACHTUNG!!")
        print(tag)
        print("!!ACHTUNG!!")
  else:
    return TagPlaceholder(None,node)(classes)


def retag(data,classes=None):
  if classes is None:classes=classdb
  if isinstance(data,list):
    return [retag(n,classes) for n in data]
  elif isinstance(data,dict):
    d=dict([(k,retag(v,classes)) for k,v in data.items()])
    if trewoga and "id" in d:
      raise Exception(d["id"],trewoga)
    return d
  elif isinstance(data,str|float|int):
    return data
  elif data is None:return None
  elif callable(data):
    return data(classes)
  else:
    print("Unknown data type:")
    print(type(data))
    print(data)


def quick_load(path):
  with open(path,"rt",encoding="UTF-8") as file:
    data=yaml.load(file,yaml.CLoader)
  return retag(data)

@tag("NanotrasenNameGenerator")
class NTNG:
  Prefix="NT"
  SuffixCodes=["LV","NX","EV","QT","PR"]
  def __init__(self,prefixCreator):
    self.PrefixCreator=prefixCreator
  def __call__(self, pattern:str):
    return pattern.format(f"{self.Prefix}{self.PrefixCreator}", f"{random.choice(self.SuffixCodes)}-{random.randint(0, 999):03}")

if __name__=="__main__":
  test_classes={"!type:NanotrasenNameGenerator":NTNG}
  yaml.add_constructor(None,TagPlaceholder)
  with open("C:/Servers/SS14 c2/Resources/Prototypes/Corvax/Maps/maus.yml","r",encoding="UTF-8") as file:
    data_raw=yaml.load(file,yaml.FullLoader)
  print(data_raw)
  test_data=retag(data_raw,test_classes)
  print(test_data)