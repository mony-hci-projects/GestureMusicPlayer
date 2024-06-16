import sys
import time
import threading
import cv2 as cv
from collections import deque
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import qdarkstyle

from SubPanes import ListPane, MainPane, ControlPane
from GestureRecognizer import Command, GestureRecognizer
from MusicPlayer import MusicPlayer


def readQssFile(file_path):
    with open(file_path, "r", encoding="UTF-8") as f:
        return f.read()


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.player = MusicPlayer('music')
        self.recognizer = GestureRecognizer()

        self.camera_width, self.camera_height = 640, 480
        self.camera = cv.VideoCapture(0, cv.CAP_DSHOW)
        self.camera.set(3, self.camera_width)
        self.camera.set(4, self.camera_height)

        self.init_ui()

        thread = threading.Thread(target=self.show_camera_view)
        thread.setDaemon(True)
        thread.start()


    def init_ui(self):
        # 主窗口基本设定
        self.setWindowTitle("My App")
        self.setFixedSize(1200, 1000)
        self.setWindowOpacity(0.9)
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(int((screen.width() - size.width()) / 2), int((screen.height() - size.height()) / 2))

        # 主窗口布局
        main_layout = QGridLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(5)

        main_widget = QWidget()
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

        # 添加各子窗格
        self.listpane_layout = ListPane(self.player, self.recognizer)
        self.main_pane = MainPane(self.player, self.recognizer)
        self.controlpane_layout = ControlPane(self.player)
        main_layout.addWidget(self.listpane_layout, 0, 0, 90, 20)
        main_layout.addWidget(self.main_pane, 0, 20, 90, 80)
        main_layout.addWidget(self.controlpane_layout, 90, 0, 10, 100)

        # 信号槽绑定
        self.controlpane_layout.new_favorite.connect(self.listpane_layout.update_favorite)
        self.controlpane_layout.new_song.connect(self.main_pane.update_cover)
        self.controlpane_layout.new_song.connect(self.listpane_layout.update_current_song)
        self.listpane_layout.song_switch.connect(self.main_pane.update_cover)
        self.listpane_layout.song_switch.connect(self.controlpane_layout.update_label)


    def execute(self, command: Command):
        match command:
            case Command.TOGGLE:
                self.controlpane_layout.toggle_player_status()
            case Command.NEXT:
                self.controlpane_layout.next_song()
            case Command.PREVIOUS:
                self.controlpane_layout.previous_song()
            case Command.VOLUME_UP:
                self.controlpane_layout.volume_up()
            case Command.VOLUME_DOWN:
                self.controlpane_layout.volume_down()
            case Command.TOGGLE_FAVORITE:
                self.controlpane_layout.mark_like()
            case Command.EXIT:
                self.close()
            case Command.NONE:
                pass
            case x:
                raise TypeError(x, "Expected Command, found:", type(x))


    # 重写窗口关闭逻辑，用于释放播放器资源
    def closeEvent(self, e: QCloseEvent):
        self.player.close()
        self.camera.release()


    def show_camera_view(self):
        # 用于 FPS 统计
        current_time = 0
        previous_time = 0

        # 使用队列存储之前的手势中心位置
        # 这样可以增大左挥手的时间间隔要求，使这个动作更容易做出，提升用户体验
        previous_centers = deque(maxlen=4)
        current_center = (0, 0)
        previous_command = Command.NONE

        while True:
            ret, frame = self.camera.read()
            frame = cv.flip(frame, 1)
            if not ret:
                break

            try:
                landmark = self.recognizer.get_landmark(frame)
                previous_centers.append(current_center)
                last_center = previous_centers.popleft()
                current_center, command = self.recognizer.gesture_recognise(frame, landmark, last_center)
                previous_centers.appendleft(last_center)
                if command != previous_command or command in\
                    [Command.VOLUME_DOWN, Command.VOLUME_UP]:
                    self.execute(command)
                    previous_command = command
            except RuntimeError as e:
                previous_centers.append(current_center)
            except TypeError as e:
                print(type(e), e)
            except ValueError as e:
                print(type(e), e)

            current_time = time.time()
            fps = 1 / (current_time - previous_time)
            previous_time = current_time
            cv.putText(frame, str(int(fps)), (20, 50), cv.FONT_HERSHEY_COMPLEX_SMALL, 2, (0x66, 0xcc, 0xff), thickness=2)

            image_buffer = cv.cvtColor(frame, cv.COLOR_BGR2BGRA)
            image = QImage(image_buffer.data, image_buffer.shape[1], image_buffer.shape[0], QImage.Format_RGB32)
            self.main_pane.update_camera_image(image)
            cv.waitKey(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyqt5"))

    w = MainWindow()
    w.show()

    app.exec_()
