# ComfyUI_upload_oss

这是一个用于ComfyUI的自定义节点，允许将生成的图像直接上传到阿里云OSS存储。

## 功能说明

该节点提供以下功能：
- 将ComfyUI中的Tensor类型图像转换为可上传格式
- 通过指定的OSS上传地址将图像上传到OSS
- 提供上传成功/失败的布尔输出
- 实现了重试机制和错误处理

## 安装方法

1. 进入ComfyUI的custom_nodes目录
2. 克隆本项目：`git clone https://github.com/yourusername/ComfyUI_upload_oss.git`
3. 安装依赖：`pip install requests pillow`
4. 重启ComfyUI

## 使用方法

1. 在ComfyUI工作流中添加"上传到OSS"节点
2. 提供有效的OSS上传地址（PUT URL）
3. 连接需要上传的图像
4. 执行工作流，节点会显示上传结果

## 节点参数

- `oss_put_url`: OSS的PUT类型上传地址
- `image`: ComfyUI中的Tensor类型图像

## 输出结果

- 布尔值：上传成功为True，失败为False

## 注意事项

- 请确保提供的OSS上传地址有效且具有写入权限
- 节点会自动处理图像格式转换
- 上传过程中会显示详细的日志信息
- 实现了3次重试机制和指数退避策略
    