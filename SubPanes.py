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

        self.listpane_layout = QVBoxLayout()
        self.setLayout(self.listpane_layout)

        self.button_layout = QHBoxLayout()
        self.listpane_layout.addLayout(self.button_layout)

        self.music_widget = QStackedWidget()
        self.listpane_layout.addWidget(self.music_widget)

        self.music_list_button = QPushButton()
        self.music_list_button.setText("音乐列表")
        self.music_list_button.clicked.connect(lambda: self.music_widget.setCurrentIndex(0))
        self.button_layout.addWidget(self.music_list_button)

        self.favorite_list_button = QPushButton()
        self.favorite_list_button.setText("收藏列表")
        self.favorite_list_button.clicked.connect(lambda: self.music_widget.setCurrentIndex(1))
        self.button_layout.addWidget(self.favorite_list_button)

        self.music_list = QListWidget()
        self.music_list.doubleClicked.connect(self.switch_song)
        for i in range(0, len(self.player.music_list)):
            song = ".".join(self.player.music_list[i].split(".")[:-1])
            item = QListWidgetItem(self.music_list)
            item.setText(song)
        self.update_current_song()
        self.music_widget.addWidget(self.music_list)

        self.favorite_list = QListWidget()
        self.update_favorite()
        self.music_widget.addWidget(self.favorite_list)

        self.info_list = QTableWidget()
        self.info_list.setColumnCount(2)
        self.info_list.setColumnWidth(0, 80)
        self.info_list.setRowCount(len(self.gesture_functions))
        self.info_list.setHorizontalHeaderLabels(['手势', '功能'])
        for i in range(0, len(self.gesture_functions)):
            self.info_list.setItem(i, 0, QTableWidgetItem(self.gesture_functions[i]['gesture']))
            self.info_list.setItem(i, 1, QTableWidgetItem(self.gesture_functions[i]['function']))
        self.listpane_layout.addWidget(self.info_list)

        self.set_rootpath_button = QPushButton()
        self.set_rootpath_button.setText("切换音乐目录")
        self.set_rootpath_button.clicked.connect(self.set_root_path)
        self.listpane_layout.addWidget(self.set_rootpath_button)


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
            path = self.player.favorite[i]
            filename = os.path.basename(path)
            song = ".".join(filename.split(".")[:-1])
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

        self.controlpane_layout = QGridLayout()
        self.controlpane_layout.setColumnStretch(10, 0)
        self.setLayout(self.controlpane_layout)

        self.toggle_button = QPushButton(qtawesome.icon('fa.play', color='#F76677', font=18), "")
        self.toggle_button.setIconSize(QtCore.QSize(30, 30))
        self.toggle_button.clicked.connect(self.toggle_player_status)
        self.controlpane_layout.addWidget(self.toggle_button, 0, 4, 1, 1)

        self.song_label = QLabel()
        self.update_label()
        self.controlpane_layout.addWidget(self.song_label, 0, 0, 1, 3)

        self.previous_button = QPushButton(qtawesome.icon('fa.backward', color="#3FC89C"), "")
        self.previous_button.clicked.connect(self.previous_song)
        self.controlpane_layout.addWidget(self.previous_button, 0, 3, 1, 1)

        self.next_button = QPushButton(qtawesome.icon('fa.forward', color="#3FC89C"), "")
        self.next_button.clicked.connect(self.next_song)
        self.controlpane_layout.addWidget(self.next_button, 0, 5, 1, 1)

        self.volume_down_button = QPushButton(qtawesome.icon('fa.volume-down', color="#3FC89C"), "")
        self.volume_down_button.clicked.connect(self.volume_down)
        self.controlpane_layout.addWidget(self.volume_down_button, 1, 0, 1, 4)

        self.volume_up_button = QPushButton(qtawesome.icon('fa.volume-up', color="#3FC89C"), "")
        self.volume_up_button.clicked.connect(self.volume_up)
        self.controlpane_layout.addWidget(self.volume_up_button, 1, 5, 1, 4)

        self.like_button = QPushButton(qtawesome.icon('fa.star', color="#3FC89C"), "")
        self.update_like_button()
        self.like_button.clicked.connect(self.mark_like)
        self.controlpane_layout.addWidget(self.like_button, 0, 8, 1, 1)


    # 收藏当前歌曲
    def mark_like(self):
        self.player.execute(Command.TOGGLE_FAVORITE)
        self.update_like_button()
        self.new_favorite.emit()


    def update_like_button(self):
        if self.player.is_current_in_favorite():
            self.like_button.setText("取消收藏")
        else:
            self.like_button.setText("收藏")


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
        self.update_like_button()
        self.new_song.emit()


    def previous_song(self):
        self.player.execute(Command.PREVIOUS)
        self.update_label()
        self.update_like_button()
        self.new_song.emit()


    def toggle_player_status(self):
        self.player.execute(Command.TOGGLE)
        self.update_label()
        self.update_like_button()
