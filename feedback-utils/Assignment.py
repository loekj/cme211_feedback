import copy
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from Student import Student

class Assignment(object):
  def __init__(self, category_map, student_git_map, hw_directory, repository_path):
    self.category_map = category_map
    self.student_git_map = student_git_map
    self.students = []
    self.hw_dir = hw_directory
    self.repo_path = repository_path
    self.skip_files = []
    self.skip_ext = []
    self.git_root = self.setGitRoot();

  def getCatMap(self):
    return self.category_map

  def createStudents(self):
    self.students = [Student(sunet, git, self.repo_path, self.hw_dir, copy.deepcopy(self.category_map)) \
                        for sunet, git in self.student_git_map.iteritems()]

  def getStudents(self):
    return self.students

  def getStudent(self, sunet):
    try:
      single_student = [student for student in self.students if student.getSunet() == sunet][0]
    except IndexError:
      print('SUnetID not known!')
    else:
      return single_student

  def getDir(self):
    return self.hw_dir

  def getRepoPath(self):
    return self.repo_path

  def skipFile(self, filename):
    self.skip_files.append(filename)

  def skipExt(self, extension):
    self.skip_ext.append(extension)  

  def getSkipExts(self):
    return self.skip_ext
  
  def getSkipFiles(self):
    return self.skip_files 

  def setGitRoot(self):
    root_dir = self.repo_path
    if root_dir.endswith('/'):
      root_dir = root_dir[:-1]
    root = os.path.split(root_dir)[0]+'/'
    if not root.endswith('git/'):
      print('Can\'t find root directory of AFS cme211/git/. Repos dir must be one level up from this')
    return root

  def plotScoresDistr(self):
    total_scores = [int(student.getScore()) for student in self.students]
    plt.figure()
    plt.hist(total_scores, bins = len(total_scores), cumulative=True)
    plt.title('Cumul. Distr. {0}'.format(self.hw_dir.replace('/','')))
    plt.xlabel('Points')
    plt.ylabel('Students')
    save_dir = '{0}{1}/{2}/'.format(self.git_root,'figs',self.hw_dir.replace('/',''))
    plt.savefig(save_dir+'ScoresDistr.png')

  def writeScoresToFile(self):
    with open('{0}{1}/{2}/{3}'.format(self.git_root,'data',self.hw_dir.replace('/',''),'Scores.txt'), 'w') as f:
      for student in self.students:
        f.write('{0}: {1}\n'.format(student.getSunet(), student.getScore()))


