import os
import time
import pygame
import mutagen
import pickle
import threading
from PIL import Image, ImageDraw, ImageFilter
from PyQt5 import QtCore, QtGui
from GestureRecognizer import Command


# 将图片裁剪出一个方形
def crop_max_square(pil_img):
    crop_width = min(pil_img.size)
    crop_height = min(pil_img.size)
    img_width, img_height = pil_img.size
    return pil_img.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))


# 使用蒙版将图片处理为圆形
def mask_circle_transparent(pil_img, blur_radius, offset=0):
    offset = blur_radius * 2 + offset
    mask = Image.new("L", pil_img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((offset, offset, pil_img.size[0] - offset, pil_img.size[1] - offset), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur_radius))

    result = pil_img.copy()
    result.putalpha(mask)
    return result


class MusicPlayer:
    def __init__(self, root_path: str = "."):
        # 设置播放器音乐文件夹目录
        if not os.path.exists(root_path):
            os.mkdir(root_path)
        self.root_path = os.path.abspath(root_path)
        self.music_list = os.listdir(self.root_path)
        self.music_num = len(self.music_list)

        # 加载收藏夹
        if os.path.exists("favorite.pickle"):
            with open("favorite.pickle", "rb") as f:
                self.favorite = pickle.load(f)
        else:
            with open("favorite.pickle", "wb") as f:
                pickle.dump([], f)
            self.favorite = []

        # 初始化音乐播放器
        pygame.mixer.init()
        self.__music_controller = pygame.mixer.music
        self.music_id = 0 if len(self.music_list) > 0 else -1
        self.volume = 3  # pygame 的音乐播放器音乐调节范围为 0.0 到 1.0，为避免浮点运算带来的误差，使用整数并除以十传入 set_volume 方法
        self.is_pausing = True

        thread = threading.Thread(target=self.run)
        thread.setDaemon(True)
        thread.start()


    def set_root_path(self, root_path):
        # 设置播放器音乐文件夹目录
        if not os.path.exists(root_path):
            os.mkdir(root_path)
        self.root_path = os.path.abspath(root_path)
        self.music_list = os.listdir(self.root_path)
        self.music_num = len(self.music_list)
        self.music_id = 0 if len(self.music_list) > 0 else -1


    def run(self):
        while True:
            try:
                time.sleep(0.1)
                if not self.__music_controller.get_busy() and not self.is_pausing:
                    self.next()
            except Exception as e:
                # 由于使用了多线程，可能会在退出程序时出现异常，但不影响程序正常使用
                print(e)


    def play(self):
        self.__music_controller.load(os.path.join(self.root_path, self.music_list[self.music_id]))
        self.__music_controller.play()
        self.is_pausing = False


    def close(self):
        self.__music_controller.fadeout(2)
        self.__music_controller.stop()
        with open("favorite.pickle", "wb") as f:
            pickle.dump(self.favorite, f)


    def next(self):
        self.music_id = (self.music_id + 1) % self.music_num
        self.play()


    def previous(self):
        self.music_id = ((self.music_id - 1) + self.music_num) % self.music_num
        self.play()


    def switch_to(self, song_id):
        self.music_id = song_id % self.music_num
        self.play()


    def get_busy(self):
        return self.__music_controller.get_busy()


    def like_current_song(self):
        current_song = os.path.join(self.root_path, self.music_list[self.music_id])
        if current_song not in self.favorite:
            self.favorite.append(current_song)
        else:
            self.favorite.remove(current_song)


    def is_current_in_favorite(self):
        if self.music_id < 0:
            return False
        current_song = os.path.join(self.root_path, self.music_list[self.music_id])
        return current_song in self.favorite


    def get_current_cover(self):
        try:
            # 歌曲文件可能缺失 APIC 标签(KeyError)或全部标签(TypeError, 因为对不存在的 tags 进行了索引)
            audio = mutagen.File(os.path.join(self.root_path, self.music_list[self.music_id]))
            cover_data = audio.tags['APIC:'].data

            cover_path = "./pictures/origin_cover.png"
            with open(cover_path, "wb") as img:
                img.write(cover_data)

            # 将图片处理为适合作封面的图
            mark_img = Image.open(cover_path)
            trumb_width = 600

            im_square = crop_max_square(mark_img).resize((trumb_width, trumb_width), Image.LANCZOS)
            im_thumb = mask_circle_transparent(im_square, 0)
            im_thumb.save(cover_path)

            pix_img = QtGui.QPixmap(cover_path)
            pix = pix_img.scaled(300, 300, QtCore.Qt.KeepAspectRatio)
            os.remove(cover_path)
            return pix
        except (KeyError, TypeError) as e:
            print(e, type(e))
            pix_img = QtGui.QPixmap('./pictures/default_cover.png')
            pix = pix_img.scaled(300, 300, QtCore.Qt.KeepAspectRatio)
            return pix
        except IndexError:
            print("根目录为空")
            return None


    def execute(self, command: Command) -> int | Command:
        match command:
            case Command.TOGGLE:
                if self.__music_controller.get_busy():
                    self.__music_controller.pause()
                    self.is_pausing = True
                elif self.__music_controller.get_pos() == -1:
                    self.play()
                else:
                    self.__music_controller.unpause()
                    self.is_pausing = False
            case Command.NEXT:
                self.next()
            case Command.PREVIOUS:
                self.previous()
            case Command.VOLUME_UP:
                if self.volume < 10:
                    self.volume += 1
                    self.__music_controller.set_volume(self.volume / 10)
            case Command.VOLUME_DOWN:
                if self.volume > 0:
                    self.volume -= 1
                    self.__music_controller.set_volume(self.volume / 10)
            case Command.TOGGLE_FAVORITE:
                self.like_current_song()
            case Command.EXIT:
                self.close()
            case Command.NONE:
                pass
            case x:
                raise TypeError(x, "Expected Command, found:", type(x))
        print(f"当前音量：{self.volume}; 当前歌曲：{self.music_list[self.music_id]}")
        return self.music_id  # 返回当前歌曲 ID
