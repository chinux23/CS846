from git import Repo
import Mining
import unittest


class TestMining(unittest.TestCase):
 
    def setUp(self):
        self.repo = Repo("Data/android-async-http")
        self.commits = [ commit for commit in self.repo.iter_commits()]
        self.commit = self.commits[10]
        self.diffs = self.commit.tree.diff(self.commit.parents[0].tree)
        self.diff = self.diffs[0]

        self.assertEqual(self.diff.a_path,
            'library/src/main/java/com/loopj/android/http/AsyncHttpResponseHandler.java')
        self.assertEqual(self.diff.b_path,
            'library/src/main/java/com/loopj/android/http/AsyncHttpResponseHandler.java')
        self.assertEqual(self.commit.hexsha, '2a9b4ef7de68196945920de480880a2b7829ba2a')

        with open("a_blob.java", "wb") as f:
            f.write(self.diff.a_blob.data_stream.read())
    
        with open("b_blob.java", "wb") as f:
            f.write(self.diff.b_blob.data_stream.read())
 
    def test_GumTreeDiffFiles(self):
        changes = Mining._GumTreeDiffFiles()
        print(len(changes))
        self.assertTrue(len(changes) == 65, "GumTreeDiffFiles introduced an regression. Number of changes mismatch.")
 
    def test_seperateContextAndTarget(self):
        changes = Mining._GumTreeDiffFiles()
        target, change_context = Mining._seperateContextAndTarget(changes, 40)
        w_scope, w_dep = Mining._computeWeights(target, change_context[12])

        self.assertEqual(w_scope, 0.5)
        self.assertEqual(w_dep, 0.5)

    def test_seperateContextAndTarget2(self):
        changes = Mining._GumTreeDiffFiles()
        target, change_context = Mining._seperateContextAndTarget(changes, 20)
        w_scope, w_dep = Mining._computeWeights(target, change_context[2])

        self.assertEqual(w_scope, 1)
        self.assertEqual(w_dep, 1)

    def test_change_context(self):
        changes = Mining._GumTreeDiffFiles()
        target, change_context = Mining._seperateContextAndTarget(changes, 6)

        self.assertEqual(len(change_context), 6)

        self.assertIn("action", target)
        self.assertIn("at", target)
        self.assertIn("dependant id", target)
        self.assertIn("id", target)
        self.assertIn("immediate scope", target)
        self.assertIn("label", target)
        self.assertIn("label string", target)
        self.assertIn("parent", target)
        self.assertIn("parent type", target)
        self.assertIn("pos", target)
        self.assertIn("tree", target)
        self.assertIn("type", target)

        self.assertEqual(target["action"], "insert")
        self.assertEqual(target["at"], 1)
        self.assertEqual(target["dependant id"], "SimpleName: Utils")
        self.assertEqual(target["id"], 377)
        self.assertEqual(target["immediate scope"], 404)
        self.assertEqual(target["label"], 'SimpleName: asserts')
        self.assertEqual(target["label string"], "asserts")
        self.assertEqual(target["parent"], 382)
        self.assertEqual(target["parent type"], 32)
        self.assertEqual(target["pos"], 5164)
        self.assertEqual(target["tree"], 377)
        self.assertEqual(target["type"], 42)

    def test_getNearbyTokens(self):
        tokens = Mining._getNearbyTokens({"pos": 4885})
        self.assertEqual(len(tokens), Mining.MAXIMUM_DEPTH)

        for token in tokens:
            self.assertIn("token_id", token)

    def test_seperateContextAndTarget(self):
        changes = Mining._GumTreeDiffFiles()
        target, change_context = Mining._seperateContextAndTarget(changes, 6)

        last_change = change_context[-1]

        self.assertEqual(last_change["action"], "insert")
        self.assertEqual(last_change["at"], 0)
        self.assertEqual(last_change["dependant id"], "SimpleName: Utils")
        self.assertEqual(last_change["id"], 376)
        self.assertEqual(last_change["immediate scope"], 404)
        self.assertEqual(last_change["label"], 'SimpleName: Utils')
        self.assertEqual(last_change["label string"], "Utils")
        self.assertEqual(last_change["parent"], 382)
        self.assertEqual(last_change["parent type"], 32)
        self.assertEqual(last_change["pos"], 5158)
        self.assertEqual(last_change["tree"], 376)
        self.assertEqual(last_change["type"], 42)

    def test_make_sure_change_context_are_ascending(self):
        changes = Mining._GumTreeDiffFiles()
        target, change_context = Mining._seperateContextAndTarget(changes, 6)
        for i in range(len(change_context)-1):
            self.assertTrue(change_context[i]["pos"] <= change_context[i+1]["pos"]) 

    def test_get_token_primitivetype(self):
        node = {
                    "type": 39,
                    "label": "int",
                    "id": 28,
                    "immediate scope": 36,
                    "dependant id": "PrimitiveType: int",
                    "parent type": 32,
                    "parent label": "",
                    "typeLabel": "PrimitiveType",
                    "pos": "241",
                    "length": "3",
                    "children": []
                }
        self.assertEqual(Mining._get_token(node), ('Token', 39, 'int'))

    def test_get_token_simplename(self):
        node = {
                "type": 42,
                "label": "a",
                "id": 29,
                "immediate scope": 36,
                "dependant id": "SimpleName: a",
                "parent type": 31,
                "parent label": "",
                "typeLabel": "SimpleName",
                "pos": "245",
                "length": "1",
                "children": []
            }
        self.assertEqual(Mining._get_token(node), ('Token', 31, 'a'))

    def test_get_token_modifier(self):
        node = {
								"type": 83,
								"label": "static",
								"id": 3,
								"immediate scope": 3,
								"dependant id": "Modifier: public",
								"parent type": 37,
								"parent label": "",
								"typeLabel": "Modifier",
								"pos": "46",
								"length": "6",
								"children": []
							}
        self.assertEqual(Mining._get_token(node), ('Token', 83, 'static'))

    def test_get_token_keywords(self):
        node = {
                "type": 70,
                "id": 22,
                "immediate scope": 36,
                "dependant id": "EnhancedForStatement",
                "parent type": 23,
                "parent label": "",
                "typeLabel": "EnhancedForStatement",
                "pos": "115",
                "length": "73",
                "children": [
                    {
                        "type": 44,
                        "id": 15,
                        "immediate scope": 36,
                        "dependant id": "SingleVariableDeclaration",
                        "parent type": 22,
                        "parent label": "",
                        "typeLabel": "SingleVariableDeclaration",
                        "pos": "120",
                        "length": "6",
                        "children": [
                            {
                                "type": 43,
                                "label": "Task",
                                "id": 13,
                                "immediate scope": 36,
                                "dependant id": "SimpleType: Task",
                                "parent type": 15,
                                "parent label": "",
                                "typeLabel": "SimpleType",
                                "pos": "120",
                                "length": "4",
                                "children": [
                                    {
                                        "type": 42,
                                        "label": "Task",
                                        "id": 12,
                                        "immediate scope": 36,
                                        "dependant id": "SimpleName: Task",
                                        "parent type": 13,
                                        "parent label": "Task",
                                        "typeLabel": "SimpleName",
                                        "pos": "120",
                                        "length": "4",
                                        "children": []
                                    }
                                ]
                            },
                            {
                                "type": 42,
                                "label": "t",
                                "id": 14,
                                "immediate scope": 36,
                                "dependant id": "SimpleType: Task",
                                "parent type": 15,
                                "parent label": "",
                                "typeLabel": "SimpleName",
                                "pos": "125",
                                "length": "1",
                                "children": []
                            }
                        ]
                    },
                    {
                        "type": 42,
                        "label": "tasks",
                        "id": 16,
                        "immediate scope": 36,
                        "dependant id": "SingleVariableDeclaration",
                        "parent type": 22,
                        "parent label": "",
                        "typeLabel": "SimpleName",
                        "pos": "129",
                        "length": "5",
                        "children": []
                    },
                    {
                        "type": 8,
                        "id": 21,
                        "immediate scope": 36,
                        "dependant id": "SingleVariableDeclaration",
                        "parent type": 22,
                        "parent label": "",
                        "typeLabel": "Block",
                        "pos": "136",
                        "length": "52",
                        "children": [
                            {
                                "type": 21,
                                "id": 20,
                                "immediate scope": 36,
                                "dependant id": "ExpressionStatement",
                                "parent type": 21,
                                "parent label": "",
                                "typeLabel": "ExpressionStatement",
                                "pos": "158",
                                "length": "12",
                                "children": [
                                    {
                                        "type": 32,
                                        "id": 19,
                                        "immediate scope": 36,
                                        "dependant id": "MethodInvocation",
                                        "parent type": 20,
                                        "parent label": "",
                                        "typeLabel": "MethodInvocation",
                                        "pos": "158",
                                        "length": "11",
                                        "children": [
                                            {
                                                "type": 42,
                                                "label": "t",
                                                "id": 17,
                                                "immediate scope": 36,
                                                "dependant id": "SimpleName: t",
                                                "parent type": 19,
                                                "parent label": "",
                                                "typeLabel": "SimpleName",
                                                "pos": "158",
                                                "length": "1",
                                                "children": []
                                            },
                                            {
                                                "type": 42,
                                                "label": "execute",
                                                "id": 18,
                                                "immediate scope": 36,
                                                "dependant id": "SimpleName: t",
                                                "parent type": 19,
                                                "parent label": "",
                                                "typeLabel": "SimpleName",
                                                "pos": "160",
                                                "length": "7",
                                                "children": []
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        self.assertEqual(Mining._get_token(node), ('Token', 70, ''))

    def test_save(self):
        Mining.iterateAllCommits(self.repo, 10)
        Mining.save(self.repo.working_dir)

        results = Mining.load(self.repo.working_dir)

        self.assertEqual(results[0], Mining.Ci_Database)
        self.assertEqual(results[1], Mining.C_Ci_Database)
        self.assertEqual(results[2], Mining.P_list)
        self.assertEqual(results[3], Mining.Ci_Accumulated_Weights)
        self.assertEqual(results[4], Mining.Ci_Accumulated_Distance)
        self.assertEqual(results[5], Mining.C_token_Database)
        self.assertEqual(results[6], Mining.token_Database)
        self.assertEqual(results[7], Mining.token_Accumulated_Weights)
        self.assertEqual(results[8], Mining.token_Accumulated_Distance)

if __name__ == '__main__':
    unittest.main()