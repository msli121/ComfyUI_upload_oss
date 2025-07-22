import requests
import io
import time
import random
import logging
from PIL import Image
import numpy as np

# 配置日志
log = logging.getLogger("comfyui-upload-oss")
log.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch = logging.StreamHandler()
ch.setFormatter(formatter)
log.addHandler(ch)

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
            log.error(f"上传过程发生错误: {str(e)}")
            raise
    
    def _tensor_to_pil(self, tensor):
        """将ComfyUI的Tensor图像转换为PIL Image"""
        # 转换为numpy数组并调整维度
        img = 255. * tensor.cpu().numpy()
        img = img.astype(np.uint8)
        img = np.transpose(img, (0, 2, 3, 1))[0]
        return Image.fromarray(img)
    
    def _upload_to_oss(self, oss_put_url, buffer):
        """执行实际的OSS上传"""
        for attempt in range(3):
            try:
                log.info(f"[upload_to_oss] (第{attempt + 1}/3次) 上传到 OSS: {oss_put_url}")
                
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
                
                log.info(f"上传OSS完成：{oss_put_url}")
                return True, "success"
                
            except Exception as e:
                log.error(f"[upload_to_oss] 上传到 OSS 失败：{e}", exc_info=True)
                
                # 指数退避策略
                wait_time = (2 ** attempt) + random.uniform(0, 1)
                log.info(f"[upload_to_oss] 等待 {wait_time:.2f} 秒后重试...")
                time.sleep(wait_time)
                
                # 重置缓冲区指针
                buffer.seek(0)
                
        return False, "多次尝试上传失败"    