#!/usr/bin/python
"""
Python module to clone the largest 50 java projects.

"""
from git import Repo
import shutil
import os

def loadrepos():
    import json

    items = []

    for i in range(10):
        i += 1
        with open("DataRepoList/repo" + str(i) +".json") as f:
            repo = json.loads(f.read())
        items += repo["items"]
    
    return items

def clone(git_url, name):
    from git import Repo
    if os.path.exists("Data/"+name):
        repo = Repo("Data/"+name)
    else:
        repo = Repo.clone_from(git_url, "Data/"+name)
    return repo

if __name__ == "__main__":
    items = loadrepos()
    repos = []
    total_commits = 0

    for item in items[:]:
        print("Clone {}".format(item["name"]))
        repo = clone(item["git_url"], item["name"])
        length = len([commit for commit in repo.iter_commits()])

        if length >= 1000:
            repos.append(repo)
            print("Adding " + item["name"])
            print("Currently there are " + str(len(repos)) + " repos.")
            total_commits += length
            if len(repos) >= 50:
                print("Prison Break!")
                print("length of repos are {}".format(len(repos)))
                print("Condition is {}".format(len(repos) >= 50))
                break
        else:
            # remove the repo
            shutil.rmtree("Data/"+item["name"])

    print("Total commits " + str(total_commits))
    
