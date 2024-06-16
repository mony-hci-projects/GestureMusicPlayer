## 项目架构

- 主界面：使用 PyQt5 绘制界面
- 音乐播放模块：使用 Pygame 模块控制音乐播放
- 手势识别模块：使用 mediapipe 进行手势识别

## 项目依赖

- 开发环境：Python3.10.5
- 依赖包：PyQt5 pygame mediapipe opencv-python qtawesome

## 音乐播放器主要功能

播放 | 暂停
上一首 | 下一首
增加音量 | 降低音量
收藏 | 取消收藏
关闭应用

## 待删

pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)

在音乐播放完成时，用事件的方式通知用户程序，设置当音乐播放完成时发送pygame.USEREVENT+1事件给用户程序。

 

pygame.mixer.music.queue(filename)

使用指定下一个要播放的音乐文件，当前的音乐播放完成后自动开始播放指定的下一个。一次只能指定一个等待播放的音乐文件。

要循环播放音频，可以使用pygame.mixer.music.play()函数的可选参数-1。例如，pygame.mixer.music.play(-1)将使音频无限循环播放。
