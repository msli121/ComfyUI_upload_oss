from .upload_oss import UploadToOSS

NODE_CLASS_MAPPINGS = {
    "upload_oss": UploadToOSS
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "upload_oss": "上传到OSS"
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']    