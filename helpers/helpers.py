#!/usr/bin/env python

"""
    Miscellaneous helper functions to be imported into the main script
    ~~~~~~
"""

import sys
import subprocess
import os
import time
import ConfigParser
from distutils import spawn

# -------------------------------------

def check_dependencies(required_programs):
    """Check for errors, check dependencies"""

    # required_programs - define required programs in list, e.g., ["java", "samtools", "tabix"]

    for j in required_programs:
        if not spawn.find_executable(j):
            print("[ERROR] Can't find " + j + ". Please add it to your PATH")
            sys.exit(1)

# -------------------------------------

def check_path(myfile):
    """Check for the existence of a file"""

    # expanduser handle tilde
    for f in myfile.split(','):
        if not os.path.isfile(os.path.expanduser(f)):
            print("[ERROR] Can't find the file " + f)
            sys.exit(1)

# -------------------------------------

def check_null(i):
    """Check that value is not None """

    # expects a tuple like this:
    # ('input', args.input)

    if i[1] is None:
        print("[ERROR] " + i[0] + " must not be null")
        sys.exit(1)

# -------------------------------------

def check_file_exists_and_nonzero(myfile):
    """Check for the existence and nonzero-ness of a file"""

    # loop through comma-delimited list of files
    for i in myfile.split(','):
        # if (os.path.isfile(i)):
        if os.path.isfile(os.path.expanduser(i)):
            if os.path.getsize(os.path.expanduser(i)) == 0:
                print(i + " is empty. Exiting")
                sys.exit(1)
        else:
            print("Can't find " + i + ". Exiting.")
            sys.exit(1)

# -------------------------------------

def run_cmd(cmd, bool_verbose, bool_getstdout):
    """Run a system (i.e., shell) command"""

    # if verbose, print command
    if bool_verbose:
        print("[command] " + cmd)

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait() 
    # print return code
    # print(proc.returncode) 
    # print stdout stderr tuple
    # proc.communicate()

    (stdout, stderr) = proc.communicate()

    # if error, print it
    if stderr:
        print("[stderror] " + stderr),

    # return stdout
    if bool_getstdout: 
        return stdout.rstrip()
    else:
        return "0" # note: this must return a str

# -------------------------------------

def mytimer(myfunc):
    """Decorator for timing a function"""
    # http://stackoverflow.com/questions/5478351/python-time-measure-function

    def mynewfunc(*args, **kwargs):
        starttime = time.time()
        myfunc(*args, **kwargs)
        print('[step delta t] {} sec'.format(int(time.time() - starttime)))

    return mynewfunc

# -------------------------------------

def ConfigSectionMap(Config, section):
    """Process config file"""
    # https://wiki.python.org/moin/ConfigParserExamples

    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

# -------------------------------------

def mkdirp(mydir):
    """The loose equivalent of mkdir -p"""

    try:
        os.mkdir(mydir)
    except:
        pass

# -------------------------------------

def fastajoinlines(infile, outfile, idbase):
    """Put all the sequence portions of a fasta file onto a single line"""

    # a counter for entries
    counter = 1
    # a flag
    flag = 0

    with open(outfile, 'w') as f:
        with open(infile, 'r') as g:
            for line in g:
                line = line.rstrip()
                # if id line
                if line[0] == '>':
                    if flag:
                        f.write('\n')
                        counter += 1
                    f.write('>' + idbase + '_' + str(counter) + '\n')
                    flag = 1
                # if sequence line
                else:
                    f.write(line)
        f.write('\n')

    return counter

# -------------------------------------

if __name__ == "__main__":

    pass
