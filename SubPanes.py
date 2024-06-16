import os
import qtawesome
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.QtCore import Qt

from GestureRecognizer import Command


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
            path = self.player.favorite[i]
            filename = os.path.basename(path)
            song = ".".join(filename.split(".")[:-1])
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

        set_rootpath_button = QPushButton()
        set_rootpath_button.setText("切换音乐目录")
        set_rootpath_button.clicked.connect(self.set_root_path)

        listpane_layout.addWidget(set_rootpath_button)


    def set_root_path(self):
        root_path = QFileDialog.getExistingDirectory(self, '选择文件夹', './')
        if root_path:
            self.player.set_root_path(root_path)
            self.music_list.clear()
            for i in range(0, len(self.player.music_list)):
                song = ".".join(self.player.music_list[i].split(".")[:-1])
                item = QListWidgetItem(self.music_list)
                item.setText(song)
            self.update_current_song()
            self.repaint()


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
        cover = self.player.get_current_cover()
        if cover:
            self.cover_label.setPixmap(cover)


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
        if self.player.music_id < 0:
            return
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

