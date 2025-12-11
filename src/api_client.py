"""API 客户端模块
用于与 Kie AI 的 Nano Banana Pro API 进行交互
"""

import time
import json
import requests
from typing import Dict, Optional, List, Any
from tqdm import tqdm
import os


class APIClient:
    """Kie AI API 客户端"""

    def __init__(self, api_key: str):
        """
        初始化 API 客户端

        Args:
            api_key: API 密钥
        """
        self.api_key = api_key
        self.base_url = "https://api.kie.ai"
        self.api_version = "v1"
        self.model_name = "nano-banana-pro"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    def create_task(self, prompt: str, **kwargs) -> Dict[str, Any]:
        """
        创建图像生成任务

        Args:
            prompt: 图像生成提示词
            **kwargs: 其他参数（aspect_ratio, resolution, output_format, image_input, callback_url）

        Returns:
            API 响应数据

        Raises:
            Exception: 当 API 调用失败时
        """
        # 设置默认参数
        params = {
            "model": self.model_name,
            "input": {
                "prompt": prompt,
                "aspect_ratio": kwargs.get("aspect_ratio", "3:4"),  # A4 竖版
                "resolution": kwargs.get("resolution", "2K"),
                "output_format": kwargs.get("output_format", "png"),
                "image_input": kwargs.get("image_input", [])
            }
        }

        # 添加回调 URL（如果提供）
        if "callback_url" in kwargs:
            params["callBackUrl"] = kwargs["callback_url"]

        # 发送请求
        url = f"{self.base_url}/api/{self.api_version}/jobs/createTask"

        try:
            response = requests.post(url, headers=self.headers, json=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to create task: {str(e)}"
            if e.response:
                error_msg += f"\nResponse: {e.response.text}"
            raise Exception(error_msg)

    def query_task(self, task_id: str) -> Dict[str, Any]:
        """
        查询任务状态

        Args:
            task_id: 任务 ID

        Returns:
            API 响应数据

        Raises:
            Exception: 当 API 调用失败时
        """
        url = f"{self.base_url}/api/{self.api_version}/jobs/recordInfo"
        params = {"taskId": task_id}

        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            error_msg = f"Failed to query task: {str(e)}"
            if e.response:
                error_msg += f"\nResponse: {e.response.text}"
            raise Exception(error_msg)

    def wait_for_completion(
        self,
        task_id: str,
        timeout: int = 300,
        poll_interval: int = 3,
        show_progress: bool = True
    ) -> Dict[str, Any]:
        """
        等待任务完成

        Args:
            task_id: 任务 ID
            timeout: 超时时间（秒）
            poll_interval: 轮询间隔（秒）
            show_progress: 是否显示进度条

        Returns:
            任务结果数据

        Raises:
            Exception: 当任务失败或超时时
        """
        start_time = time.time()

        # 初始化进度条
        if show_progress:
            pbar = tqdm(
                total=100,
                desc="Generating image",
                unit="%",
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]"
            )
            pbar.update(0)

        try:
            while True:
                # 检查超时
                if time.time() - start_time > timeout:
                    raise Exception(f"Task timeout after {timeout} seconds")

                # 查询任务状态
                result = self.query_task(task_id)

                if result["code"] != 200:
                    raise Exception(f"API returned error code {result['code']}: {result.get('msg', 'Unknown error')}")

                data = result["data"]
                state = data.get("state", "waiting")

                # 更新进度条（估算）
                if show_progress:
                    if state == "waiting":
                        pbar.update(1)
                        if pbar.n < 30:
                            pbar.n = 30
                    elif state == "success":
                        pbar.update(100 - pbar.n)
                    else:
                        # 处理中状态
                        if pbar.n < 90:
                            pbar.update(1)

                # 检查任务状态
                if state == "success":
                    if show_progress:
                        pbar.close()
                    return result
                elif state == "fail":
                    if show_progress:
                        pbar.close()
                    fail_code = data.get("failCode", "Unknown")
                    fail_msg = data.get("failMsg", "Task failed")
                    raise Exception(f"Task failed with code {fail_code}: {fail_msg}")

                # 等待后继续轮询
                time.sleep(poll_interval)

        except KeyboardInterrupt:
            if show_progress and pbar:
                pbar.close()
            raise Exception("Task interrupted by user")
        except Exception as e:
            if show_progress and pbar:
                pbar.close()
            raise

    def generate_image(
        self,
        prompt: str,
        output_path: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        生成图像的完整流程

        Args:
            prompt: 图像生成提示词
            output_path: 输出文件路径（如果为 None，则自动生成）
            **kwargs: 其他参数

        Returns:
            生成的图像文件路径
        """
        print("Creating generation task...")
        # 创建任务
        task_result = self.create_task(prompt, **kwargs)
        task_id = task_result["data"]["taskId"]
        print(f"Task created with ID: {task_id}")

        # 等待任务完成
        print("Waiting for task completion...")
        completion_result = self.wait_for_completion(task_id)

        # 获取图像 URL
        data = completion_result["data"]
        result_json = json.loads(data["resultJson"])
        image_urls = result_json.get("resultUrls", [])

        if not image_urls:
            raise Exception("No image URLs in result")

        # 下载图像
        image_url = image_urls[0]
        if output_path is None:
            # 自动生成文件名
            output_dir = kwargs.get("output_dir", "./outputs/")
            os.makedirs(output_dir, exist_ok=True)
            timestamp = int(time.time())
            filename = f"generated_{timestamp}.png"
            output_path = os.path.join(output_dir, filename)

        print(f"Downloading image to: {output_path}")
        self._download_image(image_url, output_path)
        print("Image downloaded successfully!")

        return output_path

    def _download_image(self, url: str, output_path: str):
        """
        下载图像文件

        Args:
            url: 图像 URL
            output_path: 输出文件路径
        """
        try:
            response = requests.get(url, stream=True)
            response.raise_for_status()

            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to download image: {str(e)}")

    def get_task_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取任务历史（如果 API 支持）

        Args:
            limit: 返回的任务数量限制

        Returns:
            任务列表
        """
        # 注意：根据 API 文档，没有直接获取历史记录的接口
        # 这里只是一个占位符实现
        print("Warning: Task history is not supported by the current API")
        return []