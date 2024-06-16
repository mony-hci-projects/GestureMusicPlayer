# 一个基于手势识别的音乐播放器

同济大学 2023-2024 学年春季学期人机交互技术期末项目。

## 项目架构

本项目主要包含以下三个模块：

- 用户界面：程序使用 PyQt5 绘制界面，并使用 qdarkstyle 库和 qtawesome 库完成界面美化；
- 音乐播放模块：本程序使用 Pygame 库控制音乐播放，并使用 mutagen 库和 PIL 库完成对音乐封面的提取与处理；
- 手势识别模块：本程序主要使用 mediapipe 进行手势识别，并借助 opencv-python 库处理视频流、获取摄像头实时数据。

## 项目依赖

- 开发环境：Python3.10.5
- 依赖包：PyQt5 pygame mediapipe opencv-python mutagen qtawesome qdarkstyle

## 音乐播放器主要功能

如下功能均支持手势操作：

- 音乐的播放与暂停
- 切换播放的音乐
- 调节音量
- 收藏与取消收藏音乐
- 关闭应用

