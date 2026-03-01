#单元测试
import unittest
import os
from src.social_graph import SocialGraph

class TestSocialGraph(unittest.TestCase):
    def setUp(self):
        """每个测试用例前初始化测试环境"""
        self.graph = SocialGraph()
        # 添加测试用户
        self.graph.add_user(1, "张三", ["篮球", "音乐"])
        self.graph.add_user(2, "李四", ["阅读", "摄影"])
        self.graph.add_user(3, "王五", ["游戏", "电影"])
        self.graph.add_user(4, "赵六", ["运动", "烹饪"])
        # 添加测试关系
        self.graph.add_friendship(1, 2, weight=5)
        self.graph.add_friendship(1, 3, weight=8)
        self.graph.add_friendship(2, 3, weight=3)
        self.graph.add_friendship(2, 4, weight=7)

    def test_add_user(self):
        self.assertTrue(self.graph.add_user(5, "孙七", ["编程"]))
        self.assertFalse(self.graph.add_user(1, "重复用户"))
        with self.assertRaises(ValueError):
            self.graph.add_user(0, "无效用户")
        with self.assertRaises(ValueError):
            self.graph.add_user(-1, "无效用户")

    def test_add_friendship(self):
        self.assertTrue(self.graph.add_friendship(3, 4, weight=2))
        with self.assertRaises(ValueError):
            self.graph.add_friendship(1, 1)
        with self.assertRaises(ValueError):
            self.graph.add_friendship(1, 999)

    def test_get_direct_friends(self):
        self.assertEqual(self.graph.get_direct_friends(1), [2, 3])
        self.assertEqual(self.graph.get_direct_friends(4), [2])
        self.assertEqual(self.graph.get_direct_friends(999), [])

    def test_get_direct_friends_with_weight(self):
        # 用户2的好友：1(5),3(3),4(7) -> 按权重降序应为 (4,7),(1,5),(3,3)
        result = self.graph.get_direct_friends_with_weight(2)
        self.assertEqual(result, [(4,7), (1,5), (3,3)])

    def test_load_users_from_csv(self):
        csv_content = "user_id,name,interests\n5,孙七,编程;音乐\n6,周八,旅游"
        with open("data/test_users.csv", 'w', encoding='utf-8') as f:
            f.write(csv_content)
        result = self.graph.load_users_from_csv("data/test_users.csv")
        self.assertTrue(result)
        self.assertIn(5, self.graph.user_attrs)
        self.assertEqual(self.graph.user_attrs[5]['name'], "孙七")
        os.remove("data/test_users.csv")

    def test_load_relationships_from_txt(self):
        txt_content = "# 测试关系\n1 2 5\n1 3 8\n2 4 7"
        with open("data/test_rels.txt", 'w', encoding='utf-8') as f:
            f.write(txt_content)
        result = self.graph.load_relationships_from_txt("data/test_rels.txt")
        self.assertTrue(result)
        # 验证关系是否存在（用户1的好友包括2和3）
        self.assertIn(2, self.graph.graph[1])
        self.assertIn(3, self.graph.graph[1])
        os.remove("data/test_rels.txt")

if __name__ == '__main__':
    unittest.main(verbosity=2)