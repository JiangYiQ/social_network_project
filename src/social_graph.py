#导入模块和类初始化
from collections import defaultdict, deque
from typing import Dict, Set, Tuple, List, Optional, Any
import csv
import os

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

    def _update_interest_index(self, user_id: int, interests: List[str]) -> None:
        """私有方法：更新兴趣倒排索引（内部调用）"""
        if not interests:
            return
        for interest in interests:
            interest = interest.strip()
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
