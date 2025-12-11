"""提示词生成器模块
基于 prompt.md 模板生成完整的 AI 绘图提示词
"""

from typing import Tuple
from .vocabulary import VocabularyManager


class PromptGenerator:
    """提示词生成器"""

    def __init__(self):
        """初始化提示词生成器"""
        self.vocab_manager = VocabularyManager()

    def generate_prompt(
        self,
        theme: str,
        title: str,
        preview: bool = False
    ) -> str:
        """
        生成儿童识字小报的提示词

        Args:
            theme: 主题/场景
            title: 小报标题
            preview: 是否只预览而不填充词汇

        Returns:
            完整的提示词
        """
        # 获取场景词汇
        if preview:
            core_items = "[待生成]"
            common_items = "[待生成]"
            env_items = "[待生成]"
        else:
            core_items, common_items, env_items = self.vocab_manager.format_vocabulary_for_prompt(theme)

        # 提示词模板
        prompt_template = f"""请生成一张儿童识字小报《{theme}》，竖版 A4，学习小报版式，适合 5–9 岁孩子 认字与看图识物。

# 一、小报标题区（顶部）

**顶部居中大标题**：《{title}》
* **风格**：十字小报 / 儿童学习报感
* **文本要求**：大字、醒目、卡通手写体、彩色描边
* **装饰**：周围添加与 {theme} 相关的贴纸风装饰，颜色鲜艳

# 二、小报主体（中间主画面）

画面中心是一幅 **卡通插画风的「{theme}」场景**：
* **整体气氛**：明亮、温暖、积极
* **构图**：物体边界清晰，方便对应文字，不要过于拥挤。

**场景分区与核心内容**
1.  **核心区域 A（主要对象）**：表现 {theme} 的核心活动。
2.  **核心区域 B（配套设施）**：展示相关的工具或物品。
3.  **核心区域 C（环境背景）**：体现环境特征（如墙面、指示牌等）。

**主题人物**
* **角色**：1 位可爱卡通人物（职业/身份：与 {theme} 匹配）。
* **动作**：正在进行与场景相关的自然互动。

# 三、必画物体与识字清单（Generated Content）

**请务必在画面中清晰绘制以下物体，并为其预留贴标签的位置：**

**1. 核心角色与设施：**
{core_items}

**2. 常见物品/工具：**
{common_items}

**3. 环境与装饰：**
{env_items}

*(注意：画面中的物体数量不限于此，但以上列表必须作为重点描绘对象)*

# 四、识字标注规则

对上述清单中的物体，贴上中文识字标签：
* **格式**：两行制（第一行拼音带声调，第二行简体汉字）。
* **样式**：彩色小贴纸风格，白底黑字或深色字，清晰可读。
* **排版**：标签靠近对应的物体，不遮挡主体。

# 五、画风参数
* **风格**：儿童绘本风 + 识字小报风
* **色彩**：高饱和、明快、温暖 (High Saturation, Warm Tone)
* **质量**：8k resolution, high detail, vector illustration style, clean lines."""

        return prompt_template

    def interactive_generation(self) -> Tuple[str, str, str]:
        """
        交互式生成提示词

        Returns:
            (主题, 标题, 提示词)
        """
        print("\n=== 儿童识字小报生成器 ===")
        print("请按照提示输入信息：\n")

        # 获取主题/场景
        available_scenes = self.vocab_manager.list_scenes()
        print(f"可用场景：{', '.join(available_scenes)}")

        while True:
            theme = input("\n请问这期儿童识字小报的主题/场景是什么？（如：超市、医院、公园）: ").strip()
            if theme:
                break
            print("请输入有效的主题/场景。")

        # 获取标题
        while True:
            title = input("\n请问小报的大标题是什么？（如：《走进超市》《快乐医院》）: ").strip()
            if title:
                # 自动添加书名号（如果没有）
                if not title.startswith("《") and not title.startswith("<"):
                    title = f"《{title}》"
                break
            print("请输入有效的标题。")

        # 生成提示词
        prompt = self.generate_prompt(theme, title)

        return theme, title, prompt

    def preview_prompt(self, theme: str, title: str) -> str:
        """
        预览提示词（不填充具体词汇）

        Args:
            theme: 主题/场景
            title: 小报标题

        Returns:
            预览提示词
        """
        return self.generate_prompt(theme, title, preview=True)

    def validate_theme(self, theme: str) -> bool:
        """
        验证主题是否在词汇库中

        Args:
            theme: 主题名称

        Returns:
            是否有效
        """
        vocab = self.vocab_manager.get_scene_vocabulary(theme)
        return bool(vocab)

    def get_theme_suggestions(self, partial: str = "") -> list:
        """
        获取主题建议

        Args:
            partial: 部分输入（用于自动补全）

        Returns:
            建议的主题列表
        """
        all_scenes = self.vocab_manager.list_scenes()
        if not partial:
            return all_scenes

        suggestions = [
            scene for scene in all_scenes
            if partial.lower() in scene.lower()
        ]
        return suggestions