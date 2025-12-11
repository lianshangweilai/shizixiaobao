"""词汇数据库模块
用于管理不同场景下的中文词汇及其拼音
"""

import json
import os
from typing import Dict, List, Tuple


class VocabularyManager:
    """词汇管理器"""

    def __init__(self):
        self.vocabulary_data = self._load_vocabulary_data()

    def _load_vocabulary_data(self) -> Dict[str, Dict[str, List[Tuple[str, str]]]]:
        """加载词汇数据"""
        vocabulary = {
            "超市": {
                "人物": [
                    ("shōu yín yuán", "收银员"),
                    ("gù kè", "顾客"),
                    ("bǎo ān", "保安"),
                    ("lǐ huò yuán", "理货员"),
                ],
                "物品": [
                    ("huò jià", "货架"),
                    ("tuī chē", "推车"),
                    ("lán zi", "篮子"),
                    ("shāng pǐn", "商品"),
                    ("jì jià qiāo", "计价器"),
                    ("bāo zhuāng", "包装"),
                    ("píng guǒ", "苹果"),
                    ("niú nǎi", "牛奶"),
                    ("miàn bāo", "面包"),
                ],
                "设施": [
                    ("chū kǒu", "出口"),
                    ("rù kǒu", "入口"),
                    ("shōu yín tái", "收银台"),
                    ("cùn bāo guì", "储物柜"),
                    ("yín xíng kǎ", "银行卡"),
                ],
                "环境": [
                    ("zhāo pái", "招牌"),
                    ("dēng", "灯"),
                    ("qiáng", "墙"),
                    ("dì bǎn", "地板"),
                    ("chuāng", "窗"),
                ]
            },
            "医院": {
                "人物": [
                    ("yī shēng", "医生"),
                    ("hù shì", "护士"),
                    ("bìng rén", "病人"),
                    ("yào jì shī", "药剂师"),
                ],
                "物品": [
                    ("yào pǐn", "药品"),
                    ("yì zhēn", "针"),
                    ("tǐ wēn jì", "体温计"),
                    ("yī xiè", "器械"),
                    ("chuáng", "床"),
                    ("bìng lì", "病历"),
                    ("chā piàn", "卡片"),
                ],
                "设施": [
                    ("zhěn suǒ", "诊所"),
                    ("guà hào chù", "挂号处"),
                    ("yào fáng", "药房"),
                    ("jí jiù shì", "急救室"),
                    ("hù shì zhàn", "护士站"),
                ],
                "环境": [
                    ("zǒu láng", "走廊"),
                    ("dēng", "灯"),
                    ("chāng", "窗"),
                    ("mén", "门"),
                    ("zhǐ jiǔ", "纸巾"),
                ]
            },
            "公园": {
                "人物": [
                    ("lǎo rén", "老人"),
                    ("xiǎo hái", "小孩"),
                    ("qīng nián", "青年"),
                    ("jiān líng yuán", "清洁员"),
                ],
                "物品": [
                    ("huā", "花"),
                    ("shù", "树"),
                    ("yǐ zi", "椅子"),
                    ("zhuō zi", "桌子"),
                    ("qiū qiān", "秋千"),
                    ("huá tī", "滑梯"),
                    ("mǎ", "马"),
                    ("niǎo", "鸟"),
                ],
                "设施": [
                    (" mén", "门"),
                    ("lù", "路"),
                    ("qiáo", "桥"),
                    ("tíng zi", "亭子"),
                    ("gōng gòng cè suǒ", "公共厕所"),
                ],
                "环境": [
                    ("cǎo dì", "草地"),
                    ("hé", "河"),
                    ("shān", "山"),
                    ("tiān kōng", "天空"),
                    ("yún", "云"),
                ]
            },
            "学校": {
                "人物": [
                    ("lǎo shī", "老师"),
                    ("xué shēng", "学生"),
                    ("xiào zhǎng", "校长"),
                    ("bǎo ān", "保安"),
                ],
                "物品": [
                    ("zhuō zi", "桌子"),
                    ("yǐ zi", "椅子"),
                    ("shū", "书"),
                    ("bǐ", "笔"),
                    ("bǎi bǎn", "白板"),
                    ("fěn bǐ", "粉笔"),
                    ("shū bāo", "书包"),
                    ("wén jù hé", "文具盒"),
                ],
                "设施": [
                    ("jiào shì", "教室"),
                    ("tú shū guǎn", "图书馆"),
                    ("cāo chǎng", "操场"),
                    ("shí táng", "食堂"),
                    ("xiào mén", "校门"),
                ],
                "环境": [
                    ("lóu", "楼"),
                    ("zǒu láng", "走廊"),
                    ("chuāng", "窗"),
                    ("dì", "地"),
                    ("qí gān", "旗杆"),
                ]
            },
            "动物园": {
                "人物": [
                    ("sì yǎng yuán", "饲养员"),
                    ("yóu kè", "游客"),
                    ("xiǎo péng yǒu", "小朋友"),
                    ("xiàng dǎo", "向导"),
                ],
                "物品": [
                    ("wán jù", "玩具"),
                    ("xiāng jī", "相机"),
                    ("shuǐ hú", "水壶"),
                    ("bǐng gān", "饼干"),
                    ("guǎn zi", "罐子"),
                ],
                "设施": [
                    ("lóng zi", "笼子"),
                    ("yăn chū", "演出"),
                    ("cān tīng", "餐厅"),
                    ("mài piào chù", "卖票处"),
                    ("tíng chē chǎng", "停车场"),
                ],
                "环境": [
                    ("shù mù", "树木"),
                    ("huā cǎo", "花草"),
                    ("hú", "湖"),
                    ("shān", "山"),
                    ("dǎo", "岛"),
                ]
            },
            "火车站": {
                "人物": [
                    ("chéng kè", "乘客"),
                    ("sī jī", "司机"),
                    ("liè chè yuán", "列车员"),
                    ("gōng zuò rén yuán", "工作人员"),
                ],
                "物品": [
                    ("xíng li", "行李"),
                    ("piào", "票"),
                    ("bào zhǐ", "报纸"),
                    ("shǒu jī", "手机"),
                    ("shuǐ", "水"),
                ],
                "设施": [
                    ("zhàn tái", "站台"),
                    ("dà tīng", "大厅"),
                    ("děng hòu qū", "等候区"),
                    ("xíng li sòng", "行李输送"),
                    ("xún wèn chù", "询问处"),
                ],
                "环境": [
                    ("tiě guǐ", "铁轨"),
                    ("dà mén", "大门"),
                    ("zhǎo pái", "招牌"),
                    ("shí zhōng", "时钟"),
                    ("lù dēng", "路灯"),
                ]
            },
        }

        # 尝试从外部文件加载额外的词汇数据
        external_data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "config", "vocabulary_data"
        )

        if os.path.exists(external_data_path):
            for filename in os.listdir(external_data_path):
                if filename.endswith(".json"):
                    scene_name = filename[:-5]  # 移除 .json 后缀
                    try:
                        with open(os.path.join(external_data_path, filename), 'r', encoding='utf-8') as f:
                            scene_data = json.load(f)
                            # 将数据转换为正确的格式
                            formatted_data = {}
                            for category, items in scene_data.items():
                                formatted_data[category] = [
                                    (item["pinyin"], item["chinese"])
                                    for item in items
                                ]
                            vocabulary[scene_name] = formatted_data
                    except Exception as e:
                        print(f"Warning: Failed to load vocabulary from {filename}: {e}")

        return vocabulary

    def get_scene_vocabulary(self, scene: str) -> Dict[str, List[Tuple[str, str]]]:
        """获取指定场景的词汇

        Args:
            scene: 场景名称

        Returns:
            词汇字典，包含不同类别的词汇列表
        """
        # 尝试精确匹配
        if scene in self.vocabulary_data:
            return self.vocabulary_data[scene]

        # 尝试模糊匹配
        scene_lower = scene.lower()
        for key, value in self.vocabulary_data.items():
            if scene_lower == key.lower() or scene_lower in key.lower() or key.lower() in scene_lower:
                return value

        # 如果没有找到，返回空字典
        print(f"Warning: Scene '{scene}' not found in vocabulary database.")
        return {}

    def get_vocabulary_list(self, scene: str, limit: int = 20) -> List[Tuple[str, str]]:
        """获取场景的词汇列表（混合所有类别）

        Args:
            scene: 场景名称
            limit: 返回的词汇数量限制

        Returns:
            词汇元组列表 (pinyin, chinese)
        """
        vocab_dict = self.get_scene_vocabulary(scene)
        vocab_list = []

        # 按优先级添加词汇：人物 > 物品 > 设施 > 环境
        categories = ["人物", "物品", "设施", "环境"]
        for category in categories:
            if category in vocab_dict:
                vocab_list.extend(vocab_dict[category])
                if len(vocab_list) >= limit:
                    break

        return vocab_list[:limit]

    def format_vocabulary_for_prompt(self, scene: str) -> Tuple[str, str, str]:
        """格式化词汇用于提示词模板

        Returns:
            (核心角色与设施, 常见物品/工具, 环境与装饰)
        """
        vocab_dict = self.get_scene_vocabulary(scene)

        # 提取不同类别的词汇
        core_items = []
        common_items = []
        env_items = []

        # 优先级分组
        if "人物" in vocab_dict:
            core_items.extend(vocab_dict["人物"][:3])
        if "设施" in vocab_dict:
            core_items.extend(vocab_dict["设施"][:2])
        if "物品" in vocab_dict:
            common_items.extend(vocab_dict["物品"][:8])
        if "环境" in vocab_dict:
            env_items.extend(vocab_dict["环境"][:5])

        # 格式化为字符串
        format_item = lambda items: ", ".join([f"{pinyin} {chinese}" for pinyin, chinese in items])

        return (
            format_item(core_items),
            format_item(common_items),
            format_item(env_items)
        )

    def add_scene(self, scene_name: str, vocabulary_data: Dict[str, List[Tuple[str, str]]]):
        """添加新的场景词汇"""
        self.vocabulary_data[scene_name] = vocabulary_data

    def list_scenes(self) -> List[str]:
        """列出所有可用的场景"""
        return list(self.vocabulary_data.keys())