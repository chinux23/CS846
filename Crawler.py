#!/usr/bin/python
"""
Python module to clone the largest 50 java projects.

"""
from git import Repo
import shutil

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
    repo = Repo.clone_from(git_url, "/Users/chen/Repository/CS846/Data/"+name)
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
            total_commits += length
            if len(repos) >= 50:
                break
        else:
            # remove the repo
            shutil.rmtree("/Users/chen/Repository/CS846/Data/"+item["name"])

    print(repos)
    print("Total commits " + str(total_commits))
    
