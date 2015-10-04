# Helper class for string streams
class StringStream(object):
  def __init__(self):
    self.stream = []

  def write(self, string):
    if not isinstance(string, str): #no unicode allowed, just bytestrings
      raise ValueError
    self.stream.append(string)

  def __str__(self):
    return ('').join(self.stream)