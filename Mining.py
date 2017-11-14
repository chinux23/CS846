import subprocess
import json
import time

MAXIMUM_DEPTH = 6
# This file generates the data set for statistically analysis

def _loadProcess(commandline):
    # print("Starting a process \n \t {}".format(commandline))
    p = subprocess.Popen(commandline, shell=True)
    return p

def wait_for_proc_complete(proc, timeout=600):
    i = 0
    return_code = None
    while (proc.poll() is None):
        time.sleep(0.1)
        i += 1
        if i > timeout:
            break

def _GumTreeDiffFiles():
    # launch GumTree and output the information as json
    diff_string = subprocess.check_output(["./GumTree/gumtree", "jsondiff", "b_blob.java", "a_blob.java"])

    # load the json
    diff = json.loads(diff_string)

    # filter only insert
    changes = [ action for action in diff["actions"] if action["action"] == 'insert']

    return changes

def _seperateContextAndTarget(changes, num_of_change_context=6):
    size = len(changes)
    midpoint = size / 2

    # find the method invocation at the midpoint
    i = midpoint
    while i < size:
        if changes[i]["type"] == 32: # method invocation
            print i
            break
        i += 1

    # find the 2nd SimpleName node, that's the method name
    assert(changes[i+1]["type"] == 43)
    assert(changes[i+2]["type"] == 42)
    assert(changes[i+3]["type"] == 42)
    target = changes[i+3]

    X = num_of_change_context
    # Generate (previous) X change context 
    if i + 3 - X < 0:
        print("Not enough change context")
        change_contexts = []
    else:
        change_contexts = [ changes[i+3-j-1] for j in range(X)]

    return (target, change_contexts)

def GumTreeDiff(base_blob, target_blob):
    '''
    This function takes two files (same file from different commit) from the Git,
    and produce a target atomic change, along with its change_context.

    TODO: Add Scope information (in scope or out of scope)

        param base_blob:    base file where the change is made to
        param target_blob:  the resulting file after the change is made.

        return: target, change_context, and code_context
    '''

    # output diff java files.
    with open("a_blob.java", "wb") as f:
        f.write(target_blob.data_stream.read())
    
    with open("b_blob.java", "wb") as f:
        f.write(base_blob.data_stream.read())

    # Change Context
    changes = _GumTreeDiffFiles()
    target, change_context = _seperateContextAndTarget(changes, MAXIMUM_DEPTH)

    # Code Context
    ast = _ParseFileIntoAST()


def _ParseFileIntoAST():
    '''
    Return AST as json
    '''

    # launch GumTree and output the information as json
    output = subprocess.check_output(["./GumTree/gumtree", "parse", "a_blob.java"])
    ast = json.loads(output)

    return ast



