import os
import sys
import yaml
import re
import copy

from Student import Student
from Assignment import Assignment


PY_EXT = ['py']
C_EXT = ['h', 'hpp', 'c', 'cpp']

RE_CAT = '{0}--([a-zA-Z]+)_(\d{{1,2}})'
RE_PATTERN = '^\s*' + RE_CAT + '(.*?){0}--END'
RE_BONUS_PATTERN = '^\s*{0}--(?:bonus|BONUS)_(\d{{1,2}})(.*?){0}--END'
RE_NOTSUBM_PATTERN = '^\s*{0}--(notsubmitted|NOTSUBMITTED)'


def regexNotSubmitted(re_notsubm_pattern, file_content):
  if re.search(re_notsubm_pattern, file_content) is not None:
    return False
  return True

def regexBonus(assignment, student, re_bonus_pattern, file_content, file_name, comment_style):
  m = re.search(re_bonus_pattern, file_content)
  if m is not None:
    points = int(m.group(1))
    comments = m.group(2)
    has_code = True
    if not comment_style+'--START' in comments:
      has_code = False
    else:
      try:
        comments, code_block = comments.split(comment_style+'--START')
      except ValueError as e:
        print('ERROR: Wrong syntax block, splitting on --START is wrong in file {0}'.format(file_name))
        print(comments)
        sys.exit(1)
    comments = [line.strip()[3:].strip() for line in comments.split('\n') if line.strip() != '' and line.strip().startswith(comment_style+'--')]
    comments = ['-'+line.strip() if not line.strip().startswith('-') else line.strip() for line in comments]
    if has_code:
      student.write('{0:<15}{1}\n{2:<15}{3}\n\nCOMMENTS:\n{4}\n\nRELEVANT CODE:\n{5}\n\n\n\n--------------------------\n'.format('FILE:',file_name, 'BONUS', '+'+str(points),('\n').join(comments),code_block.strip()))
    else:
      student.write('{0:<15}{1}\n{2:<15}{3}\n\nCOMMENTS:\n{4}\n\n\n\n--------------------------\n'.format('FILE:',file_name, 'BONUS', '+'+str(points), ('\n').join(comments)))
    student.addBonus(points)
    return True
  return False

def regexCategories(assignment, student, re_category_block_pattern, re_category_pattern, file_content, file_name, comment_style):
  cat_regex_found = False
  m = re.findall(re_category_block_pattern, file_content)
  if m is not None and len(m) != 0:
    for comment in m:
      cat = comment[0].strip().lower()
      points = int(comment[1].strip())

      has_code = True
      if not comment_style+'--START' in comment[2]:
        comments = comment[2]
        has_code = False
      else:
        m = re.search(re_category_pattern, comment[2])
        if m:
          while True:
            inp = raw_input('\tWARNING: Suspicious pattern found in comment block in file {0} Check file! Continue? y/n: '.format(file_name))
            if inp == 'y':
              break
            elif inp == 'n':
              sys.exit(1)
        try:
          comments, code_block = comment[2].split(comment_style+'--START')
        except ValueError as e:
          print('ERROR: Wrong syntax block, splitting on --START is wrong in file {0}'.format(file_name))
          print(comments)
          sys.exit(1)          
      comments = [line.strip()[3:].strip() for line in comments.split('\n') if line.strip() != '' and line.strip().startswith(comment_style+'--')]
      comments = ['-'+line.strip() if not line.strip().startswith('-') else line.strip() for line in comments]
      cat_list = assignment.getCatMap().keys()
      if cat.lower() != 'bonus' and cat not in cat_list:
        while(True):
          cat_in = raw_input('\tCategory \'{0}\' unknown, type one of the categories: \n\t{1}:\n\t'.format(cat, " ".join(cat_list)))
          if cat_in.strip() in cat_list:
            cat = cat_in.strip()
            break
      if cat.lower() != 'bonus':
        if has_code:
          student.write('{0:<15}{1}\n{2:<15}{3}\n\nCOMMENTS:\n{4}\n\nRELEVANT CODE:\n{5}\n\n\n\n--------------------------\n'.format('FILE:',file_name, cat.upper(),'-'+str(points), ('\n').join(comments),code_block.strip()))
        else:
          student.write('{0:<15}{1}\n{2:<15}{3}\n\nCOMMENTS:\n{4}\n\n\n\n--------------------------\n'.format('FILE:',file_name, cat.upper(),'-'+str(points), ('\n').join(comments)))
        student.subtract(cat, points)
        cat_regex_found = True
  return cat_regex_found



def parseFile(root, file_name, assignment, student, is_python):  
  path = os.path.join(root, file_name)
  with open(path) as f:
    file_content = f.read() # in-memory, to use regex findall

  if is_python:
    comment_style = '#'
  else:
    comment_style = '//'

  # compile regex
  re_notsubm_pattern = re.compile(RE_NOTSUBM_PATTERN.format(comment_style))
  re_category_pattern = re.compile(RE_CAT.format(comment_style))
  re_category_block_pattern = re.compile(RE_PATTERN.format(comment_style), flags = re.MULTILINE | re.DOTALL )
  re_bonus_pattern = re.compile(RE_BONUS_PATTERN.format(comment_style), flags = re.MULTILINE | re.DOTALL )    

  # check for not submitted flag
  if not regexNotSubmitted(re_notsubm_pattern, file_content):
    print('\tNot submitted flag found for {0} ({1}-submit) in file {2}'.format(student.getSunet(), student.getGit(), file_name))
    assignment.addNotSubmitted(student.getSunet())
    student.subtractAll()
    return True

  # check for bonus and add bonus
  has_bonus = regexBonus(assignment, student, re_bonus_pattern, file_content, file_name, comment_style)

  # check for normal subtract categories
  has_deductions = regexCategories(assignment, student, re_category_block_pattern, re_category_pattern, file_content, file_name, comment_style)

  if (not has_bonus) and (not has_deductions):
    return False
  return True


def gradeStudent(assignment, student):
  wrote_to_student = False
  for root, dirnames, filenames in os.walk(student.getPath()):
      for filename in filenames:
        file_extension = filename.lower().split('.')[-1]
        if file_extension in C_EXT:
          if parseFile(root, filename, assignment, student, False):
            wrote_to_student = True
        elif file_extension in PY_EXT:
          if parseFile(root, filename, assignment, student, True):
            wrote_to_student = True

  if not wrote_to_student:
    while True:
      inp = raw_input('\tWARNING: No files parsed or no comments found... set as not submitted? y/n: ')
      if inp == 'y':
        assignment.addNotSubmitted(student.getSunet())
        student.subtractAll()
        break
      elif inp == 'n':
        break


def postProcess(assignment):
    # cap points to nonnegative
    assignment.capPoints()  

    # set score map of students
    assignment.setScores()


def writeToFiles(assignment):
    # checks whether /data/* and /figs/* exists, otherwise creates it
    assignment.checkExistsDirs()
    # save all feedback to repos
    assignment.saveFiles()
    # write files from students who not submitted and not exists
    assignment.writeMissingStudents()
    assignment.writeNotSubmittedStudents()  
    # write score distributions
    assignment.writeScoresToFile()
    assignment.writeTADistr()

def writePlots(assignment):
    assignment.plotScoresDistr()
    assignment.plotTADistr()


def initialize(assignment):  
  # create student objects and store them in assignement object
  assignment.createStudents()

  # check whether students repo path exists, and whether they have submitted (also need manual precheck)
  assignment.checkStudents()


def getParams(config_path):
  try:
    f = open(config_path)
  except:
    print('YAML file {0} could not be opened'.format(config_path))
    return 1
  else:
    params = yaml.load(f)
    f.close()
    return params

def getCatMap(categories):
  # parse categories to dict such that categories: max points are key value pairs
  return dict([ (cat.split('-')[0], int(cat.split('-')[1])) for cat in categories.split(' ')])


def getMaps(map_ta):
  try:
    with open(map_ta) as f:
      map_ta_list = f.readlines()
  except:
    print('File I/O error. Does the file {0} the exist?'.format(map_ta))
    return 1
  ta_dict = dict( [ (ta.strip().split()[-1], []) for ta in map_ta_list] )
  [ ta_dict[line.strip().split()[-1]].append(line.strip().split()[0]) for line in map_ta_list ]
  sunet_to_git = dict( [ (line.strip().split()[0], line.strip().split()[1]) for line in map_ta_list ] )
  return ta_dict, sunet_to_git


def main(argv=sys.argv):
  if len(sys.argv) < 2:
    print ('Usage:\n\t {0} <config file>'.format(sys.argv[0]))
    return 1

  # get params from config file
  params = getParams(sys.argv[1])

  # get config yaml params
  repo_path = params['repo_path']
  hw = params['hw']
  ta_dict, sunet_to_git = getMaps(params['map_ta'])
  root_git = params['root_git']
  cat_map = getCatMap(params['categories'])


  # set-up assignment class with students
  assignment = Assignment(cat_map, ta_dict, sunet_to_git, hw, repo_path, root_git)
  initialize(assignment)

  # loop over students and grade!
  for student in assignment.getStudents():
    if (student.getSunet() in assignment.getNotExists()) or (student.getSunet() in assignment.getNotSubmitted()):
      continue
    print('{0:<20}{1} ({2}-submit)'.format('...student:', student.getSunet(), student.getGit()))
    gradeStudent(assignment, student)
    print('...done!')

  postProcess(assignment)
  writeToFiles(assignment)
  writePlots(assignment)
  
  # print summary to stdout
  assignment.printOutput()


if __name__=='__main__':
  sys.exit(main())
