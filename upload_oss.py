import requests
import io
import time
import random
import logging
from PIL import Image
import numpy as np
import torchvision.transforms.functional as F

# 配置日志
logger = logging.getLogger("comfyui-upload-oss")
logger.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)


class UploadToOSS:
    """上传图片到OSS存储"""

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "oss_put_url": ("STRING", {"multiline": False}),
                "image": ("IMAGE",)
            },
        }

    RETURN_TYPES = ("BOOLEAN",)
    FUNCTION = "upload"
    CATEGORY = "utils"

    def upload(self, oss_put_url, image):
        """执行上传操作"""
        if not oss_put_url:
            raise ValueError("OSS上传地址不能为空")

        try:
            # 将Tensor转换为PIL Image
            pil_image = self._tensor_to_pil(image)

            # 创建内存缓冲区
            buffer = io.BytesIO()
            pil_image.save(buffer, format="PNG")
            buffer.seek(0)

            # 执行上传
            success, message = self._upload_to_oss(oss_put_url, buffer)

            if not success:
                raise Exception(f"上传失败: {message}")

            return (True,)

        except Exception as e:
            logger.error(f"上传过程发生错误: {str(e)}")
            raise

    def _tensor_to_pil(self, image) -> Image.Image:
        """将ComfyUI的Tensor图像转换为PIL Image"""
        # 检查并调整shape
        if image.ndim == 4:
            # (B, C, H, W) 或 (B, H, W, C)
            if image.shape[1] in [1, 3, 4]:  # (B, C, H, W)
                img_tensor = image[0]
            elif image.shape[-1] in [1, 3, 4]:  # (B, H, W, C)
                img_tensor = image[0].permute(2, 0, 1)
            else:
                logger.error(f"未知的图片shape: {image.shape}")
                return (image,)
        elif image.ndim == 3:
            # (C, H, W) 或 (H, W, C)
            if image.shape[0] in [1, 3, 4]:  # (C, H, W)
                img_tensor = image
            elif image.shape[-1] in [1, 3, 4]:  # (H, W, C)
                img_tensor = image.permute(2, 0, 1)
            else:
                logger.error(f"未知的图片shape: {image.shape}")
                return (image,)
        else:
            logger.error(f"未知的图片shape: {image.shape}")
            raise ValueError(f"未知的图片shape: {image.shape}")
        # 转为PIL Image
        return F.to_pil_image(img_tensor)

    def _upload_to_oss(self, oss_put_url, buffer):
        """执行实际的OSS上传"""
        for attempt in range(3):
            try:
                logger.info(f"[upload_to_oss] (第{attempt + 1}/3次) 上传到 OSS: {oss_put_url}")

                # 设置请求超时时间（秒）
                request_timeout = 60

                # 发送PUT请求到OSS
                response = requests.put(
                    oss_put_url,
                    data=buffer,
                    timeout=request_timeout
                )

                # 检查HTTP状态码
                response.raise_for_status()

                logger.info(f"上传OSS完成：{oss_put_url}")
                return True, "success"

            except Exception as e:
                logger.error(f"[upload_to_oss] 上传到 OSS 失败：{e}", exc_info=True)

                # 指数退避策略
                # wait_time = (2 ** attempt) + random.uniform(0, 1)
                # logger.info(f"[upload_to_oss] 等待 {wait_time:.2f} 秒后重试...")
                time.sleep(2)

                # 重置缓冲区指针
                buffer.seek(0)

        return False, "多次尝试上传失败"
