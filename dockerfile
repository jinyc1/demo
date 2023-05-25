# 使用官方 Python 基础镜像
FROM python:3.8-slim-buster

# 工作目录设置为 /app
WORKDIR /app

# 把当前目录下的所有文件添加到容器的 /app 目录下
ADD . /app

# 使用 pip 命令从 requirements.txt 文件中安装 Python 应用所需要的包
RUN pip install --no-cache-dir -r requirements.txt

# 运行应用所需要的端口
EXPOSE 5000

# 容器启动后执行的命令
CMD ["python", "radius_clear_onlie/clear_api.py"]
