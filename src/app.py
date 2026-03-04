# src/app.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
from tkinter.scrolledtext import ScrolledText
from src.social_graph import SocialGraph
import os
from typing import List, Tuple
import datetime


class SocialNetworkApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("社交网络分析系统")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)

        self.graph = SocialGraph()
        # 修改为正确的绝对路径
        self.user_csv_path = "C:/Users/零零幺/OneDrive/Documents/桌面/social_network_project/data/user_sample.csv"
        self.relation_txt_path = "C:/Users/零零幺/OneDrive/Documents/桌面/social_network_project/data/relationships.txt"

        self.user_id_var = tk.StringVar()
        self.start_id_var = tk.StringVar()
        self.target_id_var = tk.StringVar()
        self.degree_var = tk.StringVar(value="3")
        self.top_k_var = tk.StringVar(value="5")
        self.weighted_var = tk.BooleanVar(value=False)

        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        # 菜单栏
        menubar = Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = Menu(menubar, tearoff=0)
        file_menu.add_command(label="加载用户数据", command=self.load_user_data_manual)
        file_menu.add_command(label="加载关系数据", command=self.load_relation_data_manual)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        menubar.add_cascade(label="文件", menu=file_menu)

        help_menu = Menu(menubar, tearoff=0)
        help_menu.add_command(label="功能说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)
        menubar.add_cascade(label="帮助", menu=help_menu)

        # 左侧功能区
        left_frame = ttk.Frame(self.root, width=300)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
        left_frame.pack_propagate(False)

        # 一度人脉
        direct_frame = ttk.LabelFrame(left_frame, text="一度人脉查询", padding=(10, 5))
        direct_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(direct_frame, text="用户ID：").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(direct_frame, textvariable=self.user_id_var, width=15).grid(row=0, column=1, pady=5)
        ttk.Button(direct_frame, text="查询", command=self.query_direct_friends).grid(row=0, column=2, padx=5, pady=5)

        # 二度人脉
        second_frame = ttk.LabelFrame(left_frame, text="二度人脉查询", padding=(10, 5))
        second_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(second_frame, text="用户ID：").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(second_frame, textvariable=self.user_id_var, width=15).grid(row=0, column=1, pady=5)
        ttk.Button(second_frame, text="查询", command=self.query_second_degree).grid(row=0, column=2, padx=5, pady=5)

        # 社交距离
        distance_frame = ttk.LabelFrame(left_frame, text="社交距离计算", padding=(10, 5))
        distance_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(distance_frame, text="起点ID：").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(distance_frame, textvariable=self.start_id_var, width=15).grid(row=0, column=1, pady=5)
        ttk.Label(distance_frame, text="终点ID：").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(distance_frame, textvariable=self.target_id_var, width=15).grid(row=1, column=1, pady=5)
        ttk.Checkbutton(distance_frame, text="加权图", variable=self.weighted_var).grid(row=0, column=2, padx=5, pady=5,
                                                                                        rowspan=2)
        ttk.Button(distance_frame, text="计算", command=self.calculate_distance).grid(row=2, column=1, pady=5)

        # 扩展功能
        extend_frame = ttk.LabelFrame(left_frame, text="扩展功能", padding=(10, 5))
        extend_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(extend_frame, text="多度人脉（度数）：").grid(row=0, column=0, sticky=tk.W, pady=5)
        ttk.Entry(extend_frame, textvariable=self.degree_var, width=5).grid(row=0, column=1, pady=5)
        ttk.Button(extend_frame, text="查询", command=self.query_n_degree).grid(row=0, column=2, padx=5, pady=5)
        ttk.Label(extend_frame, text="兴趣推荐（数量）：").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(extend_frame, textvariable=self.top_k_var, width=5).grid(row=1, column=1, pady=5)
        ttk.Button(extend_frame, text="推荐", command=self.recommend_by_interest).grid(row=1, column=2, padx=5, pady=5)

        # 右侧结果区
        right_frame = ttk.Frame(self.root)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.result_text = ScrolledText(right_frame, wrap=tk.WORD, font=("Consolas", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=(0, 5))
        self.result_text.config(state=tk.DISABLED)

        # 修复：将 anchor=tk.RIGHT 改为 anchor='e'
        ttk.Button(right_frame, text="清空结果", command=self.clear_result).pack(anchor='e')

        self.display_result("欢迎使用社交网络分析系统！\n已自动加载默认数据文件。\n", "info")

    def display_result(self, message: str, tag: str = "normal"):
        self.result_text.config(state=tk.NORMAL)
        time_str = datetime.datetime.now().strftime("[%H:%M:%S] ")
        full_msg = time_str + message + "\n"
        self.result_text.tag_config("info", foreground="#0066CC")
        self.result_text.tag_config("success", foreground="#009933")
        self.result_text.tag_config("error", foreground="#CC0000")
        self.result_text.insert(tk.END, full_msg, tag)
        self.result_text.see(tk.END)
        self.result_text.config(state=tk.DISABLED)

    def clear_result(self):
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.display_result("结果区已清空", "info")

    def load_data(self):
        self.display_result("开始加载默认数据...", "info")

        # 检查文件是否存在
        import os
        if not os.path.exists(self.user_csv_path):
            self.display_result(f"错误：用户数据文件不存在 -> {self.user_csv_path}", "error")
            self.display_result("请检查文件路径或手动加载", "info")
        else:
            self.display_result(f"找到用户数据文件：{self.user_csv_path}", "info")
            user_ok = self.graph.load_users_from_csv(self.user_csv_path)
            if user_ok:
                self.display_result("用户数据加载成功", "success")
            else:
                self.display_result("用户数据加载失败，请检查文件格式", "error")

        if not os.path.exists(self.relation_txt_path):
            self.display_result(f"错误：关系数据文件不存在 -> {self.relation_txt_path}", "error")
            self.display_result("请检查文件路径或手动加载", "info")
        else:
            self.display_result(f"找到关系数据文件：{self.relation_txt_path}", "info")
            rel_ok = self.graph.load_relationships_from_txt(self.relation_txt_path)
            if rel_ok:
                self.display_result("关系数据加载成功", "success")
            else:
                self.display_result("关系数据加载失败，请检查文件格式", "error")

        if hasattr(self.graph, 'user_attrs') and self.graph.user_attrs:
            self.display_result(f"当前系统共有 {len(self.graph.user_attrs)} 个用户", "info")

    def load_user_data_manual(self):
        path = filedialog.askopenfilename(title="选择用户数据文件",
                                          filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")])
        if path:
            self.user_csv_path = path
            if self.graph.load_users_from_csv(path):
                self.display_result(f"用户数据加载成功（{path}）", "success")
            else:
                self.display_result(f"用户数据加载失败（{path}）", "error")

    def load_relation_data_manual(self):
        path = filedialog.askopenfilename(title="选择关系数据文件",
                                          filetypes=[("TXT文件", "*.txt"), ("所有文件", "*.*")])
        if path:
            self.relation_txt_path = path
            if self.graph.load_relationships_from_txt(path):
                self.display_result(f"关系数据加载成功（{path}）", "success")
            else:
                self.display_result(f"关系数据加载失败（{path}）", "error")

    def _validate_user_id(self, user_id_str: str) -> Tuple[bool, int]:
        try:
            user_id = int(user_id_str.strip())
            if user_id <= 0:
                raise ValueError("用户ID必须为正整数")
            if not hasattr(self.graph, 'user_attrs') or user_id not in self.graph.user_attrs:
                raise ValueError(f"用户ID {user_id} 不存在")
            return True, user_id
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
            return False, -1

    def query_direct_friends(self):
        user_id_str = self.user_id_var.get()
        valid, user_id = self._validate_user_id(user_id_str)
        if not valid:
            return
        friends = self.graph.get_direct_friends(user_id)
        user_name = self.graph.user_attrs[user_id]['name']
        if not friends:
            self.display_result(f"用户{user_id}（{user_name}）无直接好友", "info")
            return
        friend_info = []
        for fid in friends:
            fname = self.graph.user_attrs[fid]['name']
            friend_info.append(f"{fid}（{fname}）")
        self.display_result(f"用户{user_id}（{user_name}）的一度人脉：{', '.join(friend_info)}", "success")

    def query_second_degree(self):
        user_id_str = self.user_id_var.get()
        valid, user_id = self._validate_user_id(user_id_str)
        if not valid:
            return
        second = self.graph.find_second_degree_friends_optimized(user_id)
        user_name = self.graph.user_attrs[user_id]['name']
        if not second:
            self.display_result(f"用户{user_id}（{user_name}）无二度人脉", "info")
            return
        friend_info = []
        for fid in second:
            fname = self.graph.user_attrs[fid]['name']
            friend_info.append(f"{fid}（{fname}）")
        self.display_result(f"用户{user_id}（{user_name}）的二度人脉：{', '.join(friend_info)}", "success")

    def calculate_distance(self):
        start_str = self.start_id_var.get()
        target_str = self.target_id_var.get()
        valid_start, start_id = self._validate_user_id(start_str)
        valid_target, target_id = self._validate_user_id(target_str)
        if not valid_start or not valid_target:
            return
        distance, path = self.graph.calculate_distance(start_id, target_id, self.weighted_var.get())
        start_name = self.graph.user_attrs[start_id]['name']
        target_name = self.graph.user_attrs[target_id]['name']
        mode = "加权图" if self.weighted_var.get() else "无权图"
        if distance == -1:
            self.display_result(f"{mode}下，用户{start_id}（{start_name}）与{target_id}（{target_name}）无连通路径", "info")
            return
        path_info = []
        for fid in path:
            fname = self.graph.user_attrs[fid]['name']
            path_info.append(f"{fid}（{fname}）")
        path_str = " -> ".join(path_info)
        dist_desc = f"权重和：{distance}" if self.weighted_var.get() else f"距离：{distance}（边数）"
        self.display_result(
            f"{mode}下，用户{start_id}（{start_name}）与{target_id}（{target_name}）的最短路径：\n{path_str}\n{dist_desc}",
            "success")

    def query_n_degree(self):
        user_id_str = self.user_id_var.get()
        degree_str = self.degree_var.get()
        valid, user_id = self._validate_user_id(user_id_str)
        if not valid:
            return
        try:
            degree = int(degree_str.strip())
            if degree < 3:
                raise ValueError("多度人脉度数必须≥3")
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
            return
        n_degree = self.graph.find_n_degree_friends(user_id, degree)
        user_name = self.graph.user_attrs[user_id]['name']
        if not n_degree:
            self.display_result(f"用户{user_id}（{user_name}）无{degree}度人脉", "info")
            return
        friend_info = []
        for fid in n_degree:
            fname = self.graph.user_attrs[fid]['name']
            friend_info.append(f"{fid}（{fname}）")
        self.display_result(f"用户{user_id}（{user_name}）的{degree}度人脉：{', '.join(friend_info)}", "success")

    def recommend_by_interest(self):
        user_id_str = self.user_id_var.get()
        top_k_str = self.top_k_var.get()
        valid, user_id = self._validate_user_id(user_id_str)
        if not valid:
            return
        try:
            top_k = int(top_k_str.strip())
            if top_k <= 0:
                raise ValueError("推荐数量必须为正整数")
        except ValueError as e:
            messagebox.showerror("输入错误", str(e))
            return
        recommends = self.graph.recommend_by_interest(user_id, top_k)
        user_name = self.graph.user_attrs[user_id]['name']
        user_interests = ", ".join(self.graph.user_attrs[user_id]['interests'])
        if not recommends:
            self.display_result(f"无符合条件的推荐用户（用户{user_id}兴趣：{user_interests}）", "info")
            return
        recommend_info = []
        for fid, count in recommends:
            fname = self.graph.user_attrs[fid]['name']
            recommend_info.append(f"{fid}（{fname}）[共同兴趣数：{count}]")
        self.display_result(
            f"基于兴趣推荐给用户{user_id}（{user_name}）的用户（前{top_k}名）：\n{', '.join(recommend_info)}\n用户兴趣：{user_interests}",
            "success")

    def show_help(self):
        help_text = """\
社交网络分析系统功能说明：
1. 一度人脉：查询指定用户的直接好友
2. 二度人脉：查询用户的"好友的好友"（排除直接好友）
3. 社交距离：计算两用户间最短路径（支持加权/无权图切换）
4. 多度人脉：查询3度及以上人脉（自定义度数）
5. 兴趣推荐：推荐有共同兴趣的非好友用户（按共同兴趣数排序）

操作提示：
- 首次启动自动加载默认数据文件
- 可通过"文件"菜单手动选择数据文件
- 输入用户ID时请确保为正整数且存在于数据中
- 结果区内容可通过"清空结果"按钮删除
"""
        messagebox.showinfo("功能说明", help_text)

    def show_about(self):
        about_text = """\
社交网络分析系统（V1.0）
基于数据结构课程设计开发
核心技术：Python、Tkinter、图论算法（BFS、Dijkstra）
功能覆盖：人脉查询、路径计算、智能推荐

开发团队：猿代码小组
开发日期：2026年3月4日
"""
        messagebox.showinfo("关于", about_text)


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = SocialNetworkApp(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("启动失败", f"应用启动时发生异常：{str(e)}")