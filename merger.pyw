import os
import tkinter as tk
from tkinter import filedialog, messagebox

from tkinterdnd2 import DND_FILES, TkinterDnD

# ===== 📖 UI参数 =====

# 初始窗口大小
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 900

# 初始的左右分割比例（左边文件列表宽度的百分比）
INITIAL_LEFT_PANE_WIDTH_RATIO = 0.25

# 状态栏初始提示文本
STATUS_BAR_INIT_TEXT = "请拖拽文件或文件夹到此处"

# 应用标题
APP_TITLE = "多文件文本合并工具"

# --- 主程序 ---


class TextMergerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        # 存储文件的完整路径，列表的顺序就是合并的顺序
        self.file_paths = []

        # --- 创建UI组件 ---
        self._create_widgets()

        # --- 绑定拖拽事件 ---
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind("<<Drop>>", self.handle_drop)

    def _create_widgets(self):
        # 主布局：使用 PanedWindow 实现可拖拽调整左右区域大小
        main_pane = tk.PanedWindow(
            self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED
        )
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # --- 左侧：文件列表区 ---
        left_frame = tk.Frame(main_pane, width=300)
        left_frame.pack_propagate(False)

        tk.Label(
            left_frame, text="文件列表 (可拖拽排序)", font=("Helvetica", 12, "bold")
        ).pack(pady=(0, 5))

        list_frame = tk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)

        self.file_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE)
        self.file_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        list_scrollbar = tk.Scrollbar(
            list_frame, orient=tk.VERTICAL, command=self.file_listbox.yview
        )
        list_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.file_listbox.config(yscrollcommand=list_scrollbar.set)

        # 绑定列表内部拖拽排序事件
        self.file_listbox.bind("<Button-1>", self._on_drag_start)
        self.file_listbox.bind("<B1-Motion>", self._on_drag_motion)
        self.file_listbox.bind("<ButtonRelease-1>", self._on_drop)
        self.file_listbox.bind("<Delete>", self.remove_selected_file)
        self.file_listbox.bind("<Up>", self._on_key_up)
        self.file_listbox.bind("<Down>", self._on_key_down)

        main_pane.add(left_frame)

        # --- 右侧：内容预览区 ---
        right_frame = tk.Frame(main_pane)
        tk.Label(right_frame, text="内容预览", font=("Helvetica", 12, "bold")).pack(
            pady=(0, 5)
        )

        text_frame = tk.Frame(right_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.text_preview = tk.Text(
            text_frame, wrap=tk.WORD, state=tk.DISABLED, font=("Consolas", 10)
        )
        self.text_preview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        text_scrollbar = tk.Scrollbar(
            text_frame, orient=tk.VERTICAL, command=self.text_preview.yview
        )
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text_preview.config(yscrollcommand=text_scrollbar.set)

        main_pane.add(right_frame)
        initial_sash_pos = int(WINDOW_WIDTH * INITIAL_LEFT_PANE_WIDTH_RATIO)
        main_pane.sash_place(0, initial_sash_pos, 0)

        # --- 底部：控制按钮和状态栏 ---
        bottom_frame = tk.Frame(self.root)
        bottom_frame.pack(fill=tk.X, padx=10, pady=5)

        # 创建按钮（移除快捷键提示）
        tk.Button(bottom_frame, text="排序文件", command=self.sort_files).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(bottom_frame, text="颠倒顺序", command=self.reverse_files).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(bottom_frame, text="复制内容", command=self.copy_to_clipboard).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(bottom_frame, text="保存到文件...", command=self.save_to_file).pack(
            side=tk.LEFT, padx=5
        )
        tk.Button(bottom_frame, text="重新读取", command=self.reload_all_files).pack(
            side=tk.LEFT, padx=5
        )

        # 右侧清除按钮
        tk.Button(bottom_frame, text="全部清除", command=self.clear_all).pack(
            side=tk.RIGHT, padx=5
        )

        self.status_label = tk.Label(
            self.root, text=STATUS_BAR_INIT_TEXT, bd=1, relief=tk.SUNKEN, anchor=tk.W
        )
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def handle_drop(self, event):
        """处理拖拽进来的文件/文件夹"""
        paths = self.root.tk.splitlist(event.data)
        added_count = 0
        was_empty = len(self.file_paths) == 0

        for path in paths:
            if os.path.isdir(path):
                added_count += self._add_directory(path)
            elif os.path.isfile(path):
                if self._add_file(path):
                    added_count += 1

        if added_count > 0:
            # 如果拖拽前是空的，则自动按文件名排序
            if was_empty and len(self.file_paths) > 1:
                self.sort_files()
            else:
                self.update_text_preview()
            self.update_status(f"成功添加 {added_count} 个文件。")
        else:
            self.update_status("未添加任何新文件。")

    def _add_file(self, file_path):
        """添加单个文件（不做类型过滤，仅防重复）"""
        if file_path in self.file_paths:
            return False

        self.file_paths.append(file_path)
        self.file_listbox.insert(tk.END, os.path.basename(file_path))
        return True

    def _add_directory(self, dir_path):
        """递归添加文件夹内的所有文件"""
        count = 0
        for root, dirs, files in os.walk(dir_path):
            # 不再过滤目录，遍历所有子目录
            for file in files:
                file_path = os.path.join(root, file)
                if self._add_file(file_path):
                    count += 1
        return count

    def sort_files(self):
        """按文件名对文件列表进行排序"""
        if len(self.file_paths) <= 1:
            return

        self.file_paths.sort(key=lambda x: os.path.basename(x).lower())
        self.update_file_listbox()
        self.update_text_preview()
        self.update_status("文件列表已按名称排序。")

    def reverse_files(self):
        """颠倒文件列表顺序"""
        if len(self.file_paths) <= 1:
            return

        self.file_paths.reverse()
        self.update_file_listbox()
        self.update_text_preview()
        self.update_status("文件列表顺序已颠倒。")

    def update_text_preview(self):
        """根据 file_paths 列表重新生成并显示合并后的文本"""
        self.text_preview.config(state=tk.NORMAL)
        self.text_preview.delete("1.0", tk.END)

        final_content = []
        for file_path in self.file_paths:
            # --- 修改部分开始 ---
            # 修改点：直接使用 file_path 获取完整路径，而不使用 basename
            # 原代码: basename = os.path.basename(file_path)
            display_name = file_path

            # 获取后缀名仍然需要用到 basename 或 splitext
            _, ext = os.path.splitext(file_path)
            lang = ext.lstrip(".") if ext else "text"
            # --- 修改部分结束 ---

            # 强制使用 utf-8 读取
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                content = f"[错误] 文件 '{display_name}' 不是有效的 UTF-8 编码文本。"
            except Exception as e:
                content = f"[错误] 无法读取文件 '{display_name}': {e}"

            # 使用 display_name (完整路径) 进行拼接
            formatted_block = (
                f"文件:{display_name}\n````{lang}\n{content}\n````\n\n---\n\n"
            )
            final_content.append(formatted_block)

        self.text_preview.insert("1.0", "".join(final_content))
        self.text_preview.config(state=tk.DISABLED)

    def update_file_listbox(self):
        """根据 file_paths 列表刷新UI列表"""
        self.file_listbox.delete(0, tk.END)
        for path in self.file_paths:
            # UI列表保持显示文件名，方便查看
            self.file_listbox.insert(tk.END, os.path.basename(path))

    def remove_selected_file(self, event=None):
        """移除选中的文件"""
        selected_indices = self.file_listbox.curselection()
        if not selected_indices:
            return

        index = selected_indices[0]
        removed_file = os.path.basename(self.file_paths.pop(index))

        self.update_file_listbox()
        self.update_text_preview()
        self.update_status(f"已移除文件: {removed_file}")

    def _on_key_up(self, event):
        """处理向上方向键"""
        current = self.file_listbox.curselection()
        if current:
            index = current[0]
            if index > 0:
                self.file_listbox.selection_clear(0, tk.END)
                self.file_listbox.selection_set(index - 1)
                self.file_listbox.activate(index - 1)
                self.file_listbox.see(index - 1)
        elif self.file_listbox.size() > 0:
            self.file_listbox.selection_set(0)
            self.file_listbox.activate(0)
        return "break"

    def _on_key_down(self, event):
        """处理向下方向键"""
        current = self.file_listbox.curselection()
        if current:
            index = current[0]
            if index < self.file_listbox.size() - 1:
                self.file_listbox.selection_clear(0, tk.END)
                self.file_listbox.selection_set(index + 1)
                self.file_listbox.activate(index + 1)
                self.file_listbox.see(index + 1)
        elif self.file_listbox.size() > 0:
            self.file_listbox.selection_set(0)
            self.file_listbox.activate(0)
        return "break"

    def reload_all_files(self):
        """手动重新读取所有文件并刷新预览"""
        if not self.file_paths:
            self.update_status("列表为空。")
            return

        self.update_text_preview()
        self.update_status("所有文件已重新读取。")

    def copy_to_clipboard(self):
        """复制预览区内容到剪贴板"""
        self.update_text_preview()

        content = self.text_preview.get("1.0", tk.END).strip()
        if not content:
            self.update_status("内容为空。")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        self.update_status("内容已复制到剪贴板。")

    def save_to_file(self):
        """保存内容到文件"""
        self.update_text_preview()

        content = self.text_preview.get("1.0", tk.END).strip()
        if not content:
            self.update_status("内容为空，无法保存。")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".md",
            filetypes=[
                ("Markdown 文件", "*.md"),
                ("文本文档", "*.txt"),
                ("所有文件", "*.*"),
            ],
            title="保存合并后的文件",
            initialfile="project.md",
        )

        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                self.update_status(f"文件已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("保存失败", f"无法保存文件：\n{e}")
                self.update_status("文件保存失败！")

    def clear_all(self):
        """清空所有内容"""
        self.file_paths.clear()
        self.update_file_listbox()
        self.update_text_preview()
        self.update_status("已全部清除。")

    def update_status(self, message):
        """更新状态栏信息"""
        self.status_label.config(text=message)

    # --- 列表拖拽排序的辅助方法 ---
    def _on_drag_start(self, event):
        widget = event.widget
        self._drag_start_index = widget.nearest(event.y)

    def _on_drag_motion(self, event):
        widget = event.widget
        current_index = widget.nearest(event.y)
        if current_index != self._drag_start_index:
            widget.selection_clear(0, tk.END)
            widget.selection_set(current_index)
            widget.activate(current_index)

    def _on_drop(self, event):
        widget = event.widget
        drop_index = widget.nearest(event.y)

        # 确保初始索引存在（防止拖拽时没有任何选中项的情况）
        if hasattr(self, "_drag_start_index") and drop_index != self._drag_start_index:
            item = self.file_paths.pop(self._drag_start_index)
            self.file_paths.insert(drop_index, item)

            self.update_file_listbox()
            self.update_text_preview()
            self.update_status("文件顺序已更新。")


if __name__ == "__main__":
    root = TkinterDnD.Tk()
    app = TextMergerApp(root)
    root.mainloop()
