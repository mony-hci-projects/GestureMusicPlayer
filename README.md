# 一个基于手势识别的音乐播放器

同济大学 2023-2024 学年春季学期人机交互技术期末项目。

## 项目架构

本项目主要包含以下三个模块：

- 用户界面：程序使用 PyQt5 绘制界面，并使用 qdarkstyle 库和 qtawesome 库完成界面美化；
- 音乐播放模块：本程序使用 Pygame 库控制音乐播放，并使用 mutagen 库和 PIL 库完成对音乐封面的提取与处理；
- 手势识别模块：本程序主要使用 mediapipe 进行手势识别，并借助 opencv-python 库处理视频流、获取摄像头实时数据。

项目文件组织如下：
- `main.py`：项目入口文件，用于建立程序主窗口；
- `SubPanes.py`：用户界面各子窗格实现；
- `MusicPlayer.py`：音乐播放模块；
- `GestureRecognizer.py`：手势识别模块；
- `fingersVector.py`：分析手部关节点位置关系所需的数学处理函数。

另外程序运行时会产生如下文件和文件夹，请勿删改：
- `music/`：音乐文件所在目录；
- `pictures/`：用于存放音乐默认封面和程序运行产生的临时图片；
- `favorite.pickle`：用于存储用户收藏。

## 项目依赖

- 开发环境：Python3.10.5
- 依赖包：PyQt5 pygame mediapipe opencv-python mutagen qtawesome qdarkstyle

## 如何运行

首先可以使用 `conda create -n player python=3.10` 建立 Python3.10 的虚拟环境，然后使用 `pip install PyQt5 pygame mediapipe opencv-python mutagen qtawesome qdarkstyle` 安装程序运行需要的包。

完成环境配置后，使用 `python main.py` 启动程序入口文件，即可开始运行程序。

## 音乐播放器主要功能

如下功能均支持手势操作：

- 音乐的播放与暂停
- 切换播放的音乐
- 调节音量
- 收藏与取消收藏音乐
- 关闭应用

