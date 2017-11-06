"""
Python module to clone the largest 50 java projects.

"""

def loadrepos():
    import json
    with open("repos.json") as f:
        repo1 = json.loads(f.read())

    with open("repos2.json") as f:
        repo2 = json.loads(f.read())

    items1 = repo1["items"]
    items2 = repo2["items"]
    items = items1 + items2
    return items

def clone(git_url, name):
    from git import Repo
    repo = Repo.clone_from(git_url, "/Users/chen/Repository/CS846/Data/"+name)
    return repo

if __name__ == "__main__":
    items = loadrepos()
    repos = {}

    for item in items[:50]:
        print("Clone {}".format(item["name"]))
        repos[item["name"]] = clone(item["git_url"], item["name"])
    
