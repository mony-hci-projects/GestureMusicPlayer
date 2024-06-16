import cv2 as cv
import mediapipe as mp
from enum import Enum, unique, auto
from fingersVector import fingersUp, vectorSize, vectorAngle, mkVector, vectorAngle2

@unique
class Command(Enum):
    # PLAY = auto()
    VOLUME_UP = auto()
    VOLUME_DOWN = auto()
    # PAUSE = auto()
    # RESUME = auto()
    TOGGLE = auto()
    NEXT = auto()
    PREVIOUS = auto()
    # LIKE = auto()
    # UNLIKE = auto()
    TOGGLE_FAVORITE = auto()
    EXIT = auto()
    NONE = auto()

class GestureRecognizer:
    gesture_functions = [
        {"gesture": "V", "function": "播放/暂停", "command": Command.TOGGLE},
        {"gesture": "左挥手", "function": "上一曲", "command": Command.PREVIOUS},
        {"gesture": "右挥手", "function": "下一曲", "command": Command.NEXT},
        {"gesture": "大拇指", "function": "增加音量", "command": Command.VOLUME_UP},
        {"gesture": "握拳", "function": "减少音量", "command": Command.VOLUME_DOWN},
        {"gesture": "比心", "function": "收藏/取消收藏", "command": Command.TOGGLE_FAVORITE},
        {"gesture": "Rock", "function": "关闭", "command": Command.EXIT},
    ]

    def __init__(self):
        # 绘制关键点与连接线函数
        self.mp_drawing = mp.solutions.drawing_utils
        self.handMsStyle=self.mp_drawing.DrawingSpec(color=(0,0,255),thickness=int(5))#关键点样式
        self.handConStyle=self.mp_drawing.DrawingSpec(color=(0,255,0),thickness=int(8))#关键点连接线样式
        #手部检测函数
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(static_image_mode=False,#检测的是视频流还是静态图片，False为视频流，True为图片
                                         max_num_hands=1,#检测出手的最大数量
                                         min_detection_confidence=0.75,#首部检测的最小置信度，大于该值则认为检测成功
                                         min_tracking_confidence=0.75)#目标跟踪模型的最小置信度


    def gesture_recognise(self, frame, landmark, previous_center) -> Command:
        # 静态手势识别
        command = self.__static_gesture_recognise(landmark)

        # 动态手势识别
        current_center = landmark[9]
        cv.circle(frame, current_center, 10, (0, 255, 255), -1)
        center_vector = mkVector(current_center, previous_center)
        current_previous_distance = vectorSize(previous_center, current_center)
        x_axis = (1, 0)
        angle = vectorAngle2(center_vector, x_axis)
        if center_vector[0] > 0 and current_previous_distance > 180 and angle < 30:
            command = Command.NEXT
        elif center_vector[0] < 0 and current_previous_distance > 180 and angle > 150:
            command = Command.PREVIOUS

        return current_center, command


    def __static_gesture_recognise(self, landmark) -> Command:
        command = Command.NONE
        fingers_status = fingersUp(landmark)
        # if (fingers_status[0] == 0 and fingers_status[1] == 0 and fingers_status[2] == 1 and fingers_status[3] == 1 and fingers_status[4] == 1):
        #     command = Command.TOGGLE
        #     print("OK")
        if (fingers_status[0] == 0 and fingers_status[1] == 1 and fingers_status[2] == 1 and fingers_status[3] == 0 and fingers_status[4] == 0):
            command = Command.TOGGLE
            print("V")
        elif(fingers_status[0]==1 and fingers_status[1]==0 and fingers_status[2]==0 and fingers_status[3]==0 and fingers_status[4]==0):
            command = Command.VOLUME_UP
            print("大拇指")
        elif(fingers_status[0]==0 and fingers_status[1]==0 and fingers_status[2]==0 and fingers_status[3]==0 and fingers_status[4]==0):
            command = Command.VOLUME_DOWN
            print("握拳")
        elif (fingers_status[0] == 0 and fingers_status[1] == 1 and fingers_status[2] == 0 and fingers_status[3] == 0 and fingers_status[4] == 1):
            command = Command.EXIT
            print("Rock")
        elif (fingers_status[0] == 1 and fingers_status[1] == 1 and fingers_status[2] == 0 and fingers_status[3] == 0 and fingers_status[4] == 0
        and vectorSize(landmark[3], landmark[6]) < 20 and vectorAngle(landmark[4], landmark[6], landmark[8]) < 90):
            command = Command.TOGGLE_FAVORITE
            print("比心")
        else:
            # 设置留空手势，可以更好地分隔不同操作
            command = Command.NONE
            print("空")

        return command


    def get_landmark(self, frame):
        imgRGB = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
        result = self.hands.process(imgRGB)
        hand_point = result.multi_hand_landmarks  # 返回21个手部关键点的坐标，其值为比例
        result = self.hands.process(imgRGB)
        hand_point = result.multi_hand_landmarks  # 返回21个手部关键点的坐标，其值为比例

        landmark = []
        # 当关键点存在时
        if hand_point:
            for handlms in hand_point:
                # 绘制关键点及其连接线，参数：
                # 绘制的图片，关键点坐标，连接线，点样式，线样式
                self.mp_drawing.draw_landmarks(frame, handlms, self.mp_hands.HAND_CONNECTIONS, self.handMsStyle, self.handConStyle)
                for i, lm in enumerate(handlms.landmark):
                    posX = int(lm.x * frame.shape[1])  # lm.x表示在图片大小下的比例，乘以图片大小将其转换为队形坐标
                    posY = int(lm.y * frame.shape[0])
                    landmark.append((posX, posY))  # 21个手部关键点坐标
                    # 显示关键点
                    cv.putText(frame, str(i), (posX, posY), cv.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), thickness=2)

            return landmark
        else:
            raise RuntimeError()
