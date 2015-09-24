import os
import sys
import yaml
import re
from collections import defaultdict

"""COMMENT TEMPLATE:

#CATEGORY_DEDUCTION
#--why is it bad line 1
#--why is it bad line 2
#--START
CODE BLOCKS OF student
#--END

"""

# Python/C style comments files, where '' is most likely a makefile
PY_EXT = ('py', '', 'in', 'pyc', 'make')
C_EXT = ('h', 'hpp', 'c', 'cpp')

PY_RE_PATTERN = re.compile('^#--(\d|[a-zA-Z]+)_(\d{1,2})(.*?)#--END', flags = re.MULTILINE | re.DOTALL )
C_RE_PATTERN = re.compile('^//--(\d|[a-zA-Z]+)_(\d{1,2})(.*?)//--END', flags = re.MULTILINE | re.DOTALL )
CAT_MAP = {
          '1'         : 'syntax',
          '2'         : 'style',
          '3'         : 'function',
          '4'         : 'misc',
          }
PCT_MAP = {
          'syntax'    : .1,
          'style'     : .3,
          'function'  : .5,
          'misc'      : .1,
          }

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



def initDict():
  dct = defaultdict(int)
  [dct[field] for field in CAT_MAP.values()]
  return dct


def parseFile(root, file_name, ss, total_deduction, is_python):
  path = os.path.join(root, file_name)
  with open(path) as f:
    file_content = f.read() # in-memory, to use regex findall
  if is_python:
    comment_style = '#'
    m = re.findall(PY_RE_PATTERN, file_content)
  else:
    comment_style = '//'
    m = re.findall(C_RE_PATTERN, file_content)
  if m is not None and len(m) != 0:
    for comment in m:
      cat = comment[0].strip().lower()
      points = int(comment[1].strip())

      has_code = True
      if not comment_style+'--START' in comment[2]:
        print('Warning: no start codon for referencing code block in file {0}'.format(file_name))
        comments = comment[2]
        has_code = False
      else:
        comments, code_block = comment[2].split(comment_style+'--START')
      comments = [line[3:].strip() for line in comments.split('\n') if line.strip() != '' and line.strip().startswith(comment_style+'--')]
      if cat not in CAT_MAP.values():
        cat = CAT_MAP.get(cat,'misc') #default value is misc
      ss.write('{0:<15}{1}\n{2:<15}{3}\n"{4}"\nCODE:\n...{5}\n--------------------------\n\n'.format('FILE:',file_name, 'CATEGORY:',cat, ('\n').join(comments),code_block))
      total_deduction[cat] += points
  return total_deduction
      

def gradeStudent(student_repo_path, ss):
  total_deduction = initDict()
  for root, dirnames, filenames in os.walk(student_repo_path):
      for filename in filenames:
        if not '.' in filename:
          filename = filename+'.'
        file_extension = filename.lower().split('.')[-1]
        if file_extension in C_EXT:
          total_deduction = parseFile(root, filename, ss, total_deduction, is_python = False)
        elif file_extension in PY_EXT:
          total_deduction = parseFile(root, filename, ss, total_deduction, is_python = True)
        else:
          while(True):
            file_ext = input('File ext. {0} unknown. Enter "py"/"c" or blank: '.format(filename))
            if file_ext.strip() == '':
              print('skipping file...')
              break
            if file_ext.strip().lower() == 'py':
              total_deduction = parseFile(root, filename, ss, total_deduction, is_python = True)
              break
            elif file_ext.strip().lower() == 'c':
              total_deduction = parseFile(root, filename, ss, total_deduction, is_python = False)
              break
  
  # Cap at 100 max
  cat_list = total_deduction.keys()
  for category in cat_list:
    if total_deduction[category] > 100:
      total_deduction[category] = 100

  # Calculate final score
  total_score = 0
  for cat, points in total_deduction.iteritems():
    weight = PCT_MAP[cat]
    total_score += weight*(100-points)
    ss.write('{0:<11}{1:>15}{2:>20}\n'.format(cat.upper()+':', str(100-points), 'WEIGHT='+str(weight)))
  ss.write('{0:<11}{1:>15}'.format('TOTAL POINTS:',total_score))


def saveFile(student_repo_path, ss, file_name):
  with open(os.path.join(student_repo_path, file_name), 'w') as f:
    f.write(str(ss))



def main(argv=sys.argv):
  student_repo_name = None
  if len(sys.argv) < 2:
    print ('Usage:\n\t {0} <config file> [optional] <student git name>'.format(sys.argv[0]))
    return 1
  elif len(sys.argv) > 2:
    student_repo_name = '{0}-submit'.format(sys.argv[2])

  configfile = sys.argv[1]
  try:
    f = open(configfile)
  except:
    print('YAML file {0} could not be opened'.format(configfile))
    return 1
  else:
    params = yaml.load(f)
    f.close()

  is_global = params['global']
  repo_path = params['repo_path']
  root_path = params['root_path']
  file_name = params['file_name']
  students = params['roster']
  print(os.path.join(root_path,students))
  if is_global:
    try:
      students = open(os.path.join(root_path,students))
    except:
      print('File I/O error. Is the file {0} in the correct dir?'.format(students))
      if student_repo_name is not None:
        print('Writing feedback for one student\'s only...\n')
      is_global = False
  elif student_repo_name is None:
    print('One students\' repo feedback generation, but no student\'s repo name arg passed.')
    return 1


  if not is_global:
    ss = StringStream()
    print('...repo: {0}'.format(student_repo_name))
    student_repo_path = os.path.join(repo_path, student_repo_name)
    gradeStudent(student_repo_path, ss)
    saveFile(student_repo_path, ss, file_name)
  else:
    for student in students:
      student = student.strip()
      print('...repo: {0}'.format(student))
      ss = StringStream()
      student_repo_path = os.path.join(repo_path, student+'-submit')
      gradeStudent(student_repo_path, ss)
      saveFile(student_repo_path, ss, file_name) 
      print('...done!')     
  print('...finished!')



if __name__=='__main__':
  sys.exit(main())