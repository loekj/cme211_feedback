import os
import sys
import yaml
import re

# Comment template: """CATEGORY_POINTSDEDUCTION_DESCRIPTION"""
category_map = {
                '1'         : 'syntax',
                '2'         : 'style',
                '3'         : 'function',
                '4'         : 'misc',
                }

percentage_map = {
                'syntax'    : 10,
                'style'     : 30,
                'function'  : 50,
                'misc'      : 10,
                }

pattern_map = {
                'syntax'    : '1',
                'style'     : '2',
                'function'  : '3',
                'misc'      : '4',
                }
re.compile


def parseFile(path):
  with open(path) as f:
    file_content = f.readlines()



def main(argv=sys.argv):
  one_repo = None
  if len(sys.argv) < 2:
    print ('Usage:\n\t {0} <config file> [optional] <student repo name>'.format(sys.argv[0]))
    return 1
  elif len(sys.argv) > 2:
    student_repo_name = sys.argv[2]  

  configfile = sys.argv[1]
  f = open(configfile)
  params = yaml.load(f)
  f.close()

  is_global = params['global']
  repo_path = params['repo_path']
  file_name = params['file_name']
  roster = params['roster']
  if is_global:
    try:
      students = open(roster)
    except:
      print('File I/O error. Is the file {0} in this dir?'.format(roster))
  elif one_repo is None:
    print('One repo feedback generation mode, but no repo arg passed.')
    return 1


#os.chdir(repo_path)
if not is_global:
  student_repo_path = os.path.join(repo_path, student_repo_name)
  for root, dirnames, filenames in os.walk(student_repo_path):
    for filename in filenames:
      parseFile(os.path.join(root, filename))
else:
  for student in students:
    student = student.strip()
    print('\nWriting feedback file for student {0}'.format(student))
    base_path = '{0}/{1}-submit'.format(repo_path,student)
    file_path = '{0}/{2}'.format(base_path,file_name)






if __name__=='__main__':
  sys.exit(main())