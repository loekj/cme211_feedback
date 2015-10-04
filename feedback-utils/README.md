# CME211/212 Course Utilities
A collection of useful scripts for feedback file generating.

## How to use
The script will automatically parse extensions .py and .pyc with Python style commenting. Likewise with C style commenting for extensions .h, .hpp, .c, .cpp

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
Try to be consistent with the brackets
Either after a statement or on the newline but don't mix!
CODE:
...
if (*it != "my_str") {
  // do something
}
```

* For Python files, replace // with C&#35;
* the category variable is user defined in the config.yaml file. It must be one of those categories, upper or lower case, If it is not one of the defined catgories, it will prompt the user for input.
* Points deducted is a positive integer. If you just want to write a comment in the generated feedback file use 0 for points deducted
* Each commentline will be a separate comment line in the feedback file. At least one comment line is required.
* A code block is optional. You can leave out //--START. However, //--END is always required!!


## Input
*NOTE:* make sure a branch is created and is switched to that defines our grading branch!!
run the script from the feedback-utils directory as:
```
./python2.7 feedback.py config.yaml [optional : <SUnetID>]
```
The config.yaml file has a 'global' flag. If global is false, a SUnetID must be passed to the feedback file to generate one students' feedback (mainly for your own testing to see if the commenting you did is okay!). Otherwise, if global is true, just leave out the SUnetID argument.
The categories parameter in the config.yaml file can be edited to contain the categories for the assignment that are being graded. After each category add a dash ('-') followed by the total points that can be earned in the assignment.

## Output
The feedback.py file will output a file in the students' corresponding hw directory; the file is called feedback_[SUnetID].txt
If the global flag is true, the script will create a cumulative histogram of the total scores and writes it to /afs/ir/class/cme211/git/figs/
It will also write a file with the student sunets and their scores, in /afs/ir/class/cme211/git/data/

## Remarks: BONUS
If the assignment has a bonus part, you will have to manually add a bonus comment section yourself in one of the files that will be parsed (good style is to write it in the main script that gets executed). The script will search for any comment tags with bonus as category and parses it seperately. E.g. if there's a bonus part add the following, where the positive integer in this case will be added to the total score (instead of deducted):

**template** (C style):
```
//--bonus_5
//--comment line 1
..
//--comment line 4
//--START
relevant code block
//--END
```

## Remarks: WRITEUP
To comment and grade the writeup, create a comment in the main script that gets executed again.

## Remarks: GENERAL
If for each category the points deducted surpasses the maximum points, it will be capped at 0 automatically and produces a warning message to stdout. You can ignore it if you intended to do so.
Note that the script does not take into account how many points can be granted for separate questions in the assignment. If for example question 1 earns you 20 functionality points, and question 2 earns you 30 in the same category, the script can not handle if you deducted more than 20 points for question 1 specifically. You have to take care of this yourself! So becareful! :)
