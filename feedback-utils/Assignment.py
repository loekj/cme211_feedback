import copy
import os
import matplotlib
import utils
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from Student import Student

class Assignment(object):
  def __init__(self, category_map, ta_dict, student_git_map, hw_directory, repository_path):
    self.category_map = category_map
    self.cat_list = category_map.keys()
    self.student_git_map = student_git_map
    self.ta_dict = ta_dict
    self.students = []
    self.hw_dir = hw_directory
    self.repo_path = repository_path
    self.skip_files = []
    self.skip_ext = []
    self.git_root = self.setGitRoot()
    self.ta_scores_list = []

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

  def checkStudentsExists(self):
    for sunet, git in self.student_git_map.iteritems():
      if not os.path.exists('{0}-submit'.format(os.path.join(self.repo_path, git))):
        print('Warning! {0} with repo {1}-submit/ does not seem to exist!'.format(sunet, git))
    print('\n')

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



  def getScoresPerTa(self):
    ta_scores_dict = dict( [ (ta, map(lambda y: y.getPoints(), map(lambda x: self.getStudent(x), ta_list) ) ) for ta, ta_list in self.ta_dict.iteritems() ] ) 
    self.ta_scores_list = []
    for ta, points_list in ta_scores_dict.iteritems():
        self.ta_scores_list.append( (ta, [ [ points_dict[cat] for cat in self.cat_list] for points_dict in points_list]) )

  def writeTADistr(self):
    ta_scores_dict = dict( [ (ta, map(lambda y: (y[0], y[1].getPoints()), map(lambda x: (x, self.getStudent(x)), ta_list) ) ) for ta, ta_list in self.ta_dict.iteritems() ] ) 
    with open('{0}{1}/{2}/{3}'.format(self.git_root,'data',self.hw_dir.replace('/',''), 'TaScoresDistr.txt'), 'w') as f:
      for ta, student in ta_scores_dict.iteritems():
        for sunet_id, student_points in student:
          points_string = ','.join( ['{0}-{1}/{2}'.format(cat, str(points), str(self.category_map[cat])) for cat, points in student_points.iteritems()] )
          f.write('{0},{1},{2}\n'.format(ta, sunet_id, points_string))

  def plotTADistr(self):
    self.getScoresPerTa()
    students_mean_std = map(lambda x: ( x[0], utils.sampleStd( [sum(student) for student in x[1]] ),iter([utils.mean(cat) for cat in zip(*x[1]) ])) ), self.ta_scores_list)

    idx = range(len(self.ta_scores_list))
    width = float(2)/len(self.ta_scores_list)

    plt.figure()
    color_list = iter(['b','c','g','y','r','m'])      
    bar_list = [ plt.bar(idx, map(lambda x: x[2][ii], students_mean_std), width, color = color_iter.next(), bottom = map(lambda x: sum(x[2][:ii]), students_mean_std) ) ] 
    bar_list.append( plt.bar(idx, map(lambda x: x[2][-1], students_mean_std), width, color = color_iter.next(), bottom = map(lambda x: sum(x[2][:-1]), students_mean_std) ) )        

    plt.xticks(map(lambda x: x + (width / float(2)), idx), map(lambda x: x[0], students_mean_std))
    plt.title('Score Distr. Per TA {0}'.format(self.hw_dir.replace('/','')))
    plt.ylabel('Mean Scores')
    plt.legend( map(lambda x: x[0], bar_list), cat_list )
    save_dir = '{0}{1}/{2}/'.format(self.git_root,'figs',self.hw_dir.replace('/',''))
    plt.savefig(save_dir+'TaScoresDistr.png')

    
