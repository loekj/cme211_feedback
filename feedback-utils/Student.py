import os

from StringStream import StringStream

class Student(object):
  def __init__(self, sunet, git, repo_path, hw, points_dict):
    self.sunet = sunet
    self.git = git
    self.filename = 'feedback_{0}.txt'.format(sunet)
    self.filestring = StringStream()
    self.path = os.path.join(repo_path, '{0}-submit'.format(git), hw)
    self.bonus = -1
    self.points = points_dict
    self.total_score = 0

  def setScore(self, cat_map, ta):
    for cat, val in self.points.iteritems():
      self.write('{0:<18}{1:>15}\n'.format(cat.upper()+':', str(val)+'/'+str(cat_map[cat])))
      self.total_score += val
    
    # Write Bonus
    if self.bonus != -1:
      self.write('{0:<18}{1:>15}\n\n'.format('BONUS:', '+'+str(self.bonus)))
      self.total_score += self.bonus

    self.write('\n{0:<18}{1:>15}\n{2}\n'.format('GRADING TA:', ta, ''.join(['#']*33)))        
    self.write('{0:<18}{1:>15}\n{2}\n'.format('TOTAL POINTS:',self.total_score, ''.join(['#']*33) ))

  def getFilename(self):
    return self.filename

  def getPath(self):
    return self.path

  def addBonus(self, points):
    if self.bonus == -1:
      self.bonus = 0
    self.bonus += points

  def getBonus(self):
    return self.bonus

  def getGit(self):
    return self.git

  def subtract(self, cat, points):
    self.points[cat] -= points

  def subtractAll(self):
    self.points = dict( [(cat, 0) for cat, points in self.points.iteritems()] )

  def write(self, string_obj):
    self.filestring.write(string_obj)

  def saveFile(self):
    with open(os.path.join(self.path, self.filename), 'w') as f:
      f.write(str(self.filestring))

  def getSunet(self):
    return self.sunet

  def getScore(self):
    return self.total_score  

  def getPoints(self):
    return self.points

  def capPoints(self):
    if any(val < 0 for val in self.points.values()):
      print('WARNING: For {0} ({1}-submit), deducted too many points for categorie(s). Capping at 0...'.format(self.sunet, self.git))
      self.points = dict([(cat, val) if val >= 0 else (cat, 0) for cat, val in self.points.iteritems()])
