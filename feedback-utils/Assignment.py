import copy
import os, sys
import matplotlib
import utils
import glob
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from Student import Student
from StringStream import StringStream


class Assignment(object):
  def __init__(self, category_map, ta_dict, student_git_map, hw, repository_path, root_git, min_files):
    self.category_map = category_map
    self.cat_list = category_map.keys()
    self.student_git_map = student_git_map
    self.ta_dict = ta_dict
    self.students = []
    self.hw = hw.replace('/','')
    self.repo_path = repository_path
    self.skip_files = []
    self.skip_ext = []
    self.git_root = root_git
    self.min_files = min_files

    # contains only students' scores > 0 for plotting purposes
    self.ta_scores_list = []
    
    self.notExists = []
    self.notSubmitted = []

  def getCatMap(self):
    return self.category_map

  def getMinFiles(self):
    return self.min_files

  def createStudents(self):
    self.students = [Student(sunet, git, self.repo_path, self.hw, copy.deepcopy(self.category_map)) \
                        for sunet, git in self.student_git_map.iteritems()]

  def getNotExists(self):
    return self.notExists

  def getNotSubmitted(self):
    return self.notSubmitted

  def getStudents(self):
    return self.students

  def getStudent(self, sunet):
    try:
      single_student = [student for student in self.students if student.getSunet() == sunet][0]
    except IndexError:
      print('SUnetID not known!')
    else:
      return single_student

  def addNotSubmitted(self, sunet):
    self.notSubmitted.append(sunet)

  def skipFile(self, filename):
    self.skip_files.append(filename)

  def skipExt(self, extension):
    self.skip_ext.append(extension)  

  def getSkipExts(self):
    return self.skip_ext
  
  def getSkipFiles(self):
    return self.skip_files 

  def checkExistsDirs(self):
    for directory in ['figs', 'data']:
      for hw_dir in ['hw{0}'.format(str(ii)) for ii in range(1,7)]+['project']:
        if not os.path.exists(os.path.join(self.git_root, directory, hw_dir)):
          os.makedirs(os.path.join(self.git_root, directory, hw_dir))
  

  def checkStudents(self):
    ignore_list = ['.DS_Store', '._.DS_Store', '.__afs7786', 'README.md','']
    for student in self.students:
      student_path = student.getPath()
      if not os.path.exists(student_path):
        self.notExists.append(student.getSunet())
        print('{0:<20}{1:<20}{2:<20}'.format('Missing:',student.getSunet(), student.getGit()))
        student.subtractAll()
      else:
        glob_list = glob.glob(os.path.join(student_path, '*'))
        while True:
          try:
            idx_hw = [os.path.split(a)[-1].lower() for a in glob_list].index(self.hw)
          except ValueError:
            break
          else:
            glob_list = glob.glob(os.path.join(glob_list[idx_hw],'*'))
        files = [os.path.split(a)[-1] for a in glob_list]
        ignore_list[-1] = student.getFilename()
        for ignore in ignore_list:
          try:
            files.pop( files.index(ignore) )
          except ValueError:
            pass
        if len(files) == 0:
          print('{0:<20}{1:<20}{2:<20}'.format('Not submitted:',student.getSunet(), student.getGit()))
          self.notSubmitted.append(student.getSunet())
          student.subtractAll()
        elif len(files) <= self.min_files:
          while True:
            input = raw_input('WARNING! {0}, ({1}-submit) only has files \'{2}\'.\nIs this correct? Enter \'n\' to declare as not submitted. Otherwise \'y\': '.format(student.getSunet(), student.getGit(), ', '.join(files)))
            if input.strip() == 'n':
              self.notSubmitted.append(student.getSunet())
              student.subtractAll()
              break
            elif input.strip() == 'y':
              break
    print('\n')

  def setScores(self):
    for student in self.students:
      sunet = student.getSunet()
      ta_list = [ta for ta, sunet_list in self.ta_dict.iteritems() if sunet in sunet_list]
      if len(ta_list) != 1:
        ta = 'Unknown, email staff!'
      else: 
        ta = ta_list[0]
      student.setScore(self.category_map, ta)

  def capPoints(self):
    for student in self.students:
      student.capPoints()

  def saveFiles(self):
    for student in self.students:
      if student.getSunet() not in self.notExists:
        student.saveFile()

  def plotScoresDistr(self):
    total_scores = [int(student.getScore()) for student in self.students]
    plt.figure()
    plt.hist(total_scores, bins = len(total_scores), cumulative=True)
    plt.title('Cumul. Distr. {0}'.format(self.hw))
    plt.xlabel('Points')
    plt.ylabel('Students')
    plt.savefig( os.path.join(self.git_root, 'figs', self.hw, 'ScoresDistr.png') )

  def writeMissingStudents(self):
    with open(os.path.join(self.git_root, 'data', self.hw,'MissingRepos.txt'), 'w') as f:
      f.write('\n'.join(self.notExists))

  def writeNotSubmittedStudents(self):
    with open(os.path.join(self.git_root, 'data', self.hw,'NotSubmittedRepos.txt'), 'w') as f:
      f.write('\n'.join(self.notSubmitted))

  def writeScoresToFile(self):
    with open(os.path.join(self.git_root, 'data', self.hw,'Scores.txt'), 'w') as f:
      for student in self.students:
        f.write('{0}: {1}\n'.format(student.getSunet(), student.getScore()))

  def getScoresPerTa(self):
    ta_scores_dict = {}
    for ta, ta_list in self.ta_dict.iteritems():
      if ta not in ta_scores_dict:
        ta_scores_dict[ta] = []
      for student in ta_list:
        student_obj = self.getStudent(student)
        student_points = student_obj.getPoints()
        if sum(student_points.values()) > 0:
          ta_scores_dict[ta].append(student_points)
    self.ta_scores_list = []
    for ta, points_list in ta_scores_dict.iteritems():
        self.ta_scores_list.append( (ta, [ [ points_dict[cat] for cat in self.cat_list]  for points_dict in points_list]) )

  def writeTADistr(self):
    ta_scores_dict = dict( [ (ta, map(lambda y: (y[0], y[1].getPoints()), map(lambda x: (x, self.getStudent(x)), ta_list) ) ) for ta, ta_list in self.ta_dict.iteritems() ] ) 
    with open(os.path.join(self.git_root, 'data', self.hw, 'TaScoresDistr.txt'), 'w') as f:
      for ta, student in ta_scores_dict.iteritems():
        for sunet_id, student_points in student:
          points_string = ','.join( ['{0}-{1}/{2}'.format(cat, str(points), str(self.category_map[cat])) for cat, points in student_points.iteritems()] )
          if student.getBonus() != -1:
            f.write('{0},{1},{2},bonus-{3}\n'.format(ta, sunet_id, points_string, str(student.getBonus())))
          else:
            f.write('{0},{1},{2}\n'.format(ta, sunet_id, points_string))

  def plotTADistr(self):
    self.getScoresPerTa()
    students_mean_std = map(lambda x: ( x[0], utils.sampleStd( [sum(student) for student in x[1]] ),[utils.mean(cat) for cat in zip(*x[1])] ) , self.ta_scores_list)
    students_mean_std = [tas for tas in students_mean_std if len(tas[2]) != 0]
    idx = range(len([tas for tas in self.ta_scores_list if len(tas[1]) != 0]))
    width = float(2)/len(idx)

    plt.figure()
    color_iter = iter(['b','c','g','y','r','m'])      
    bar_list = [ plt.bar(idx, map(lambda x: x[2][ii], students_mean_std), width, color = color_iter.next(), bottom = map(lambda x: sum(x[2][:ii]), students_mean_std) ) for ii in range(len(self.cat_list)-1) ] 
    bar_list.append( plt.bar(idx, map(lambda x: x[2][-1], students_mean_std), width, color = color_iter.next(), bottom = map(lambda x: sum(x[2][:-1]), students_mean_std), yerr = map(lambda x: x[1], students_mean_std)  ) )
    plt.xticks(map(lambda x: x + (width / float(2)), idx), map(lambda x: x[0], students_mean_std))
    plt.title('Score Distr. Per TA {0}'.format(self.hw))
    plt.ylabel('Mean Scores')
    plt.legend( map(lambda x: x[0], bar_list), self.cat_list )
    plt.savefig( os.path.join(self.git_root, 'figs', self.hw, 'TaScoresDistr.png' ))

    # write the mean and std to file
    ss = StringStream()
    for ta in students_mean_std:
      write_cat = ['{0}-{1:.2f}'.format(self.cat_list[index],mean) for index, mean in enumerate(ta[2])]
      ss.write('{0},{1},mean-{2:.2f},std-{3:.2f}\n'.format(ta[0], ','.join(write_cat), sum(ta[2]), ta[1]) )    
    with open(os.path.join(self.git_root, 'data', self.hw, 'TaScoresMeanStd.txt'), 'w') as f:
      f.write(str(ss))

  def printOutput(self):
    ss = StringStream()
    ss.write('\n{0}\nSUMMARY\n{1}\n'.format(''.join(['#']*63), ''.join(['#']*63)))
    for student in self.students:
      if ( (student.getSunet() not in self.notExists) and (student.getSunet() not in self.notSubmitted) ):
        ss.write('{0:<20}{1:<25}{2:<10}{3:>8}\n'.format(student.getSunet(), student.getGit(),'points:', str(student.getScore()) + '/100'))
    ss.write('{0}\n'.format(''.join(['#']*63)))
    ss.write('{0:<20}{1}/{2}\n'.format('NOT-EXISTED:', len(self.notExists), len(self.students)))
    ss.write('{0:<20}{1}/{2}\n'.format('NOT-SUBMITTED:', len(self.notSubmitted), len(self.students)))
    print(str(ss))

    