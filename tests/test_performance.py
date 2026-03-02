import time
import random
from src.social_graph import SocialGraph

def test_bfs_performance():
    graph = SocialGraph()
    # 生成1000用户
    for uid in range(1, 1001):
        graph.add_user(uid, f"User{uid}", [f"interest{random.randint(1,20)}"])
    # 生成5000随机关系
    rels = set()
    while len(rels) < 5000:
        u1 = random.randint(1,1000)
        u2 = random.randint(1,1000)
        if u1 != u2:
            rels.add((min(u1,u2), max(u1,u2)))
    for u1,u2 in rels:
        graph.add_friendship(u1, u2, random.randint(1,10))

    start = time.time()
    for _ in range(10):
        uid = random.randint(1,1000)
        graph.find_second_degree_friends_optimized(uid)
    avg = (time.time() - start) / 10
    print(f"BFS平均耗时：{avg:.4f}秒")
    assert avg <= 0.1, f"性能不达标：{avg}秒"

def test_dijkstra_performance():
    # 类似，测试Dijkstra
    pass  # 可自行扩展

if __name__ == "__main__":
    test_bfs_performance()