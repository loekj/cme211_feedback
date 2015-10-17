# CME211/212 Course Utilities

A collection of useful scripts for feedback file generating. The script will automatically parse extensions .py and with Python style commenting. Likewise with C style commenting for extensions .h, .hpp, .c, .cpp

## summary (Chronological)
* Initializes student objs stored in assignment obj
* Check if student exists as repo, and checks whether submitted
* Per student checks repo's files. Ignores certain extensions (and their ~, #, and .sw[k-p] temporary file alteregos) by default
* Checks for regex flag 'not submitted', bonus, and category specific. Writes to student object
* After grading, writes results to files and creates plots

## How to use
**template** (C style):
```
//--[category]_[points deducted]
//--comment line 1
..
//--comment line 4
//--START
relevant code block
//--END
```

For example, in a my_script.cpp file I can have the following:<br>
```
//--style_4
//--Try to be consistent with the brackets
//--Either after a statement or on the newline but don't mix!
//--START
if (*it != "my_str") {
  // do something
}
//--END
```

In the outputted feedback file it will put a block like so:
```
FILE:           my_script.cpp
STYLE:          -4

COMMENTS:
-Try to be consistent with the brackets
-Either after a statement or on the newline but don't mix!

CODE:
if (*it != "my_str") {
  // do something
}
```
### NOTES:
* For Python files, replace // with &#35;
* Category can be lower or upper case (and is robust for typos)
* Points deducted is a positive integer. If you just want to write a comment in the generated feedback file use 0 for points deducted
* Each commentline will be a separate comment line in the feedback file. At least one comment line is required.
* A code block is optional. It is triggered by using //--START. You can leave out //--START to not have a code block. But __//--END is always required!!__

## Input
run the script from the feedback-utils directory as:
```
python2.7 feedback.py config.yaml
```
The yaml file is self explanatory, see inside for usage

### NOTES:
* Smake sure a branch is created and is switched to that defines our grading branch!!
* The categories parameter in the config.yaml file can be edited to contain the categories for the assignment. After each category add a dash ('-') followed by the total points that can be earned in the assignment.
* _min\_files_ is a parameter for globbing the repo directories. If e.g. min files = 2, it looks whether there are at least 2 files in the directory (excluding sub directories). If there's less, it prompts the user whether to classify that student as 'not submitted' to deduct all points. (see more in 'Running it' section below)

## Running it
After initialization of the assignment object (containing student objects), it checks whether the students exist as a repo, and whether they have submitted. The latter needs a bit more attention: It goes to the deepest directory in the repo with the corresponding hw name e.g. 'alatimer-submit/hw2/hw2/' if alatimer accidentally has another hw2 directory nested in there. Then, it glob.globs() to check which files are present. The following files are ignored by default:
```'.DS_Store', '._.DS_Store', '.__afs7786', 'README.md',''```
If nothing found it marks the student as 'not submitted'. If the number of files found in the hw2/ directory is less than the yaml parameter _min\_files_ it prompts to stdout for input. 

It globs each students' repo and processes the files. It ignores the following extensions by default (and the temporary files from emacs, vim and text editors appending the file with a tilde (~)):
```'pdf','txt','pyc','md', 'docx', 'doc', 'log', '.' (hidden files)```

Whenever it stumbles upon an unknown extension it will prompt the user to choose one of the following options:

* 'c' for c-style commenting
* 'py' for python-style commenting
* '' for skipping the file only once
* 'e' for skipping all files (globally) with this extension
* 'f' for skipping all files (globally) with the same file name
<<<<<<< HEAD

Then it proceeds to check each file for a 'not submitted' flag denoted by the regex:<br>
```
//--notsubmitted
```
If it finds one of these, it marks the student as not submitted and deducts all points. This is important as sometimes a students pushes something to git that's just total nonsense. We don't want to delete the files, so just put this regex at the top of one of the files.

Then it checks for bonus regex, and the normal category deduction regex. It wraps up with some post processing to checks students' scores (cap at 0), add bonuses, etcetera.

### NOTES:
* Unknown extension prompt answer 'f' can be unstable: It checks file name only, any subdirectories not taken into account! Hence if there's a subdirectory with the same file name it will skip that one too. Be careful!
* A file name without an extension or ending with a dot '.' are appended with a .NO\_EXT flag. Be careful to skip all .NO\_EXT extensions by default. Recommended usage is to just skip them only once.
* _min\_files_ parameter does not include sub directory search as of now. Minimum (main) files in hw2/ directory only are considered.
=======

Then it proceeds to check each file for a 'not submitted' flag denoted by the regex:
```//--notsubmitted```
If it finds one of these, it marks the student as not submitted and deducts all points. This is important as sometimes a students pushes something to git that's just total nonsense. We don't want to delete the files, so just put this regex at the top of one of the files.
>>>>>>> 5788d1bd7949c461228758fca2c6cf7b311daac0

Then it checks for bonus regex, and the normal category deduction regex. It wraps up with some post processing to checks students' scores (cap at 0), add bonuses, etcetera.

### NOTES:
* Unknown extension prompt answer 'f' can be unstable: It checks file name only, any subdirectories not taken into account! Hence if there's a subdirectory with the same file name it will skip that one too. Be careful!
* A file name without an extension or ending with a dot '.' are appended with a .NO\_EXT flag. Be careful to skip all .NO\_EXT extensions by default. Recommended usage is to just skip them only once.
* _min\_files_ parameter does not include sub directory search as of now. Minimum (main) files in hw2/ directory only are considered.


## Output
The feedback.py file will output a file in the students' corresponding hw directory; the file is called feedback_[SUnetID].txt
The script will create cool plots and writes it to /afs/ir/class/cme211/git/figs/
It will also write data files to /afs/ir/class/cme211/git/data/ 

### NOTES:
* The script does not take into account how many points can be granted for separate questions in the assignment. If for example question 1 earns you 20 functionality points, and question 2 earns you 30 in the same category, the script can not handle if you deducted more than 20 points for question 1 specifically. You have to take care of this yourself! So becareful! :)

## Output
The feedback.py file will output a file in the students' corresponding hw directory; the file is called feedback_[SUnetID].txt
The script will create cool plots and writes it to /afs/ir/class/cme211/git/figs/
It will also write data files to /afs/ir/class/cme211/git/data/ 

### NOTES:
* The script does not take into account how many points can be granted for separate questions in the assignment. If for example question 1 earns you 20 functionality points, and question 2 earns you 30 in the same category, the script can not handle if you deducted more than 20 points for question 1 specifically. You have to take care of this yourself! So becareful! :)

## Remarks: BONUS
If the assignment has a bonus part, you will have to manually add a bonus comment section yourself in one of the files that will be parsed (good style is to write it in the main script that gets executed). The script will search for any comment tags with bonus as category and parses it seperately. Just add one bonus regex block. E.g. if there's a bonus part add the following, where the positive integer in this case will be added to the total score (instead of deducted):

**template** (C style):
```
//--bonus_5
//--Awesome job on the bonus! Full 5 points :)
//--Comment 2
//--...
//--Last comment
//--START
relevant code block
//--END
```

## Remarks: WRITEUP
To comment on parts of the writeup and deduct points, create a comment according to the template in the main script that gets executed. Just like you would do with the bonus.
