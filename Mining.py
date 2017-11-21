import subprocess
import json
import time
from collections import deque
import os

Ci_Database = {}
C_Ci_Database = {}
P_list = set()
Ci_Accumulated_Weights = {}
Ci_Accumulated_Distance = {}

C_token_Database = {}
token_Database = {}
token_Accumulated_Weights = {}
token_Accumulated_Distance = {}

Keywords_Statement =set([
    "AssertStatement", 
    "ContinueStatement",
    "DoStatement",
    "EnhancedForStatement",
    "ForStatement",
    "IfStatement",
    "LabeledStatement",
    "ReturnStatement",
    "SwitchStatement",
    "SynchronizedStatement",
    "ThrowStatement",
    "TryStatement",
    "WhileStatement"
])


# This is the change context or code context size that is most cost effective.
MAXIMUM_DEPTH = 15

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
            break
        i += 1
    else:
        # There is no method invocation.
        if i == size:
            return None

    # that's the method name
    target = changes[i]

    X = num_of_change_context
    # Generate (previous) X change context 
    if i - X < 0:
        print("Not enough change context")
        change_contexts = []
    else:
        change_contexts = [ changes[i-X+j] for j in range(X)]

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
    result = _seperateContextAndTarget(changes, MAXIMUM_DEPTH)

    if result is None:
        return None
    else:
        target, change_context = result

    # Code Context
    ast = _ParseFileIntoAST()
    token_context = _getNearbyTokens(target)

    # annoate change context with token id
    target, change_context = _annoate_change_context(ast, change_context, target)

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

def _get_token(node):
    """
    decide whether node is a token or not.
    
    The paper did not explain what defines to be a token.
    We use the following definition to approximate according to the example given in the paper.

    1. keywords
    2. Simple names
    3. Primitive type

    return <Token, Type, Label> as a tuple
    """
    global Keywords_Statement

    if node["typeLabel"] in Keywords_Statement:
        return ("Token", node["type"], "")
        
    if node["type"] == 83:    # Modifier
        return ("Token", node["type"], node["label"])

    if node["type"] == 39:     # Primitive Type
        return ("Token", node["type"], node["label"])

    if node["type"] == 42:    # Simple Names
        return ("Token", node["parent type"], node["label"])

    return None

def _annoate_change_context(jsonfile, change_context, target):
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

        if node["id"] == target["id"]:
            target["token_id"] = token_count

        # Visit the node: check type
        token = _get_token(node)
        if token:
            token_count += 1

        # check if there is any children needs to add to the stack
        while len(childrens) != 0:
            stack.append(childrens.pop())

    return (target, change_context)

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
        token = _get_token(node)
        if token:
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
                    "id": node["id"],
                    "dependent id": node["dependant id"],
                    "immediate scope": node["immediate scope"],
                    "parent type": node["parent type"],
                    "parent label": node["parent label"],
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

        update_database(target, change_context, code_context)

def update_database(target, change_context, code_context):
    global Ci_Database
    global C_Ci_Database
    global P_list
    global Ci_Accumulated_Weights
    global Ci_Accumulated_Distance

    global C_token_Database
    global token_Database
    global token_Accumulated_Weights
    global token_Accumulated_Distance

    target_change = atmoic_change(target)

    try:
        Ci_Database[target_change] += 1
    except:
        Ci_Database[target_change] = 1

    P_list.add(target_change)

    for change in change_context:
        atomicChange = atmoic_change(change)
        c_ci = target_change + atomicChange

        try:
            Ci_Database[atomicChange] += 1
        except:
            Ci_Database[atomicChange] = 1

        try:
            C_Ci_Database[c_ci] += 1
        except:
            C_Ci_Database[c_ci] = 1

        w_scope, w_dep = _computeWeights(target, change)
        try:
            Ci_Accumulated_Weights[c_ci] += w_scope * w_dep
        except:
            Ci_Accumulated_Weights[c_ci] = w_scope * w_dep
        
        try:
            Ci_Accumulated_Distance[c_ci] += target["token_id"] - change["token_id"]
        except:
            Ci_Accumulated_Distance[c_ci] = target["token_id"] - change["token_id"]

    # update code context 
    for context in code_context:
        token = _get_token(context)
        c_token = target_change + token

        try:
            token_Database[token] += 1
        except:
            token_Database[token] = 1

        try:
            C_token_Database[c_token] += 1
        except:
            C_token_Database[c_token] = 1

        w_scope, w_dep = _computeWeights(target, context)
        try:
            token_Accumulated_Weights[c_token] += w_scope * w_dep
        except:
            token_Accumulated_Weights[c_token] = w_scope * w_dep
        
        try:
            token_Accumulated_Distance[c_token] += target["token_id"] - context["token_id"]
        except:
            token_Accumulated_Distance[c_token] = target["token_id"] - context["token_id"]


def atmoic_change(json):
    atomic_change = (json["action"], json["type"], json["label"])
    return atomic_change

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
    if diff.a_path is None or diff.a_blob is None:
        # this commit removed a file? we don't care.
        return None
    # is this file extension ends with java?
    _, file_extension = os.path.splitext(diff.a_path)
    if file_extension != '.java':
        return None

    if diff.b_path is not None or diff.b_blob is None:
        _, file_extension = os.path.splitext(diff.b_path)
        if file_extension != '.java':
            return None
    
    return GumTreeDiff(diff.b_blob, diff.a_blob)


if __name__ == "__main__":
    # Locate the repository and go through all commits

    # save the database into a file.

    pass
