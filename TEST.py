#!python -u

import APIREC
import Aggregator
import Mining
import math
from Queue import PriorityQueue, heapq
from multiprocessing import Pool
from functools import partial
import time
import os

InTraining = False

# top1, top2, top3, top5, top10
top = [1, 2, 3, 5, 10]
weights =[0.5, 0.5]


def score(target, change_context, code_context):
    global weights

    if weights is None:
        w_change = 0.5
        w_code = 1 - w_change
    else:
        w_change = weights[0]
        w_code = weights[1]

    change_score = APIREC.change_score_transaction(target, change_context)
    code_score = APIREC.code_score_transaction(target, code_context)
    
    score = w_change * change_score + w_code * code_score
    
    return score

def predict(total_number):
    hit = 0
    
    for n in range(total_number):

        target = APIREC.target_context[n][0]
        change_context = APIREC.target_context[n][1]
        code_context = APIREC.target_context[n][2]

        h = []
        for candidate in APIREC.P_list:

            candidate_target = dict(target)
            candidate_target['label'] = candidate[2]
            _score = score(candidate_target, change_context, code_context)
            q = heapq.heappush(h, (_score, candidate))        

        top10 = heapq.nlargest(10, h)
        # print("Top 10: " + str(top10))
        prediction = Mining.atmoic_change(target)
        # print("Target: " + str(prediction))

        for i in top10:
            candidate = i[1]
            if candidate == prediction:
                hit += 1
                # print("hit")
                break

    print("Final prediction accuracy: " + str(1.0 * hit / total_number))

def _predict(n):
    # print("{} with {}".format(n, training))

    global top
    global weights

    hit = 0
    target = APIREC.target_context[n][0]
    change_context = APIREC.target_context[n][1]
    code_context = APIREC.target_context[n][2]

    h = []

    for candidate in APIREC.P_list:

        candidate_target = dict(target)
        candidate_target['label'] = candidate[2]
        change_score = APIREC.change_score_transaction(candidate_target, change_context)
        code_score = APIREC.code_score_transaction(candidate_target, code_context)
        
        w_change = weights[0]
        w_code = 1 - w_change
        _score = w_change * change_score + w_code * code_score
        heapq.heappush(h, (_score, candidate))

    hit = [0] * 5
    for i in range(5):
        topX = heapq.nlargest(top[i], h)
        # print("Top 10: " + str(top10))
        prediction = Mining.atmoic_change(target)
        # print("Target: " + str(prediction))

        for item in topX:
            candidate = item[1]
            if candidate == prediction:
                hit[i] += 1
                # print("{} hit".format(i))
                break
    # print("return {}".format(hit))
    return hit

def testRepo(repo, size=100):
    global top
    print("----------------------------------------------")
    print("Loadiong repo {}".format(repo))
    _, _, _, _, _, _, _, _, _, target_context = Mining.load(repo)
    APIREC.target_context = target_context
    print("There are {} items in repo {}.".format(len(target_context), repo))
    
    t1 = time.time()

    size = len(APIREC.target_context)

    print("Processing " + str(size) + " items.")
    p = Pool()

    result = p.map(_predict, range(size))

    p.close()
    p.join()

    print("Took " + str(time.time() - t1) + " seconds.")
    print("Total evaluation: " + str(len(result)))
    result = [sum(x) for x in zip(*result)]
    for i in range(len(result)):
        print("Overall Accurracy for top{} is ".format(top[i]) + str(result[i] * 1.0 / size))

    # in-sample counts
    num_in = 0
    for example in target_context:
        if Mining.atmoic_change(example[0]) in APIREC.P_list:
            num_in += 1

    for i in range(len(result)):
        print("In-sample Accurracy for top{} is ".format(top[i]) + str(result[i] * 1.0 / num_in)) 

def validate(repos):
    repos = []
    for folder in os.listdir("Community"):
        repo_path = os.path.join("Community", folder)
        if os.path.isdir(os.path.join("Community", folder)) and not folder.startswith("."):
            repos.append("Community/{}".format(folder))

    for repo in repos:
        print("Loadiong repo {}".format(repo))
        _, _, _, _, _, _, _, _, _, target_context = Mining.load(repo)
        print("There are {} items in repo {}.".format(len(target_context), repo))

def main():

    print("Loading database.")
    APIREC.load()

    repos = []
    for folder in os.listdir("Community"):
        repo_path = os.path.join("Community", folder)
        if os.path.isdir(os.path.join("Community", folder)) and not folder.startswith("."):
            repos.append("Community/{}".format(folder))

    for repo in repos:
        testRepo(repo)


if __name__ == "__main__":
    main()
