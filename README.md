# 儿童识字小报生成器

基于 Kie AI Nano Banana Pro API 的儿童识字海报生成工具，为 5-9 岁儿童生成中文识字学习海报。

## 功能特点

- 🎨 基于先进的 AI 图像生成技术
- 📚 内置多个常见场景词汇库（超市、医院、公园等）
- 🏷️ 自动生成带拼音标注的识字标签
- 📐 支持 A4 竖版格式，适合打印
- 🎯 专为儿童教育设计的提示词模板
- 💻 简单易用的命令行界面

## 安装指南

### 1. 环境要求

- Python 3.8 或更高版本
- pip 包管理器

### 2. 克隆项目

```bash
git clone https://github.com/yourusername/图片生成器.git
cd 图片生成器
```

### 3. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python -m venv venv
source venv/bin/activate
```

### 4. 安装依赖

```bash
pip install -r requirements.txt
```

### 5. 配置 API Key

1. 访问 [Kie AI API Key 管理页面](https://kie.ai/api-key) 获取 API Key
2. 复制 `.env.example` 文件为 `.env`

```bash
cp .env.example .env
```

3. 编辑 `.env` 文件，替换为您的 API Key：

```env
KIE_AI_API_KEY=your_actual_api_key_here
```

## 使用方法

### 交互式生成

```bash
python src/main.py -i
```

程序会引导您输入：
- 主题/场景
- 小报标题

### 命令行参数生成

```bash
# 基础用法
python src/main.py -t 超市 -T "走进超市"

# 指定输出目录
python src/main.py -t 医院 -T "快乐医院" -o ./my_outputs/

# 指定图片参数
python src/main.py -t 公园 -T "美丽的公园" --ratio 3:4 --resolution 2K
```

### 查看所有可用场景

```bash
python src/main.py --list-scenes
```

### 预览提示词（不生成图片）

```bash
python src/main.py -t 动物园 -T "动物朋友们" --preview
```

### 保存提示词到文件

```bash
python src/main.py -t 火车站 -T "繁忙的车站" --save-prompt prompt.txt
```

## 命令行参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-i, --interactive` | 交互式生成模式 | - |
| `-t, --theme` | 主题/场景（如：超市、医院） | 必需 |
| `-T, --title` | 小报标题 | 必需 |
| `-o, --output` | 输出目录 | `./outputs/` |
| `--ratio` | 图片宽高比 | `3:4` |
| `--resolution` | 图片分辨率（1K/2K/4K） | `2K` |
| `--format` | 图片格式（png/jpg） | `png` |
| `--preview` | 只预览提示词，不生成图片 | - |
| `--list-scenes` | 列出所有可用场景 | - |
| `--save-prompt` | 保存提示词到文件 | - |

## 项目结构

```
图片生成器/
├── src/
│   ├── __init__.py              # 包初始化
│   ├── main.py                  # 主程序入口
│   ├── prompt_generator.py      # 提示词生成器
│   ├── api_client.py            # API 客户端
│   └── vocabulary.py            # 词汇数据库
├── config/
│   └── api_config.py            # API 配置
├── config/vocabulary_data/      # 扩展词汇数据目录
├── outputs/                     # 生成的图片存储
│   └── history/                 # 生成历史记录
├── prompt.md                    # 提示词模板
├── requirements.txt             # Python 依赖
├── .env.example                 # 环境变量示例
└── README.md                    # 说明文档
```

## 内置场景词汇

当前支持的场景包括：

- 🏪 **超市** - 收银员、货架、推车、商品等
- 🏥 **医院** - 医生、护士、药品、病床等
- 🌳 **公园** - 花草、树木、秋千、滑梯等
- 🏫 **学校** - 老师、学生、课桌、黑板等
- 🦁 **动物园** - 各种动物、饲养员、笼子等
- 🚂 **火车站** - 列车、站台、乘客、行李等

## 扩展词汇库

您可以添加自定义场景词汇：

1. 在 `config/vocabulary_data/` 目录下创建 JSON 文件
2. 文件名为场景名称，如 `海滩.json`
3. 内容格式：

```json
{
  "人物": [
    {"pinyin": "yóu yǒng", "chinese": "游泳"},
    {"pinyin": "jiù shēng yuán", "chinese": "救生员"}
  ],
  "物品": [
    {"pinyin": "yùn dòng qi", "chinese": "运动器"},
    {"pinyin": "fáng shài shuǎng", "chinese": "防晒霜"}
  ],
  "设施": [
    {"pinyin": "cháng zi", "chinese": "场子"},
    {"pinyin": "gèng yī shì", "chinese": "更衣室"}
  ],
  "环境": [
    {"pinyin": "hǎi shuǐ", "chinese": "海水"},
    {"pinyin": "shā tān", "chinese": "沙滩"}
  ]
}
```

## 注意事项

1. **API 限制**：请注意 API 调用频率限制和配额使用
2. **生成时间**：图片生成通常需要 30-60 秒
3. **网络要求**：需要稳定的网络连接访问 Kie AI API
4. **内容审核**：生成的内容适合儿童教育，请勿用于不当用途

## 故障排除

### 问题：API Key 未找到
```
✗ 未找到 API Key！
ℹ 请在 .env 文件中设置 KIE_AI_API_KEY=your_api_key_here
```
**解决方案**：确保已正确创建并配置了 `.env` 文件

### 问题：任务生成失败
```
✗ 生成失败：Task failed with code xxx: xxx
```
**解决方案**：
- 检查网络连接
- 验证 API Key 是否有效
- 确认账户余额充足

### 问题：主题不存在
```
⚠ 警告：主题 'xxx' 不在词汇库中，将使用通用词汇
```
**解决方案**：
- 使用 `--list-scenes` 查看可用场景
- 或创建自定义词汇库

## 开发说明

### 代码规范

- 使用 Python 3.8+ 语法特性
- 遵循 PEP 8 编码规范
- 使用类型提示增强代码可读性

### 测试

```bash
# 运行单元测试（如果存在）
python -m pytest tests/
```

## 更新日志

### v1.0.0
- 初始版本发布
- 支持 6 个内置场景
- 实现命令行和交互式两种使用方式
- 支持图片参数自定义

## 许可证

本项目采用 MIT 许可证。

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 GitHub Issue
- 发送邮件至：your-email@example.com

---

**感谢使用儿童识字小报生成器！** 🎉