"""儿童识字小报生成器 - 主程序
使用 Kie AI Nano Banana Pro API 生成儿童识字海报
"""

import argparse
import sys
import os
from dotenv import load_dotenv
from colorama import init, Fore, Style
from datetime import datetime

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from prompt_generator import PromptGenerator
from api_client import APIClient


def print_banner():
    """打印程序横幅"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║      儿童识字小报生成器 v1.0                                  ║
    ║      基于 Kie AI Nano Banana Pro API                          ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(Fore.CYAN + banner + Style.RESET_ALL)


def print_success(message: str):
    """打印成功消息"""
    print(Fore.GREEN + f"✓ {message}" + Style.RESET_ALL)


def print_error(message: str):
    """打印错误消息"""
    print(Fore.RED + f"✗ {message}" + Style.RESET_ALL)


def print_warning(message: str):
    """打印警告消息"""
    print(Fore.YELLOW + f"⚠ {message}" + Style.RESET_ALL)


def print_info(message: str):
    """打印信息消息"""
    print(Fore.BLUE + f"ℹ {message}" + Style.RESET_ALL)


def save_history(theme: str, title: str, output_path: str):
    """保存生成历史"""
    history_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "outputs", "history")
    os.makedirs(history_dir, exist_ok=True)

    history_file = os.path.join(history_dir, "generation_history.json")

    import json
    from datetime import datetime

    # 读取现有历史
    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        except:
            history = []

    # 添加新记录
    history.append({
        "timestamp": datetime.now().isoformat(),
        "theme": theme,
        "title": title,
        "output_path": output_path
    })

    # 保存历史（最多保留 100 条）
    history = history[-100:]
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def main():
    """主函数"""
    # 初始化 colorama
    init()

    # 加载环境变量
    load_dotenv()

    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description="儿童识字小报生成器 - 使用 AI 生成适合儿童的中文识字海报",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 交互式生成
  python main.py -i

  # 直接指定主题和标题
  python main.py -t 超市 -T "走进超市"

  # 指定输出目录和图片参数
  python main.py -t 医院 -T "快乐医院" -o ./my_outputs/ --ratio 3:4 --resolution 2K

  # 预览提示词
  python main.py -t 公园 -T "美丽的公园" --preview
        """
    )

    parser.add_argument("-i", "--interactive", action="store_true",
                       help="交互式生成模式")
    parser.add_argument("-t", "--theme", type=str,
                       help="主题/场景（如：超市、医院、公园）")
    parser.add_argument("-T", "--title", type=str,
                       help="小报标题（如：走进超市、快乐医院）")
    parser.add_argument("-o", "--output", type=str, default="./outputs/",
                       help="输出目录（默认：./outputs/）")
    parser.add_argument("--ratio", type=str, default="3:4",
                       choices=["1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9", "auto"],
                       help="图片宽高比（默认：3:4）")
    parser.add_argument("--resolution", type=str, default="2K",
                       choices=["1K", "2K", "4K"],
                       help="图片分辨率（默认：2K）")
    parser.add_argument("--format", type=str, default="png",
                       choices=["png", "jpg"],
                       help="图片格式（默认：png）")
    parser.add_argument("--preview", action="store_true",
                       help="只预览提示词，不生成图片")
    parser.add_argument("--list-scenes", action="store_true",
                       help="列出所有可用的场景")
    parser.add_argument("--save-prompt", type=str,
                       help="保存提示词到指定文件")

    args = parser.parse_args()

    # 打印横幅
    print_banner()

    # 检查 API Key
    api_key = os.getenv("KIE_AI_API_KEY")
    if not api_key and not args.preview and not args.list_scenes:
        print_error("未找到 API Key！")
        print_info("请在 .env 文件中设置 KIE_AI_API_KEY=your_api_key_here")
        sys.exit(1)

    # 初始化组件
    prompt_generator = PromptGenerator()

    # 列出可用场景
    if args.list_scenes:
        scenes = prompt_generator.get_theme_suggestions()
        print("\n可用的场景：")
        for i, scene in enumerate(scenes, 1):
            print(f"  {i:2d}. {scene}")
        return

    # 交互式模式
    if args.interactive:
        theme, title, prompt = prompt_generator.interactive_generation()
    else:
        # 参数模式
        if not args.theme or not args.title:
            print_error("请提供主题和标题，或使用 -i 进入交互模式")
            parser.print_help()
            sys.exit(1)

        theme = args.theme
        title = args.title
        if not title.startswith("《") and not title.startswith("<"):
            title = f"《{title}》"

        # 验证主题
        if not prompt_generator.validate_theme(theme):
            print_warning(f"警告：主题 '{theme}' 不在词汇库中，将使用通用词汇")

        # 生成提示词
        prompt = prompt_generator.generate_prompt(theme, title)

    # 保存提示词（如果指定）
    if args.save_prompt:
        try:
            with open(args.save_prompt, 'w', encoding='utf-8') as f:
                f.write(f"# 主题：{theme}\n")
                f.write(f"# 标题：{title}\n")
                f.write(f"# 生成时间：{datetime.now()}\n\n")
                f.write(prompt)
            print_success(f"提示词已保存到：{args.save_prompt}")
        except Exception as e:
            print_error(f"保存提示词失败：{str(e)}")

    # 预览模式
    if args.preview:
        print("\n" + "="*60)
        print(f"主题：{theme}")
        print(f"标题：{title}")
        print("="*60)
        print(prompt)
        return

    # 生成图片
    try:
        print_info(f"\n开始生成儿童识字小报...")
        print_info(f"主题：{theme}")
        print_info(f"标题：{title}")
        print_info(f"图片参数：{args.ratio}, {args.resolution}, {args.format}")

        # 创建 API 客户端
        client = APIClient(api_key)

        # 生成图像
        output_path = client.generate_image(
            prompt=prompt,
            output_dir=args.output,
            aspect_ratio=args.ratio,
            resolution=args.resolution,
            output_format=args.format
        )

        # 保存历史
        save_history(theme, title, output_path)

        print_success(f"\n图片生成成功！")
        print_info(f"输出路径：{output_path}")

        # 显示文件信息
        file_size = os.path.getsize(output_path) / (1024 * 1024)  # MB
        print_info(f"文件大小：{file_size:.2f} MB")

    except KeyboardInterrupt:
        print_error("\n用户中断了生成过程")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n生成失败：{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()