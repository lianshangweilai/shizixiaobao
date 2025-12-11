"""API 配置文件
Kie AI Nano Banana Pro API 相关配置
"""

# API 基础配置
API_BASE_URL = "https://api.kie.ai"
API_VERSION = "v1"
MODEL_NAME = "nano-banana-pro"

# 默认生成参数
DEFAULT_PARAMS = {
    "aspect_ratio": "3:4",  # A4 竖版更适合识字小报
    "resolution": "2K",
    "output_format": "png"
}

# 支持的宽高比
SUPPORTED_RATIOS = ["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9", "auto"]

# 支持的分辨率
SUPPORTED_RESOLUTIONS = ["1K", "2K", "4K"]

# 支持的输出格式
SUPPORTED_FORMATS = ["png", "jpg"]

# API 调用配置
REQUEST_TIMEOUT = 30  # 请求超时时间（秒）
POLL_INTERVAL = 3     # 轮询间隔（秒）
TASK_TIMEOUT = 300    # 任务超时时间（秒）
MAX_RETRIES = 3       # 最大重试次数

# 输出配置
DEFAULT_OUTPUT_DIR = "./outputs/"
HISTORY_DIR = "./outputs/history/"

# 提示词配置
PROMPT_TEMPLATE_PATH = "./prompt.md"