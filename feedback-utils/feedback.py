import os
import sys
import yaml
import re
import copy

from Student import Student
from Assignment import Assignment


PY_EXT = ['py']
C_EXT = ['h', 'hpp', 'c', 'cpp']

# ignoring these extensions
IGNORE_EXT = ['pdf','txt','pyc','md', 'docx', 'doc', 'log'] 



RE_PATTERN = '^\s*{0}--([a-zA-Z]+)_(\d{{1,2}})(.*?){0}--END'
RE_BONUS_PATTERN = '^\s*{0}--(?:bonus|BONUS)_(\d{{1,2}})(.*?){0}--END'
RE_NOTSUBM_PATTERN = '^\s*{0}--(notsubmitted|NOTSUBMITTED)'

def printIgnoreExt():
  global IGNORE_EXT
  IGNORE_EXT = IGNORE_EXT + \
                map(lambda x: x+'#', PY_EXT+C_EXT+IGNORE_EXT) + \
                map(lambda x: x+'~', PY_EXT+C_EXT+IGNORE_EXT) + \
                ['sw'+chr(a) for a in range(107,113)]
  print('\nIgnoring extensions:')
  print(', '.join(IGNORE_EXT + ['.(hidden)'] ))


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
      comments, code_block = comments.split(comment_style+'--START')
    comments = [line.strip()[3:].strip() for line in comments.split('\n') if line.strip() != '' and line.strip().startswith(comment_style+'--')]
    comments = ['-'+line.strip() if not line.strip().startswith('-') else line.strip() for line in comments]
    if has_code:
      student.write('{0:<15}{1}\n{2:<15}{3}\n\nCOMMENTS:\n{4}\n\nRELEVANT CODE:\n{5}\n\n\n\n--------------------------\n'.format('FILE:',file_name, 'BONUS', '+'+str(points),('\n').join(comments),code_block.strip()))
    else:
      student.write('{0:<15}{1}\n{2:<15}{3}\n\nCOMMENTS:\n{4}\n\n\n\n--------------------------\n'.format('FILE:',file_name, 'BONUS', '+'+str(points), ('\n').join(comments)))
    student.addBonus(points)
    return True
  return False

def regexCategories(assignment, student, re_categories_pattern, file_content, file_name, comment_style):
  cat_regex_found = False
  m = re.findall(re_categories_pattern, file_content)
  if m is not None and len(m) != 0:
    for comment in m:
      cat = comment[0].strip().lower()
      points = int(comment[1].strip())

      has_code = True
      if not comment_style+'--START' in comment[2]:
        comments = comment[2]
        has_code = False
      else:
        comments, code_block = comment[2].split(comment_style+'--START')
      comments = [line.strip()[3:].strip() for line in comments.split('\n') if line.strip() != '' and line.strip().startswith(comment_style+'--')]
      comments = ['-'+line.strip() if not line.strip().startswith('-') else line.strip() for line in comments]
      cat_list = assignment.getCatMap().keys()
      if cat.lower() != 'bonus' and cat not in cat_list:
        while(True):
          cat_in = raw_input('\tCategory \'{0}\' unknown, type one of the categories: {1}: '.format(cat, " ".join(cat_list)))
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
  re_categories_pattern = re.compile(RE_PATTERN.format(comment_style), flags = re.MULTILINE | re.DOTALL )
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
  has_deductions = regexCategories(assignment, student, re_categories_pattern, file_content, file_name, comment_style)

  if (not has_bonus) and (not has_deductions):
    return False
  return True


def gradeStudent(assignment, student):
  wrote_to_student = False
  for root, dirnames, filenames in os.walk(student.getPath()):
      for filename in filenames:
        is_python = None
        
        # If ends with . or no . at all, add no extension flag to file
        if not '.' in filename:
          filename = filename+'.NO_EXT'
        elif filename.endswith('.'):
          filename = filename+'NO_EXT'

        file_extension = filename.lower().split('.')[-1]
        if filename.startswith('.') or file_extension in IGNORE_EXT:
          continue

        if file_extension in C_EXT:
          is_python = False
        elif file_extension in PY_EXT:
          is_python = True
        elif file_extension in assignment.getSkipExts() or filename in assignment.getSkipFiles():
          continue

        # unknown extension. Prompt user what to do
        else:
          while(is_python is None):
            file_ext = raw_input('\t{0:<25}{1:<25}\n\t{2:<25}{3:<25}\n\t{4:<25}'.format('File:','...'+filename[max(len(filename)-10,0):], 'Unknown extension:', '.'+file_extension, '\'py\'/\'c\'/\'e\'/\'f\'/\'\':'))
            if file_ext.strip() == '':
              break
            elif file_ext.strip() == 'e':
              assignment.skipExt(filename.split('.')[-1])
              break
            elif file_ext.strip() == 'f':
              assignment.skipFile(filename)
              break              
            elif file_ext.strip().lower() == 'py':
              is_python = True
            elif file_ext.strip().lower() == 'c':
              is_python = False
        if is_python is not None:
          wrote_to_student = parseFile(root, filename, assignment, student, is_python)

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
    # set score map of students
    assignment.setScores()

    # cap points to nonnegative
    assignment.capPoints()  

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
  printIgnoreExt()

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
  min_files = int(params['min_files'])
  cat_map = getCatMap(params['categories'])

  # set-up assignment class with students
  assignment = Assignment(cat_map, ta_dict, sunet_to_git, hw, repo_path, root_git, min_files)
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
