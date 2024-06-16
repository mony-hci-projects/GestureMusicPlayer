import sys
import time
import threading
import cv2 as cv
import qtawesome
from collections import deque
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt

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

        thread = threading.Thread(target=self.play_video)
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
        main_layout.setSpacing(0)

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


    def play_video(self):
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
                previous_centers.clear()
                current_center = (0, 0)
            except TypeError as e:
                print(type(e), e)

            current_time = time.time()
            fps = 1 / (current_time - previous_time)
            previous_time = current_time
            cv.putText(frame, str(int(fps)), (20, 50), cv.FONT_HERSHEY_COMPLEX_SMALL, 2, (0x66, 0xcc, 0xff), thickness=2)

            image_buffer = cv.cvtColor(frame, cv.COLOR_BGR2BGRA)
            image = QImage(image_buffer.data, image_buffer.shape[1], image_buffer.shape[0], QImage.Format_RGB32)
            self.main_pane.update_camera_image(image)
            cv.waitKey(1)


# 歌单窗格
class ListPane(QFrame):
    song_switch = QtCore.pyqtSignal()

    def __init__(self, player, recognizer):
        super(ListPane, self).__init__()
        self.player = player
        self.gesture_functions = recognizer.gesture_functions

        listpane_layout = QVBoxLayout()
        self.setLayout(listpane_layout)

        self.music_list = QListWidget()
        self.music_list.doubleClicked.connect(self.switch_song)
        for i in range(0, len(player.music_list)):
            song = ".".join(player.music_list[i].split(".")[:-1])
            item = QListWidgetItem(self.music_list)
            item.setText(song)
        self.update_current_song()

        listpane_layout.addWidget(self.music_list)

        self.favorite_list = QListWidget()
        for i in range(0, len(player.favorite)):
            song = ".".join(player.favorite[i].split(".")[:-1])
            item = QListWidgetItem(self.favorite_list)
            item.setText(song)

        listpane_layout.addWidget(self.favorite_list)

        # TODO: 所有歌曲与收藏歌曲占用同一窗格，需要切换
        # 使用 QStackedLayout 和 setCurrentIndex （test.py right_layout）

        info_list = QTableWidget()
        info_list.setColumnCount(2)
        info_list.setColumnWidth(0, 80)
        info_list.setRowCount(len(self.gesture_functions))
        info_list.setHorizontalHeaderLabels(['手势', '功能'])
        for i in range(0, len(self.gesture_functions)):
            info_list.setItem(i, 0, QTableWidgetItem(self.gesture_functions[i]['gesture']))
            info_list.setItem(i, 1, QTableWidgetItem(self.gesture_functions[i]['function']))

        listpane_layout.addWidget(info_list)


    def switch_song(self):
        item = QListWidgetItem(self.music_list.currentItem())
        print(item.text())
        song_id = self.music_list.currentRow()
        self.player.switch_to(song_id)
        self.song_switch.emit()


    def update_current_song(self):
        self.music_list.setCurrentRow(self.player.music_id)


    def update_favorite(self):
        self.favorite_list.clear()
        for i in range(0, len(self.player.favorite)):
            song = ".".join(self.player.favorite[i].split(".")[:-1])
            item = QListWidgetItem(self.favorite_list)
            item.setText(song)


# 用于显示摄像头画面和其他歌曲信息的主窗格
class MainPane(QFrame):
    def __init__(self, player, recognizer):
        super(MainPane, self).__init__()
        self.player = player

        self.layout = QGridLayout()
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.setLayout(self.layout)

        self.cover_label = QLabel()
        self.update_cover()

        self.layout.addWidget(self.cover_label, 0, 0, 2, 2)

        self.camera_label = QLabel()

        self.layout.addWidget(self.camera_label, 3, 0, 6, 8)

    def update_cover(self):
        self.cover_label.setPixmap(self.player.get_current_cover())


    def update_camera_image(self, image):
        self.camera_label.setPixmap(QPixmap.fromImage(image))
        self.camera_label.resize(image.size())
        self.camera_label.show()


# 设置窗格，用于放置各功能按钮
class ControlPane(QFrame):
    new_favorite = QtCore.pyqtSignal()
    new_song = QtCore.pyqtSignal()

    def __init__(self, player):
        super(ControlPane, self).__init__()
        self.player = player

        controlpane_layout = QGridLayout()
        controlpane_layout.setColumnStretch(10, 0)
        self.setLayout(controlpane_layout)

        self.toggle_button = QPushButton(qtawesome.icon('fa.play', color='#F76677', font=18), "")
        self.toggle_button.setIconSize(QtCore.QSize(30, 30))
        self.toggle_button.clicked.connect(self.toggle_player_status)

        controlpane_layout.addWidget(self.toggle_button, 0, 4, 1, 1)

        self.song_label = QLabel()
        self.update_label()

        controlpane_layout.addWidget(self.song_label, 0, 0, 1, 3)

        previous_button = QPushButton()
        previous_button.setText("previous")
        previous_button.clicked.connect(self.previous_song)

        controlpane_layout.addWidget(previous_button, 0, 3, 1, 1)

        next_button = QPushButton()
        next_button.setText("next")
        next_button.clicked.connect(self.next_song)

        controlpane_layout.addWidget(next_button, 0, 5, 1, 1)

        self.volume_down_button = QPushButton()
        self.volume_down_button.setText("volume down")
        self.volume_down_button.clicked.connect(self.volume_down)

        controlpane_layout.addWidget(self.volume_down_button, 1, 0, 1, 4)

        self.volume_up_button = QPushButton()
        self.volume_up_button.setText("volume up")
        self.volume_up_button.clicked.connect(self.volume_up)

        controlpane_layout.addWidget(self.volume_up_button, 1, 5, 1, 4)

        like_button = QPushButton()
        like_button.setText("like")
        like_button.clicked.connect(self.mark_like)

        controlpane_layout.addWidget(like_button, 0, 8, 1, 1)


    def mark_like(self):
        self.player.execute(Command.TOGGLE_FAVORITE)
        self.new_favorite.emit()


    def update_label(self):
        self.song_label.setText(self.player.music_list[self.player.music_id])
        if self.player.get_busy():
            self.toggle_button.setIcon(qtawesome.icon('fa.pause', color='#3FC89C', font=18))
        else:
            self.toggle_button.setIcon(qtawesome.icon('fa.play', color='#F76677', font=18))


    def volume_up(self):
        self.player.execute(Command.VOLUME_UP)


    def volume_down(self):
        self.player.execute(Command.VOLUME_DOWN)


    def next_song(self):
        self.player.execute(Command.NEXT)
        self.update_label()
        self.new_song.emit()


    def previous_song(self):
        self.player.execute(Command.PREVIOUS)
        self.update_label()
        self.new_song.emit()


    def toggle_player_status(self):
        self.player.execute(Command.TOGGLE)
        self.update_label()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    w = MainWindow()
    w.show()

    app.exec_()
