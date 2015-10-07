import os
import sys
import yaml
import re
import copy

from Student import Student
from Assignment import Assignment


PY_EXT = ('py')
C_EXT = ('h', 'hpp', 'c', 'cpp')

RE_PATTERN = '^\s*{0}--([a-zA-Z]+)_(\d{{1,2}})(.*?){0}--END'
RE_BONUS_PATTERN = '^\s*{0}--(?:bonus|BONUS)_(\d{{1,2}})(.*?){0}--END'


def parseFile(root, file_name, assignment, student, is_python):  
  path = os.path.join(root, file_name)
  with open(path) as f:
    file_content = f.read() # in-memory, to use regex findall

  if is_python:
    comment_style = '#'
  else:
    comment_style = '//'

  re_pattern = re.compile(RE_PATTERN.format(comment_style), flags = re.MULTILINE | re.DOTALL )
  re_bonus_pattern = re.compile(RE_BONUS_PATTERN.format(comment_style), flags = re.MULTILINE | re.DOTALL )
  
  # find bonus, if any
  m = re.search(re_bonus_pattern, file_content)
  if m is not None:
    points = int(m.group(1))
    comments = m.group(2)
    has_code = True
    if not comment_style+'--START' in comments:
      has_code = False
    else:
      comments, code_block = comments.split(comment_style+'--START')
    comments = [line[3:].strip() for line in comments.split('\n') if line.strip() != '' and line.strip().startswith(comment_style+'--')]
    comments = ['-'+line if not line.startswith('-') else line for line in comments]
    if has_code:
      student.write('{0:<15}{1}\n{2:<15}{3}\n{4}\nCODE:\n...\n{5}\n--------------------------\n\n'.format('FILE:',file_name, 'BONUS', '+'+str(points),('\n').join(comments),code_block.strip()))
    else:
      student.write('{0:<15}{1}\n{2:<15}{3}\n{4}\n--------------------------\n\n'.format('FILE:',file_name, 'BONUS', '+'+str(points), ('\n').join(comments)))
    student.addBonus(points)

  m = re.findall(re_pattern, file_content)
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
      comments = [line[3:].strip() for line in comments.split('\n') if line.strip() != '' and line.strip().startswith(comment_style+'--')]
      comments = ['-'+line if not line.startswith('-') else line for line in comments]
      cat_list = assignment.getCatMap().keys()
      if cat.lower() != 'bonus' and cat not in cat_list:
        while(True):
          cat_in = input('Category {0} unknown, type one of the categories: {1}'.format(cat, " ".join(cat_list)))
          if cat_in.strip() in cat_list:
            cat = cat_in.strip()
            break
      if cat.lower() != 'bonus':
        if has_code:
          student.write('{0:<15}{1}\n{2:<15}{3}\n{4}\nCODE:\n...\n{5}--------------------------\n\n'.format('FILE:',file_name, cat.upper(),'-'+str(points), ('\n').join(comments),code_block.strip()))
        else:
          student.write('{0:<15}{1}\n{2:<15}{3}\n{4}\n--------------------------\n\n'.format('FILE:',file_name, cat.upper(),'-'+str(points), ('\n').join(comments)))
        student.subtract(cat, points)



def gradeStudent(assignment, student):
  for root, dirnames, filenames in os.walk(student.getPath()):
      for filename in filenames:
        is_python = None
        if not '.' in filename:
          filename = filename+'.'
        file_extension = filename.lower().split('.')[-1]
        if file_extension in C_EXT:
          is_python = False
        elif file_extension in PY_EXT:
          is_python = True
        elif file_extension in assignment.getSkipExts() or filename in assignment.getSkipFiles():
          continue
        else:
          while(is_python is None):
            file_ext = input('Unknown type {0}. \'py\'/\'c\'/\'e\'/\'f\'/\'\': '.format(filename))
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
          parseFile(root, filename, assignment, student, is_python)
  
  # Cap at 0 points maximum assigned
  student.capPoints()
  
  # Set final score and write summary
  student.setScoreWrite(assignment.getCatMap())



def main(argv=sys.argv):
  if len(sys.argv) < 2:
    print ('Usage:\n\t {0} <config file> [optional : <SUnetID>]'.format(sys.argv[0]))
    return 1

  if len(sys.argv) > 2:
    sunet_id = sys.argv[2].strip()

  # open config file
  configfile = sys.argv[1]
  try:
    f = open(configfile)
  except:
    print('YAML file {0} could not be opened'.format(configfile))
    return 1
  else:
    params = yaml.load(f)
    f.close()

  # get config yaml params
  is_global = params['global']
  repo_path = params['repo_path']
  hw_dir = params['hw_dir']
  map_ta = params['map_ta']
  cat_map = dict([ (cat.split('-')[0], int(cat.split('-')[1])) for cat in params['categories'].split(' ')])

  # check if input args valid
  try:
    with open(map_ta) as f:
      map_ta_list = f.readlines()
    except:
      print('File I/O error. Does the file {0} the exist?'.format(map_ta))
      return 1
  ta_dict = dict( [ (ta.strip().split()[-1], []) for ta in map_ta_list] )
  [ ta_dict[line.strip().split()[-1]].append(line.strip().split()[0]) for line in map_ta_list ]
  sunet_to_git = dict( [ (line.strip().split()[0], line.strip().split()[1]) for line in map_ta_list ] )

  if is_global:
    if len(sys.argv) > 2:
      print('Global flag set, but single SUNETid passed')
      return 1    
  elif len(sys.argv) < 3:
    print('Global flag false, but no student repo name arg passed.')
    return 1

  # set-up assignment class with students
  assignment = Assignment(cat_map, ta_dict, sunet_to_git, hw_dir, repo_path)
  assignment.checkStudentsExists()
  assignment.createStudents()


  if not is_global:
    student = assignment.getStudent(sunet_id)
    gradeStudent(assignment, student)
    student.saveFile()
    print('...done! {0} points: {1}/100\n'.format(sunet_id, student.getScore()))
  else:
    for student in assignment.getStudents():
      if not os.path.exists(student.getPath()):
        print('Warning: student repo of {0} does not exists!'.format(student.getSunet()))
        continue
      print('...repo: {0}-submit'.format(student.getGit()))
      gradeStudent(assignment, student)
      student.saveFile() 
      print('...done! {0} points: {1}/100\n'.format(student.getSunet(), student.getScore()))
    assignment.checkExistsDirs()
    assignment.plotScoresDistr()
    assignment.writeScoresToFile()
    assignment.plotTADistr()
    assignment.writeTADistr()
  print('...finished!')


if __name__=='__main__':
  sys.exit(main())