import subprocess
import json
import time
from collections import deque
import os


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

    # sort the changes based on position
    changes = sorted(changes, key= lambda change: change["pos"])

    return changes

def _seperateContextAndTarget(changes, num_of_change_context=6):
    size = len(changes)
    midpoint = size / 2

    # find the method invocation at the midpoint
    i = midpoint
    while i < size:
        if changes[i]["type"] == 42 and changes[i]["parent type"] == 32 and changes[i]["at"] == 1:
            print i
            break
        i += 1

    # that's the method name
    target = changes[i]

    X = num_of_change_context
    # Generate (previous) X change context 
    if i - X < 0:
        print("Not enough change context")
        change_contexts = []
    else:
        change_contexts = [ changes[i-X+j-1] for j in range(X)]

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
        if (base_blob): # in case there is no base file.
            f.write(base_blob.data_stream.read())

    # Change Context
    changes = _GumTreeDiffFiles()
    target, change_context = _seperateContextAndTarget(changes, MAXIMUM_DEPTH)

    # Code Context
    ast = _ParseFileIntoAST()
    token_context = _getNearbyTokens(target)

    # annoate change context with token id
    change_context = _annoate_change_context(ast, change_context)

    return [target, change_context, token_context]


def _ParseFileIntoAST():
    '''
    Return AST as json
    '''

    # launch GumTree and output the information as json
    output = subprocess.check_output(["./GumTree/gumtree", "parse", "a_blob.java"])
    ast = json.loads(output)

    return ast

def _getNearbyTokens(target):
    '''
    Return Nearby Tokens

    Have an option to annotate the change_context with token_id.

    If change_context is empty list, no annotation will be done.
    '''
    # location of the target
    target_loc = target["pos"]

    # get AST
    ast = _ParseFileIntoAST() # in a format of json

    # Perform DFS Search
    token_context = _pre_order_traverse(ast, target_loc)

    return token_context

def _annoate_change_context(jsonfile, change_context):
    # count the tokens
    token_count = 0

    stack = [jsonfile["root"]]
    # We are looking for simple names
    while len(stack) != 0:
        node = stack.pop()
        childrens = node["children"]

        # annoate change context
        for change in change_context:
            if change["id"] == node["id"]:
                change["token_id"] = token_count

        # Visit the node: check type
        if node["typeLabel"] == "SimpleName":
            token_count += 1

        # check if there is any children needs to add to the stack
        while len(childrens) != 0:
            stack.append(childrens.pop())

    return change_context

def _pre_order_traverse(jsonfile, target_loc):
    # create a FIFO queue to store result
    token_context = deque([], MAXIMUM_DEPTH)

    token_count = 0

    stack = [jsonfile["root"]]
    # We are looking for simple names
    while len(stack) != 0:
        node = stack.pop()
        childrens = node["children"]

        # Visit the node: check type
        if node["typeLabel"] == "SimpleName":
            token_count += 1

            # found the method name
            if int(node["pos"]) == int(target_loc):
                break
            else:
                # Add the token
                token_context.append({
                    "type": node["type"],
                    "typeLabel": node["typeLabel"],
                    "pos": node["pos"],
                    "label": node["label"],
                    "length": node["length"],
                    "token_id": token_count
                })

        # check if there is any children needs to add to the stack
        while len(childrens) != 0:
            stack.append(childrens.pop())

    return token_context

def iterateAllRepo():
    pass

def iterateAllCommits():
    pass

def diffCommits(base_commit, commit):
    """
    base_commit and commit must be commit object from GitPython Library.
    """
    diffs = commit.tree.diff(base_commit.tree)

    for diff in diffs:
        result = getContextFromDiff(diff)
        if result is None:
            continue

        target, change_context, code_context = result

        # TODO: iterate atomic change combination


def _computeWeights(c1, c2):
    """
    Compute Scope and Data Dependency between C1 and C2
    C1 and C2 are atomic change
    """

    # Calculate W_scope and Calculate W_dep
    if c1["immediate scope"] == c2["immediate scope"]:
        # in the same scope
        w_scope = 1
        if c1["dependant id"] == c1["dependant id"]:
            # same data dependency
            w_dep = 1
        else:
            # different data dependency
            w_dep = 0.5
    else:
        # different scope
        w_scope = 0.5
        w_dep = 0.5

    return (w_scope, w_dep)


def getContextFromDiff(diff):
    """
    a_blob is the new commit

    b_blob is the base

    This function does a bounch of error checking.

    if a_file is None, there is nothing to do. a_file is removed

    if a_file is not None, check the extension. Only proceed if it's java.

    if b_file is None, b_file is empty, a_file is a newly created. Go directly to GumTreeDiff
    
    if b_file is not None, check b_file extension, and only proceed if it's java.

    """
    if diff.a_path is None:
        # this commit removed a file? we don't care.
        return None
    # is this file extension ends with java?
    _, file_extension = os.path.splitext(diff.a_path)
    if file_extension != '.java':
        return None

    if diff.b_path is not None:
        _, file_extension = os.path.splitext(diff.b_path)
        if file_extension != '.java':
            return None
    
    return GumTreeDiff(diff.b_blob, diff.a_blob)


