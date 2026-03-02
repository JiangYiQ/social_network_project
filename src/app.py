# app.py
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Tuple


class SocialNetworkGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("社交网络分析系统 v1.0")
        self.root.geometry("900x700")

        # 设置样式
        self.root.configure(bg='#f0f0f0')

        # 创建界面
        self.create_widgets()

    def create_widgets(self):
        """创建所有界面元素"""

        # ========== 标题区域 ==========
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=60)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame, text="社交网络分析系统",
                               font=("微软雅黑", 20, "bold"),
                               bg='#2c3e50', fg='white')
        title_label.pack(expand=True)

        # ========== 主内容区域 ==========
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # ========== 左侧输入面板 ==========
        left_panel = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # 输入区域标题
        input_title = tk.Label(left_panel, text="查询参数输入",
                               font=("微软雅黑", 14, "bold"),
                               bg='#3498db', fg='white', pady=8)
        input_title.pack(fill=tk.X)

        # 输入表单
        form_frame = tk.Frame(left_panel, bg='white', padx=15, pady=15)
        form_frame.pack()

        # 用户ID输入
        tk.Label(form_frame, text="用户ID:", font=("微软雅黑", 11),
                 bg='white').grid(row=0, column=0, sticky=tk.W, pady=8)
        self.entry_user_id = tk.Entry(form_frame, font=("微软雅黑", 11),
                                      width=20, bd=2, relief=tk.GROOVE)
        self.entry_user_id.grid(row=0, column=1, pady=8, padx=(10, 0))

        # 目标用户ID输入
        tk.Label(form_frame, text="目标用户ID:", font=("微软雅黑", 11),
                 bg='white').grid(row=1, column=0, sticky=tk.W, pady=8)
        self.entry_target_id = tk.Entry(form_frame, font=("微软雅黑", 11),
                                        width=20, bd=2, relief=tk.GROOVE)
        self.entry_target_id.grid(row=1, column=1, pady=8, padx=(10, 0))

        # 度数N输入
        tk.Label(form_frame, text="度数N(≥3):", font=("微软雅黑", 11),
                 bg='white').grid(row=2, column=0, sticky=tk.W, pady=8)
        self.entry_degree = tk.Entry(form_frame, font=("微软雅黑", 11),
                                     width=20, bd=2, relief=tk.GROOVE)
        self.entry_degree.grid(row=2, column=1, pady=8, padx=(10, 0))
        self.entry_degree.insert(0, "3")  # 默认值

        # 加权选项
        self.weighted_var = tk.BooleanVar()
        tk.Checkbutton(form_frame, text="使用加权图计算",
                       variable=self.weighted_var,
                       font=("微软雅黑", 10), bg='white').grid(row=3, column=0,
                                                               columnspan=2,
                                                               sticky=tk.W, pady=10)

        # 分隔线
        tk.Frame(form_frame, height=2, bd=1, relief=tk.SUNKEN,
                 bg='#cccccc').grid(row=4, column=0, columnspan=2,
                                    sticky=tk.EW, pady=10)

        # ========== 功能按钮区域 ==========
        btn_frame = tk.Frame(left_panel, bg='white', padx=15, pady=10)
        btn_frame.pack(fill=tk.X)

        # 定义按钮样式
        btn_style = {
            'font': ("微软雅黑", 10),
            'width': 18,
            'height': 1,
            'bd': 0,
            'cursor': 'hand2'
        }

        # 创建按钮
        buttons = [
            ("一度人脉查询", self.query_direct_friends, '#3498db'),
            ("二度人脉查询", self.query_second_degree, '#2980b9'),
            ("社交距离计算", self.calculate_distance, '#27ae60'),
            ("N度人脉查询", self.query_n_degree, '#e67e22'),
            ("兴趣推荐", self.recommend_by_interest, '#9b59b6'),
            ("清空结果", self.clear_result, '#7f8c8d'),
            ("关于系统", self.about, '#95a5a6'),
        ]

        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(btn_frame, text=text, command=command,
                            bg=color, fg='white', activebackground=color,
                            activeforeground='white', **btn_style)
            btn.pack(pady=3)

        # ========== 右侧结果显示区域 ==========
        right_panel = tk.Frame(main_frame, bg='white', relief=tk.RAISED, bd=2)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 结果显示标题
        result_title = tk.Label(right_panel, text="查询结果",
                                font=("微软雅黑", 14, "bold"),
                                bg='#3498db', fg='white', pady=8)
        result_title.pack(fill=tk.X)

        # 结果显示文本框
        self.result_text = tk.Text(right_panel, wrap=tk.WORD,
                                   font=("Consolas", 11),
                                   bg='#ffffff', fg='#2c3e50',
                                   padx=15, pady=15,
                                   relief=tk.SUNKEN, bd=1)
        self.result_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 配置文本标签样式
        self.result_text.tag_config("info", foreground="#3498db")
        self.result_text.tag_config("success", foreground="#27ae60")
        self.result_text.tag_config("warning", foreground="#e67e22")

        # 显示初始信息
        self.display_simulation_result("欢迎使用社交网络分析系统！\n请输入参数并选择功能开始查询。", "info")

    # ========== 工具方法 ==========

    def _validate_user_id(self, user_id_str: str) -> Tuple[bool, int]:
        """
        验证用户ID输入
        返回：(是否有效, 转换后的ID)
        """
        if not user_id_str or not user_id_str.strip():
            messagebox.showerror("输入错误", "请输入用户ID")
            return False, -1

        try:
            user_id = int(user_id_str.strip())
            if user_id <= 0:
                raise ValueError("用户ID必须为正整数")
            return True, user_id
        except ValueError as e:
            messagebox.showerror("输入错误", f"无效的用户ID：{str(e)}")
            return False, -1

    def display_simulation_result(self, message: str, result_type: str = "info"):
        """
        显示模拟结果
        :param message: 要显示的消息
        :param result_type: "info"（蓝色）、"success"（绿色）、"warning"（橙色）
        """
        # 清除旧内容
        self.result_text.delete(1.0, tk.END)

        # 插入带颜色的消息
        self.result_text.insert(tk.END, message, result_type)
        self.result_text.insert(tk.END, "\n\n" + "=" * 50 + "\n")
        self.result_text.insert(tk.END, "【说明】这是模拟数据，明天将集成真实算法")

    # ========== 事件处理函数（模拟版本） ==========

    def query_direct_friends(self):
        """查询一度人脉（直接好友）- 模拟版本"""
        user_id = self.entry_user_id.get().strip()

        # 验证输入
        is_valid, uid = self._validate_user_id(user_id)
        if not is_valid:
            return

        # 模拟显示结果
        result_msg = f"【模拟结果】用户 {uid} 的一度人脉查询结果：\n"
        result_msg += "好友列表：[2, 3]\n"
        result_msg += "共找到 2 位直接好友"

        self.display_simulation_result(result_msg, "success")

    def query_second_degree(self):
        """查询二度人脉（好友的好友）- 模拟版本"""
        user_id = self.entry_user_id.get().strip()

        is_valid, uid = self._validate_user_id(user_id)
        if not is_valid:
            return

        result_msg = f"【模拟结果】用户 {uid} 的二度人脉查询结果：\n"
        result_msg += "二度人脉列表：[4, 5]\n"
        result_msg += "说明：这些是您好友的好友，可能感兴趣的人"

        self.display_simulation_result(result_msg, "success")

    def calculate_distance(self):
        """计算社交距离 - 模拟版本"""
        user_id1 = self.entry_user_id.get().strip()
        user_id2 = self.entry_target_id.get().strip()

        if not user_id1 or not user_id2:
            messagebox.showerror("输入错误", "请输入源用户ID和目标用户ID")
            return

        is_valid1, uid1 = self._validate_user_id(user_id1)
        is_valid2, uid2 = self._validate_user_id(user_id2)

        if not is_valid1 or not is_valid2:
            return

        # 获取加权选项
        use_weighted = self.weighted_var.get()
        weight_type = "加权" if use_weighted else "无权"

        result_msg = f"【模拟结果】用户 {uid1} 到用户 {uid2} 的{weight_type}社交距离：\n"
        result_msg += f"最短距离：2\n"
        result_msg += f"最短路径：{uid1} → 2 → {uid2}\n"
        result_msg += f"路径长度：2步"

        self.display_simulation_result(result_msg, "success")

    def query_n_degree(self):
        """查询N度人脉 - 模拟版本"""
        user_id = self.entry_user_id.get().strip()
        n_value = self.entry_degree.get().strip()

        is_valid, uid = self._validate_user_id(user_id)
        if not is_valid:
            return

        # 验证N值
        try:
            n = int(n_value)
            if n < 3:
                messagebox.showwarning("输入警告", "N度人脉建议查询3度及以上，正在使用N=3")
                n = 3
        except ValueError:
            messagebox.showerror("输入错误", "请输入有效的数字")
            return

        result_msg = f"【模拟结果】用户 {uid} 的 {n} 度人脉查询结果：\n"
        result_msg += f"找到 {n} 度人脉：\n"
        result_msg += "第3度：[5, 6, 7]\n"
        if n >= 4:
            result_msg += "第4度：[8, 9, 10]\n"
        result_msg += f"共找到 {n + 3} 位用户"

        self.display_simulation_result(result_msg, "success")

    def recommend_by_interest(self):
        """兴趣推荐 - 模拟版本"""
        user_id = self.entry_user_id.get().strip()

        is_valid, uid = self._validate_user_id(user_id)
        if not is_valid:
            return

        result_msg = f"【模拟结果】基于兴趣为 用户{uid} 推荐的用户：\n"
        result_msg += "1. 用户5 - 共同兴趣：音乐、编程\n"
        result_msg += "2. 用户8 - 共同兴趣：篮球、旅游\n"
        result_msg += "3. 用户12 - 共同兴趣：摄影、阅读\n"
        result_msg += "\n推荐度：★★★★☆"

        self.display_simulation_result(result_msg, "success")

    def clear_result(self):
        """清空结果显示区域"""
        self.result_text.delete(1.0, tk.END)
        self.display_simulation_result("结果显示区域已清空，可以开始新的查询", "info")

    def about(self):
        """显示关于信息"""
        about_msg = """
        社交网络分析系统 v1.0
        ====================

        开发团队：第X组
        成员：组员A、组员B

        功能列表：
        • 一度人脉查询
        • 二度人脉查询
        • 社交距离计算（加权/无权）
        • N度人脉查询（N≥3）
        • 兴趣推荐

        算法支持：BFS、Dijkstra
        开发工具：Python + Tkinter

        数据文件格式：
        - users.csv：用户信息
        - relationships.txt：关系数据

        明天将集成真实算法，敬请期待！
        """

        # 创建新窗口显示关于信息
        about_window = tk.Toplevel(self.root)
        about_window.title("关于")
        about_window.geometry("500x400")

        # 设置模态窗口
        about_window.transient(self.root)
        about_window.grab_set()

        text_area = tk.Text(about_window, wrap=tk.WORD, font=("微软雅黑", 10),
                            padx=15, pady=15)
        text_area.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text_area.insert(tk.END, about_msg)
        text_area.config(state=tk.DISABLED)  # 只读

        # 关闭按钮
        tk.Button(about_window, text="关闭", command=about_window.destroy,
                  bg='#3498db', fg='white', font=("微软雅黑", 10),
                  width=10).pack(pady=10)


def main():
    root = tk.Tk()
    app = SocialNetworkGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()