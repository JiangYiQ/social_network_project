#导入模块和类初始化
from collections import defaultdict, deque
from typing import Dict, Set, Tuple, List, Optional, Any
import csv
import os
import heapq

class SocialGraph:
    def __init__(self):
        """初始化社交网络图核心数据结构"""
        # 邻接表：用户ID -> 好友ID集合（无向图）
        self.graph: Dict[int, Set[int]] = defaultdict(set)
        # 用户属性：用户ID -> {'name': 姓名, 'interests': 兴趣列表}
        self.user_attrs: Dict[int, Dict] = {}
        # 边权重：(较小用户ID, 较大用户ID) -> 权重值（避免重复存储）
        self.edge_weights: Dict[Tuple[int, int], int] = {}
        # 兴趣倒排索引（扩展功能C用，先留着）
        self.interest_index: Dict[str, List[int]] = {}

    #添加用户（含参数验证）
    def add_user(self, user_id: int, name: str, interests: List[str] = None) -> bool:
        """添加用户到社交网络，含参数验证与去重"""
        # 1. 验证用户ID（必须为正整数）
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValueError(f"用户ID必须为正整数，当前输入：{user_id}")
        # 2. 检查用户是否已存在
        if user_id in self.user_attrs:
            print(f"警告：用户ID {user_id} 已存在，跳过添加")
            return False
        # 3. 存储用户属性（兴趣默认为空列表）
        self.user_attrs[user_id] = {
            'name': name.strip(),
            'interests': interests if interests else []
        }
        # 4. 构建兴趣倒排索引（扩展功能C预处理）
        self._update_interest_index(user_id, interests)
        return True

    #在添加用户时更新倒排索引
    def _update_interest_index(self, user_id: int, interests: List[str]) -> None:
        """更新兴趣倒排索引，支持兴趣去重和用户ID去重"""
        if not interests:
            return
        # 兴趣去重（可选）
        unique_interests = list(set([i.strip() for i in interests if i.strip()]))
        for interest in unique_interests:
            if interest not in self.interest_index:
                self.interest_index[interest] = []
            if user_id not in self.interest_index[interest]:
                self.interest_index[interest].append(user_id)

    #添加好友关系
    def add_friendship(self, user1: int, user2: int, weight: int = 1) -> bool:
        """添加好友关系（无向图），含参数验证与双向存储"""
        # 1. 基础参数验证
        if user1 <= 0 or user2 <= 0:
            raise ValueError(f"用户ID必须为正整数，当前输入：{user1}, {user2}")
        if user1 == user2:
            raise ValueError("用户不能与自己建立好友关系")
        # 2. 验证用户是否存在
        if user1 not in self.user_attrs:
            raise ValueError(f"用户 {user1} 不存在，请先添加用户")
        if user2 not in self.user_attrs:
            raise ValueError(f"用户 {user2} 不存在，请先添加用户")
        # 3. 双向添加关系（无向图核心）
        self.graph[user1].add(user2)
        self.graph[user2].add(user1)
        # 4. 存储边权重（按ID排序，避免重复）
        key = (min(user1, user2), max(user1, user2))
        self.edge_weights[key] = weight
        return True

    #从CSV加载用户数据
    def load_users_from_csv(self, filename: str) -> bool:
        """从CSV文件加载用户数据，自动尝试多种编码，处理异常格式"""
        print(f"正在加载用户数据：{filename}")
        if not os.path.exists(filename):
            print(f"错误：用户数据文件不存在 -> {filename}")
            return False

        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as file:
                    reader = csv.DictReader(file)
                    required_cols = ['user_id', 'name', 'interests']
                    if not all(col in reader.fieldnames for col in required_cols):
                        print(f"错误：CSV文件缺少必要列，需包含{required_cols}")
                        return False

                    success_count = 0
                    error_count = 0
                    for row_num, row in enumerate(reader, 2):  # 表头为第1行
                        try:
                            user_id = int(row['user_id'].strip())
                            name = row['name'].strip()
                            if not name:
                                raise ValueError("姓名不能为空")
                            interests_str = row['interests'].strip()
                            interests = [i.strip() for i in interests_str.split(';') if i.strip()]
                            if self.add_user(user_id, name, interests):
                                success_count += 1
                            else:
                                error_count += 1
                        except (ValueError, KeyError) as e:
                            print(f"警告：跳过第{row_num}行，错误原因：{str(e)}")
                            error_count += 1
                            continue
                    print(f"用户数据加载完成：{success_count}条成功，{error_count}条失败")
                    return success_count > 0
            except UnicodeDecodeError:
                print(f"编码 {encoding} 解析失败，尝试下一种编码...")
                continue
            except Exception as e:
                print(f"加载用户数据时发生异常：{str(e)}")
                return False
        print("错误：无法解析文件编码，建议检查文件格式")
        return False

    #从TXT加载关系数据
    def load_relationships_from_txt(self, filename: str) -> bool:
        """从TXT文件加载好友关系，支持注释行与可选权重"""
        print(f"正在加载关系数据：{filename}")
        if not os.path.exists(filename):
            print(f"错误：关系数据文件不存在 -> {filename}")
            return False

        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        for encoding in encodings:
            try:
                with open(filename, 'r', encoding=encoding) as file:
                    success_count = 0
                    error_count = 0
                    line_num = 0
                    for line in file:
                        line_num += 1
                        line = line.strip()
                        if not line or line.startswith('#'):
                            continue
                        try:
                            parts = line.split()
                            if len(parts) < 2:
                                raise ValueError("格式错误，需至少2个用户ID")
                            user1 = int(parts[0])
                            user2 = int(parts[1])
                            weight = int(parts[2]) if len(parts) >= 3 else 1
                            if self.add_friendship(user1, user2, weight):
                                success_count += 1
                            else:
                                error_count += 1
                        except (ValueError, IndexError) as e:
                            print(f"警告：跳过第{line_num}行，错误原因：{str(e)}")
                            error_count += 1
                            continue
                    print(f"关系数据加载完成：{success_count}条成功，{error_count}条失败")
                    return success_count > 0
            except UnicodeDecodeError:
                print(f"编码 {encoding} 解析失败，尝试下一种编码...")
                continue
            except Exception as e:
                print(f"加载关系数据时发生异常：{str(e)}")
                return False
        print("错误：无法解析文件编码，建议检查文件格式")
        return False

    #一度人脉查询
    def get_direct_friends(self, user_id: int) -> List[int]:
        """获取指定用户的直接好友列表，按用户ID升序排序"""
        if user_id not in self.user_attrs:
            print(f"警告：用户 {user_id} 不存在，无法查询人脉")
            return []
        friends = list(self.graph.get(user_id, set()))
        friends.sort()
        return friends

    #带权重的一度人脉查询
    def get_direct_friends_with_weight(self, user_id: int) -> List[Tuple[int, int]]:
        """获取直接好友及关系权重，按权重降序排序（扩展功能B）"""
        friends = self.get_direct_friends(user_id)
        result = []
        for friend_id in friends:
            key = (min(user_id, friend_id), max(user_id, friend_id))
            weight = self.edge_weights.get(key, 1)
            result.append((friend_id, weight))
        # 按权重降序排序，权重相同时按ID升序
        result.sort(key=lambda x: (-x[1], x[0]))
        return result

    #实现二度人脉查询（BFS算法）
    #基础版
    def find_second_degree_friends(self, user_id: int) -> List[int]:
        """查找二度人脉（好友的好友），使用BFS算法，深度限制为2"""
        if user_id not in self.user_attrs:
            print(f"警告：用户 {user_id} 不存在，无法查询二度人脉")
            return []

        visited = set([user_id])
        queue = deque([(user_id, 0)])
        second_degree = set()

        while queue:
            current_user, depth = queue.popleft()
            if depth >= 2:
                continue
            for friend in self.graph.get(current_user, set()):
                if friend not in visited:
                    visited.add(friend)
                    if depth + 1 == 2:
                        second_degree.add(friend)
                    else:
                        queue.append((friend, depth + 1))

        # 排除直接好友和自身
        direct_friends = set(self.graph.get(user_id, set()))
        second_degree = second_degree - direct_friends
        second_degree.discard(user_id)
        return sorted(list(second_degree))

    #优化版（提升效率）
    def find_second_degree_friends_optimized(self, user_id: int) -> List[int]:
        """优化版二度人脉查询，减少集合操作"""
        if user_id not in self.user_attrs:
            return []
        direct_friends = set(self.graph.get(user_id, set()))
        visited = set([user_id]) | direct_friends
        queue = deque([(friend, 1) for friend in direct_friends])
        second_degree = set()

        while queue:
            current_user, depth = queue.popleft()
            if depth != 1:
                continue
            for neighbor in self.graph.get(current_user, set()):
                if neighbor not in visited:
                    visited.add(neighbor)
                    second_degree.add(neighbor)
        return sorted(list(second_degree))

    #实现扩展功能A：多度人脉查询（N>=3）
    def find_n_degree_friends(self, user_id: int, n: int = 3) -> List[int]:
        """查找N度人脉（N≥3），使用BFS，深度限制为n"""
        if user_id not in self.user_attrs or not isinstance(n, int) or n < 3:
            print(f"参数错误：用户不存在或度数N≥3，当前N={n}")
            return []
        visited = {user_id: 0}
        queue = deque([user_id])
        n_degree = set()

        while queue:
            current = queue.popleft()
            current_depth = visited[current]
            if current_depth >= n:
                continue
            for neighbor in self.graph.get(current, set()):
                if neighbor not in visited:
                    new_depth = current_depth + 1
                    visited[neighbor] = new_depth
                    queue.append(neighbor)
                    if new_depth == n:
                        n_degree.add(neighbor)
        return sorted(list(n_degree))

    #实现推荐算法
    def recommend_by_interest(self, user_id: int, top_k: int = 5) -> List[Tuple[int, int]]:
        """
        基于兴趣的智能推荐，返回前top_k个非好友用户（按共同兴趣数降序）
        :param user_id: 目标用户ID
        :param top_k: 推荐数量
        :return: [(用户ID, 共同兴趣数), ...]
        """
        # 参数校验
        if user_id not in self.user_attrs or not isinstance(top_k, int) or top_k <= 0:
            print(f"参数错误：用户不存在或top_k需为正整数")
            return []

        target_interests = self.user_attrs[user_id]['interests']
        if not target_interests:
            print(f"用户{user_id}无兴趣标签，无法推荐")
            return []

        # 排除自身和直接好友
        excluded = set([user_id]) | set(self.graph.get(user_id, set()))

        # 统计共同兴趣数
        interest_count = defaultdict(int)
        for interest in target_interests:
            # 从倒排索引获取拥有该兴趣的用户
            for uid in self.interest_index.get(interest, []):
                if uid not in excluded:
                    interest_count[uid] += 1

        # 按共同兴趣数降序，ID升序排序
        sorted_recommends = sorted(interest_count.items(), key=lambda x: (-x[1], x[0]))
        return sorted_recommends[:top_k]

    #实现最短路径算法
    #无权图最短路径（BFS）
    def _shortest_path_unweighted(self, start: int, target: int) -> Tuple[int, List[int]]:
        """私有方法：无权图最短路径计算，返回距离与路径"""
        if start not in self.user_attrs or target not in self.user_attrs:
            return -1, []
        if start == target:
            return 0, [start]

        visited = {start: None}
        queue = deque([start])
        found = False

        while queue and not found:
            current = queue.popleft()
            for neighbor in self.graph.get(current, set()):
                if neighbor not in visited:
                    visited[neighbor] = current
                    queue.append(neighbor)
                    if neighbor == target:
                        found = True
                        break

        if not found:
            return -1, []

        # 回溯路径
        path = []
        current = target
        while current is not None:
            path.insert(0, current)
            current = visited[current]
        return len(path) - 1, path

    #加权图最短路径（Dijkstra+堆优化）
    def _shortest_path_weighted(self, start: int, target: int) -> Tuple[int, List[int]]:
        """私有方法：加权图最短路径（Dijkstra算法），返回距离与路径"""
        if start not in self.user_attrs or target not in self.user_attrs:
            return -1, []
        if start == target:
            return 0, [start]

        distances = {uid: float('inf') for uid in self.user_attrs}
        distances[start] = 0
        predecessors = {uid: None for uid in self.user_attrs}
        heap = [(0, start)]
        visited = set()

        while heap:
            current_dist, current_node = heapq.heappop(heap)
            if current_node in visited or current_dist > distances[current_node]:
                continue
            visited.add(current_node)

            for neighbor in self.graph.get(current_node, set()):
                if neighbor in visited:
                    continue
                key = (min(current_node, neighbor), max(current_node, neighbor))
                weight = self.edge_weights.get(key, 1)
                new_dist = current_dist + weight
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    predecessors[neighbor] = current_node
                    heapq.heappush(heap, (new_dist, neighbor))

        if distances[target] == float('inf'):
            return -1, []

        path = []
        current = target
        while current is not None:
            path.insert(0, current)
            current = predecessors[current]
        return distances[target], path

    #统一计算距离接口
    def calculate_distance(self, start: int, target: int, use_weighted: bool = False) -> Tuple[int, List[int]]:
        """统一社交距离计算接口，支持加权/无权图切换"""
        if use_weighted:
            return self._shortest_path_weighted(start, target)
        else:
            return self._shortest_path_unweighted(start, target)