import Mining
import os
from collections import Counter
import math
import pickle
import Aggregator
from Queue import PriorityQueue, heapq

In_Vocabulary_Algorithm = True


Ci_Database = {}
C_Ci_Database = {}
P_list = set()
Ci_Accumulated_Weights = {}
Ci_Accumulated_Distance = {}

C_token_Database = {}
token_Database = {}
token_Accumulated_Weights = {}
token_Accumulated_Distance = {}

target_context = []

def load():
    global Ci_Database
    global C_Ci_Database
    global P_list
    global Ci_Accumulated_Weights
    global Ci_Accumulated_Distance

    global C_token_Database
    global token_Database
    global token_Accumulated_Weights
    global token_Accumulated_Distance

    global target_context

    results = Aggregator.load()
    Ci_Database, C_Ci_Database, P_list, Ci_Accumulated_Weights, Ci_Accumulated_Distance, C_token_Database, token_Database, token_Accumulated_Weights, token_Accumulated_Distance, target_context = results
    P_list = set(P_list)
    target_context = filterContext(target_context)

def change_score_transaction(target, change_context):
    score = 0
    for i in range(len(change_context)):
        score += score_change(target, change_context[i], Mining.MAXIMUM_DEPTH - i)
    score = math.exp(score)
    return score

def code_score_transaction(target, code_context):
    score = 0
    for i in range(len(code_context)):
        score += score_code(target, code_context[i], Mining.MAXIMUM_DEPTH - i)
    score = math.exp(score)
    return score

def score_change(target, atomic_change, d):
    global In_Vocabulary_Algorithm
    c = Mining.atmoic_change(target)
    ci = Mining.atmoic_change(atomic_change)
    c_ci = c + ci

    w_scope, w_dep = Mining._computeWeights(target, atomic_change)

    if In_Vocabulary_Algorithm:
        N_c_ci = C_Ci_Database.get(c_ci, 0)
        N_ci = Ci_Database.get(ci, 0)

        log_score = math.log((N_c_ci * 1.0 + 1) / (N_ci + 1)) * w_scope * w_dep / d

    else:
        N_c_ci = C_Ci_Database.get(c_ci, 1)
        N_ci = Ci_Database.get(ci, 1)

        if N_ci != 1:
            log_score = math.log(N_c_ci * 1.0 / N_ci + 1) * w_scope * w_dep / d
        else:
            log_score = math.log(N_c_ci * 1.0 / N_ci) * w_scope * w_dep / d

    return log_score

def score_code(target, token_context, d):
    token = Mining._get_token(token_context)
    c = Mining.atmoic_change(target)
    c_token = c + token

    w_scope, w_dep = Mining._computeWeights(target, token_context)

    if In_Vocabulary_Algorithm:
        N_c_token = C_token_Database.get(c_token, 0)
        N_token = token_Database.get(token, 0)

        log_score = math.log((N_c_token * 1.0 + 1) / (N_token + 1)) * w_scope * w_dep / d
    else:
        N_c_token = C_token_Database.get(c_token, 1)
        N_token = token_Database.get(token, 1)

        if N_token != 1:
            # we have seen this token
            log_score = math.log(N_c_token * 1.0 / N_token + 1) * w_scope * w_dep / d
        else:
            log_score = math.log(N_c_token * 1.0 / N_token) * w_scope * w_dep / d

    return log_score

def _predicate(example):
    if len(example[1]) < 15 or len(example[2]) < 15:
        return False
    return True

def filterContext(target_context):
    return [ example for example in target_context if _predicate(example) ]


