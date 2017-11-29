import Mining
import os
from collections import Counter
import math


Ci_Database = Counter({})
C_Ci_Database = Counter({})
P_list = set()
Ci_Accumulated_Weights = Counter({})
Ci_Accumulated_Distance = Counter({})
C_token_Database = Counter({})
token_Database = Counter({})
token_Accumulated_Weights = Counter({})
token_Accumulated_Distance = Counter({})

target_context = []


def update_database(results):
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
    global P_list
    
    Ci_Database += Counter(results[0])
    C_Ci_Database += Counter(results[1])
    P_list = P_list.union(results[2])
    Ci_Accumulated_Weights += Counter(results[3])
    Ci_Accumulated_Distance += Counter(results[4])
    C_token_Database += Counter(results[5])
    token_Database += Counter(results[6])
    token_Accumulated_Weights += Counter(results[7])
    token_Accumulated_Distance += Counter(results[8])
    target_context += results[9]


def iterate():
    count = 0
    for folder in os.listdir("Data"):
        repo_path = os.path.join("Data", folder)
        if os.path.isdir(os.path.join("Data", folder)) and not folder.startswith("."):
            database_path = os.path.join(repo_path, "API___Database")
            if os.path.exists(database_path):
                count += 1
                print("" + str(count) + " " + folder)
                results = Mining.load(repo_path)
                update_database(results)

    print("Finished mining on " + str(count) + " repos.")

def save(path = "Summary"):
    import pickle

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

    if not os.path.exists("{}/API___Database".format(path)):
        os.mkdir("{}/API___Database".format(path))

    with open('{}/API___Database/Ci_Database.pkl'.format(path), 'w') as fp:
        pickle.dump(Ci_Database, fp)
    with open('{}/API___Database/C_Ci_Database.pkl'.format(path), 'w') as fp:
        pickle.dump(C_Ci_Database, fp)
    with open('{}/API___Database/P_list.pkl'.format(path), 'w') as fp:
        pickle.dump(list(P_list), fp)
    with open('{}/API___Database/Ci_Accumulated_Weights.pkl'.format(path), 'w') as fp:
        pickle.dump(Ci_Accumulated_Weights, fp)
    with open('{}/API___Database/Ci_Accumulated_Distance.pkl'.format(path), 'w') as fp:
        pickle.dump(Ci_Accumulated_Distance, fp)

    with open('{}/API___Database/C_token_Database.pkl'.format(path), 'w') as fp:
        pickle.dump(C_token_Database, fp)
    with open('{}/API___Database/token_Database.pkl'.format(path), 'w') as fp:
        pickle.dump(token_Database, fp)
    with open('{}/API___Database/token_Accumulated_Weights.pkl'.format(path), 'w') as fp:
        pickle.dump(token_Accumulated_Weights, fp)
    with open('{}/API___Database/token_Accumulated_Distance.pkl'.format(path), 'w') as fp:
        pickle.dump(token_Accumulated_Distance, fp)

    with open("{}/API___Database/target_context.pkl".format(path), 'w') as fp:
        pickle.dump(target_context, fp)

def load(path = "Summary"):
    import pickle

    if not os.path.exists("{}/API___Database".format(path)):
        raise IOError("{}/API___Database does not exist".format(path))

    with open('{}/API___Database/Ci_Database.pkl'.format(path), 'r') as fp:
        Ci_Database = pickle.load(fp)
    with open('{}/API___Database/C_Ci_Database.pkl'.format(path), 'r') as fp:
        C_Ci_Database = pickle.load(fp)
    with open('{}/API___Database/P_list.pkl'.format(path), 'r') as fp:
        P_list = pickle.load(fp)
    with open('{}/API___Database/Ci_Accumulated_Weights.pkl'.format(path), 'r') as fp:
        Ci_Accumulated_Weights = pickle.load(fp)
    with open('{}/API___Database/Ci_Accumulated_Distance.pkl'.format(path), 'r') as fp:
        Ci_Accumulated_Distance = pickle.load(fp)

    with open('{}/API___Database/C_token_Database.pkl'.format(path), 'r') as fp:
        C_token_Database = pickle.load(fp)
    with open('{}/API___Database/token_Database.pkl'.format(path), 'r') as fp:
        token_Database = pickle.load(fp)
    with open('{}/API___Database/token_Accumulated_Weights.pkl'.format(path), 'r') as fp:
        token_Accumulated_Weights = pickle.load(fp)
    with open('{}/API___Database/token_Accumulated_Distance.pkl'.format(path), 'r') as fp:
        token_Accumulated_Distance = pickle.load(fp)

    with open('{}/API___Database/target_context.pkl'.format(path), 'r') as fp:
        target_context = pickle.load(fp)

    return (Ci_Database, C_Ci_Database, set(P_list), Ci_Accumulated_Weights, Ci_Accumulated_Distance, C_token_Database,
            token_Database, token_Accumulated_Weights, token_Accumulated_Distance, target_context)

if __name__ == "__main__":
    iterate()

    save()

