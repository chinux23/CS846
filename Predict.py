#!/usr/bin/python -u

import APIREC
import Aggregator
import Mining
import math
from Queue import PriorityQueue, heapq
from multiprocessing import Pool
import time

InTraining = False


def score(target, change_context, code_context, weights=None):
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

def _predict(n, training=[0.5]):
    hit = 0
    target = APIREC.target_context[n][0]
    change_context = APIREC.target_context[n][1]
    code_context = APIREC.target_context[n][2]

    h = []
    for i in len(training):
        h.append([])

    for candidate in APIREC.P_list:

        candidate_target = dict(target)
        candidate_target['label'] = candidate[2]
        change_score = APIREC.change_score_transaction(target, change_context)
        code_score = APIREC.code_score_transaction(target, code_context)
        for i in len(training):
            w_change = training[i]
            w_code = 1 - w_change
            _score = w_change * change_score + w_code * code_score
            heapq.heappush(h[i], (_score, candidate))

    hit = []
    for i in len(training):
        top10 = heapq.nlargest(10, h[i])
        # print("Top 10: " + str(top10))
        prediction = Mining.atmoic_change(target)
        # print("Target: " + str(prediction))

        for item in top10:
            candidate = item[1]
            if candidate == prediction:
                hit[i] += 1
                # print("hit")
                break
    return hit

def main():

    print("Loading database.")
    APIREC.load()

    t1 = time.time()

    size = len(APIREC.target_context)
    # size = 10000
    print("Processing " + str(size) + " items.")
    p = Pool()

    result = p.map(_predict, range(size))

    p.close()
    p.join()

    print("Took " + str(time.time() - t1) + " seconds.")

    for i in len(result):
        print("Total evaluation: " + str(len(result[i])))
        print("Accurracy {} is ".format(i) + str(sum(result[i]) * 1.0 / size))

if __name__ == "__main__":
    main()
