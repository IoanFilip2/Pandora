#!/usr/bin/env python

"""
    Miscellaneous helper functions (shell-related, SGE-related,
    bioinformatics-related) to be imported as needed
    ~~~~~~
"""

import sys
import subprocess
import os
import time
import ConfigParser
from distutils import spawn
from datetime import datetime

# -------------------------------------

### shell-related functions

# -------------------------------------

def mkdirp(mydir):
    """The loose equivalent of mkdir -p"""

    try:
        os.mkdir(mydir)
    except:
        pass

# -------------------------------------

def check_dependencies(required_programs):
    """Check for errors, check dependencies"""

    # required_programs - define required programs in list, e.g., ["java", "samtools", "tabix"]

    for j in required_programs:
        if not spawn.find_executable(j):
            quitwitherror('Can\'t find ' + j + '. Please add it to your PATH')

# -------------------------------------

def check_path(myfile):
    """Check for the existence of a file"""

    # expanduser handle tilde
    for f in myfile.split(','):
        if not os.path.isfile(os.path.expanduser(f)):
            quitwitherror('Can\'t find the file ' + f)

# -------------------------------------

def check_path_bool(myfile):
    """Check for the existence of a file and return a boolean"""

    returnvalue = 1

    # expanduser handle tilde
    for f in myfile.split(','):
        if not os.path.isfile(os.path.expanduser(f)):
            returnvalue = 0

    return returnvalue

# -------------------------------------

def check_null(i):
    """Check that value is not None """

    # expects a tuple like this:
    # ('input', args.input)

    if i[1] is None:
        quitwitherror(i[0] + ' must not be null')

# -------------------------------------

def check_file_exists_and_nonzero(myfile, step=''):
    """Check for the existence and nonzero-ness of a file"""

    # loop through comma-delimited list of files
    for i in myfile.split(','):
        # if (os.path.isfile(i)):
        if os.path.isfile(os.path.expanduser(i)):
            if os.path.getsize(os.path.expanduser(i)) == 0:
                quitwitherror(i + ' is empty. Exiting', step=step)
        else:
            quitwitherror('Can\'t find ' + i + '. Exiting', step=step)

# -------------------------------------

def run_cmd(cmd, bool_verbose, bool_getstdout, step=''):
    """Run a system (i.e., shell) command"""

    # if verbose, print command
    if bool_verbose:
        print('[command] ' + cmd)
        sys.stdout.flush()

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc.wait()

    # print return code if not zero
    if proc.returncode != 0:
        print('[nonzero error code] ' + str(proc.returncode))

    # stdout stderr tuple
    (stdout, stderr) = proc.communicate()

    # if error, print it
    if stderr:
	if step:
            sys.stderr.write('[stderror ' + step + '] ' + stderr)
        else:
            sys.stderr.write('[stderror] ' + stderr)

    # return stdout
    if bool_getstdout: 
        return stdout.rstrip()
    else:
        # note: this must return a str
        return '0'

# -------------------------------------

def run_long_cmd(cmd, bool_verbose, myfile):
    """Run a system command that prints a lot of stuff to stdout or stderr"""

    # https://thraxil.org/users/anders/posts/2008/03/13/Subprocess-Hanging-PIPE-is-your-enemy/

    # "A closer inspection of the subprocess.Popen docs revealed a warning:
    # "Note: The data read is buffered in memory, so do not use this method if the data size is large or unlimited." ...
    # Apparently, that warning actually means "Note: if there's any chance that the data read will be more than a couple pages, 
    # this will deadlock your code." What was happening was that the memory buffer was a fixed size. 
    # When it filled up, it simply stopped letting the child process write to it. 
    # The child would then sit and patiently wait to be able to write the rest of its output.
    # Luckily the solution is fairly simple. Instead of setting stdout and stderr to PIPE, 
    # they need to be given proper file (or unix pipe) objects that will accept a reasonable amount of data."

    # if verbose, print command
    if bool_verbose:
        print('[command] ' + cmd)
        sys.stdout.flush()

    with open(myfile, 'w') as f:
        proc = subprocess.Popen(cmd, shell=True, stdout=f, stderr=f)
        proc.wait()

# -------------------------------------

def run_log_cmd(cmd, bool_verbose, myout, myerr):
    """Run a system command and save stdout and stderr to logs"""

    # if verbose, print command
    if bool_verbose:
        print('[command] ' + cmd)
        sys.stdout.flush()

    with open(myout, 'a') as f:
        with open(myerr, 'a') as g:
            proc = subprocess.Popen(cmd, shell=True, stdout=f, stderr=g)
            proc.wait()

# -------------------------------------

### SGE-related functions

# -------------------------------------

def getjid_deprecated(x):
    """Parse out and return SGE job id from string"""
    # Note: the SGE string must look like this: 'Your job 8379811 ("test") has been submitted'
    return x.split('Your job ')[1].split()[0]

# -------------------------------------

def getjid(x):
    """Parse out and return SGE job id from qsub message"""

    # Note: must be able to accommodate all of the following messages:
    # Your job 9902111 ("echo") has been submitted
    # Your job-array 9902162.1-2:1 ("echo") has been submitted
    # removed environment variable LD_LIBRARY_PATH from submit environment - it is considered a security issue Your job 9902414 ("echo") has been submitted

    jid = ''

    if 'job-array' in x:
        # get the element after 'job-array', which should be job id, and split on '.'
        jid = x.split()[x.split().index('job-array') + 1].split('.')[0]
    elif 'job' in x:
        # get the element after 'job', which should be job id (this condition has to be 2nd b/c 'job' in 'job-array')
        jid = x.split()[x.split().index('job') + 1]
    else:
        quitwitherror('Can\'t parse job id')

    # if the job id is not a proper number
    if not jid.isdigit():
        quitwitherror('Can\'t parse job id (not a digit)')

    return jid

# -------------------------------------

### bioinformatics-related functions

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

    # return the number of entries in the fasta file
    return counter

# -------------------------------------

def fastasplit(infile, filename, cutoff):
    """Split a fasta file to produce a new file per entry such that seq length > cutoff (assume fastajoinlines)"""

    # a counter for entries
    counter = 0
    id = ''

    with open(infile, 'r') as g:
        for line in g:
            line = line.rstrip()
            if line[0] == '>':
                id = line
            elif len(line) > cutoff:
                counter += 1
                with open(filename + '_' + str(counter) + '.fasta', 'w') as f:
                    f.write(id + '\n')
                    f.write(line + '\n')

    # return counter for contigs above threshold length
    return counter

# -------------------------------------

def getorf(infile, outfile, threshold):
    """get ORF (open reading frame)"""

    from Bio.Seq import Seq

    # Find ORFs in a fasta file, borrowing from:
    # http://biopython.org/DIST/docs/tutorial/Tutorial.html#htoc292

    # define amino acid table (see http://www.ncbi.nlm.nih.gov/Taxonomy/Utils/wprintgc.cgi)
    # 1. The Standard Code
    # 2. The Vertebrate Mitochondrial Code
    # 3. The Yeast Mitochondrial Code
    # 4. The Mold, Protozoan, and Coelenterate Mitochondrial Code and the Mycoplasma/Spiroplasma Code
    # etc...
    table = 1 # standard code

    # important: assume the sequence portion of the fasta is all on one line

    with open(infile, 'r') as g:
        with open(outfile, 'w') as f:
            # fasta id
            id = ''
            # ORF counter for a given seq id
            counter = 1
            for line in g:
                # parse fasta
                if line[0] == '>':
                    # grab id
                    id = line.rstrip()[1:].replace(' ', '_')
                    # reset counter
                    counter = 1
                else:
                    # create biopython seq obj
                    myseq = Seq(line.rstrip())
                    # http://biopython.org/DIST/docs/tutorial/Tutorial.html#htoc292
                    for strand, nuc in [(+1, myseq), (-1, myseq.reverse_complement())]:
                        for frame in range(3):
                            # the purpose of this line is get a multiple of three
                            # e.g., 3/3 * 3 = 3 and 4/3 * 3 = 3
                            length = 3 * ((len(myseq)-frame) // 3)
                            # split on the stop codon, a '*' character
                            # don't worry about start codons
                            for pro in nuc[frame:frame+length].translate(table).split('*'):
                                if len(pro) >= int(threshold):
                                    # print fasta entry
                                    f.write('>%s_ORF%i_len%i_strand%i_frame%i\n' % (id, counter, len(pro), strand, frame))
                                    f.write(str(pro) + '\n')
                                    counter += 1

# -------------------------------------

### Misc

# -------------------------------------

def config_section_map(Config, section):
    """Parse a configuration file and return dict"""
    # https://wiki.python.org/moin/ConfigParserExamples

    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
        except:
            print('exception on %s!' % option)
            dict1[option] = None
    return dict1

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

def quitwitherror(message, step=''):
    """Quit the program with an error message"""

    # print('[ERROR] ' + message)
    sys.stderr.write('[ERROR ' + step + '] ' + message + '\n')
    sys.exit(1)

# -------------------------------------

def echostep(step, start=1):
    """Print text to define start or end of a step"""

    if start:
        print('------------------------------------------------------------------')
        print(step.upper() + ' START')
        sys.stderr.write('------------------------------------------------------------------\n')
        sys.stderr.write(step.upper() + ' START\n')
        sys.stderr.write(str(datetime.now()) + '\n')
    else:
        print(step.upper() + ' END')
        print('------------------------------------------------------------------')
        sys.stderr.write(step.upper() + ' END\n')
        sys.stderr.write(str(datetime.now()) + '\n')
        sys.stderr.write('------------------------------------------------------------------\n')

    sys.stdout.flush()

# -------------------------------------

if __name__ == "__main__":

    # to execute as a stand-alone script, give the name of the function 
    # as the first arg, followed by the args to the function
    if sys.argv[1] in globals():
        try:
            globals()[sys.argv[1]](*sys.argv[2:])
	except:
            print('Error! Are you sure you\'re using the correct arguments?')
    else:
        print('Function not found')
