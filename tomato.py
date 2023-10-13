#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Date: 2018-07-20
Author: Lin Gang
Email: gang868@gmail.com
Description: Tomato alarm clock
Version: 1.1
'''
from enum import Enum

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLCDNumber, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPalette, QFont, QIcon, QPixmap
import sys, playsound, os
# from qfluentwidgets import (CommandBar, Action)
# from qfluentwidgets import FluentIcon as FIF
import image_rc


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OPACITY = 0.5
WIDTH = 300
HEIGHT = 300

class WorkStatus(Enum):
    WORK = ("work", "工作")
    REST = ("rest", "休息")

class Tomato(QWidget):
    def __init__(self, app:QApplication):
        super().__init__()
        self.app = app
        self.work = 25  # 番茄钟时间25分钟
        self.second_remain = self.work * 60
        self.round = 0
        self.rest = 5  # 休息时间5分钟
        self.round_rest = 30  # 1轮4个番茄钟休息30分钟
        self.current_status = "Work"
        # 是否"置顶"
        self.is_top_hint = False
        self.initUI()

    def initUI(self):
        self.setWindowTitle("番茄工作法计时器")
        deskRect = self.app.desktop().availableGeometry()
        # 右下角显示, 可能往右超出一部分, 原因未知
        w = WIDTH
        h = HEIGHT
        x = deskRect.width() - w - 1
        y = deskRect.height() - h - 1
        # self.setGeometry(0, 0, 400, 250)
        self.setGeometry(x, y, w, h)
        # self.setWindowOpacity(OPACITY)
        # 窗体置顶
        # self.setWindowFlags(Qt.WindowStaysOnTopHint)

        # 设置番茄图标（程序和托盘）
        # self.icon = QIcon(os.path.join(BASE_DIR, 'tomato.svg'))
        iconPixmap = QPixmap(":/tomato.svg")
        self.icon = QIcon(iconPixmap)
        self.setWindowIcon(self.icon)
        # 设置托盘功能（显示计时、还原窗体和退出程序）
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon)
        self.tray_menu = QMenu(QApplication.desktop())
        self.restoreAction = QAction('显示', self, triggered=self.show)
        self.quitAction = QAction('退出', self, triggered=app.quit)

        self.tipAction = QAction("%s/%d > %2d:%02d" % (self.current_status, self.round + 1, self.second_remain // 60, self.second_remain % 60), self, triggered=self.show)
        self.tray_menu.addAction(self.tipAction)
        self.tray_menu.addAction(self.restoreAction)
        self.tray_menu.addAction(self.quitAction)
        self.tray.setContextMenu(self.tray_menu)
        # 设置定时器
        self.timer = QTimer()  # 初始化计时器
        self.timer.setInterval(1000)  # 每秒跳1次
        self.timer.timeout.connect(self.onTimer)  # 绑定定时触发事件

        vbox = QVBoxLayout()

        # bar = self.createCommandBar()
        # vbox.addWidget(bar, 0, Qt.AlignTop)

        # 提示标签
        self.labelRound = QLabel(self)  # 提示标签
        self.labelRound.setText("准备开始番茄钟")
        # self.labelRound.setFixedHeight(50)
        self.labelRound.setMaximumHeight(40)
        self.labelRound.setAlignment(Qt.AlignCenter)
        self.pe = QPalette()
        self.pe.setColor(QPalette.Window, Qt.darkRed)  # 蓝底白字
        self.pe.setColor(QPalette.WindowText, Qt.white)
        self.labelRound.setAutoFillBackground(True)
        self.labelRound.setPalette(self.pe)
        label_round_font = QFont("Courier", 10, QFont.Courier)
        label_round_font.setPointSize(10)
        self.labelRound.setFont(label_round_font)

        vbox.addWidget(self.labelRound)
        # 倒计时显示器
        self.clock = QLCDNumber(self)  # 剩余时间显示组件
        # 没有效果?
        # clockFont = QFont('Microsoft YaHei', 10, 75)
        # clockFont.setBold(800)
        # self.clock.setFont(clockFont)
        # self.clock.setStyleSheet("color:darkRed")
        self.clock.display("%2d:%02d" % (self.work, 0))
        vbox.addWidget(self.clock)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        # 功能按钮
        # self.startButton = QPushButton("开始")
        # self.startButton.clicked.connect(self.start)
        # hbox.addWidget(self.startButton)
        self.startPauseButton = QPushButton()
        self.startPauseButton.setText("开始")
        self.startPauseButton.clicked.connect(self.toggleStartPause)
        hbox.addWidget(self.startPauseButton)

        self.stopButton = QPushButton("停止")
        self.stopButton.setEnabled(False)
        self.stopButton.clicked.connect(self.stop)
        hbox.addWidget(self.stopButton)

        # self.pauseButton = QPushButton("暂停")
        # self.pauseButton.setEnabled(False)
        # self.pauseButton.clicked.connect(self.pause)
        # hbox.addWidget(self.pauseButton)

        self.topHintButton = QPushButton("置顶")
        self.topHintButton.clicked.connect(self.toggleTopHint)
        hbox.addWidget(self.topHintButton)

        self.setLayout(vbox)

        self.tray.show()
        self.show()

    # def createCommandBar(self):
    #     self.commandBar = bar = CommandBar(self)
    #     bar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
    #     addAction = Action(FIF.ADD, self.tr('Add'))
    #     addAction.triggered.connect(lambda: print("Adddddddddddddddd"))
    #     self.closeAction = closeAction = Action(FIF.CLOSE, self.tr('Close'))
    #     closeAction.triggered.connect(self.close)
    #     self.minAction = minAction = Action(FIF.MINIMIZE, self.tr('Minimize'))
    #     # minAction.setIcon()
    #     minAction.triggered.connect(self.showMinimized)
    #     self.maxAction = maxAction = Action(FIF.FULL_SCREEN, self.tr('FullScreen'))
    #     maxAction.triggered.connect(self.switchMaxNormal)
    #     maxAction.setObjectName("maxAction")
    #     self.normalAction = normalAction = Action(FIF.BACK_TO_WINDOW, self.tr('BackToWindow'))
    #     normalAction.triggered.connect(self.switchMaxNormal)
    #     normalAction.setObjectName("normalAction")
    #     bar.setWindowTitle("xxxxxxxxxxxx")
    #     bar.addActions([
    #         minAction,
    #         # normalAction,
    #         maxAction,
    #         closeAction,
    #         # Action(FIF.ROTATE, self.tr('Rotate')),
    #         # Action(FIF.ZOOM_IN, self.tr('Zoom in')),
    #         # Action(FIF.ZOOM_OUT, self.tr('Zoom out')),
    #     ])
    #     # bar.addSeparator()
    #
    #     # add custom widget
    #     # button = TransparentDropDownPushButton(self.tr('Sort'), self, FIF.SCROLL)
    #     # button.setMenu(self.createCheckableMenu())
    #     # button.setFixedHeight(34)
    #     # setFont(button, 12)
    #     # bar.addWidget(button)
    #
    #     # bar.addHiddenActions([
    #     #     Action(FIF.SETTING, self.tr('Settings'), shortcut='Ctrl+I'),
    #     # ])
    #     return bar

    # 判断最大化，还是窗口化
    def switchMaxNormal(self):
        try:
            # maxAction = [item for item in self.commandBar.actions() if item.objectName() == 'maxAction'][0]
            # normalAction = [item for item in self.commandBar.actions() if item.objectName() == 'normalAction'][0]
            if self.isMaximized():
                self.showNormal()                  #窗口化显示
                # maxAction.setVisible(False)
                # normalAction.setVisible(True)
                print("取消最大化")
                self.commandBar.insertAction(self.closeAction, self.maxAction)
                self.commandBar.removeAction(self.normalAction)
            else:
                self.showMaximized()               #最大化显示
                # maxAction.setVisible(True)
                # normalAction.setVisible(False)
                print("最大化")
                self.commandBar.insertAction(self.closeAction, self.normalAction)
                self.commandBar.removeAction(self.maxAction)
        except Exception as e:
            print("switchMaxNormal Exception", e)

    def closeEvent(self, event):
        # 禁止关闭按钮退出程序
        event.ignore()
        # 点击关闭按钮即隐藏主窗体
        self.hide()

    def playSound(self, fileName):
        try:
            playsound.playsound(os.path.join(BASE_DIR, fileName))
        except Exception as ex:
            print("playsound exception: %s" % ex)

    def onTimer(self):
        # 工作状态
        self.second_remain -= 1
        if self.second_remain == 0:
            self.timer.stop()
            self.clock.display("%2d:%02d" % (self.second_remain // 60, self.second_remain % 60))
            self.round += 1
            if self.current_status == "Work":
                for i in range(2):
                    # playsound.playsound(os.path.join(BASE_DIR, 'bark.ogg'))
                    self.playSound('resource/rest-hint.mp3')
                self.pe.setColor(QPalette.Window, Qt.darkGreen)
                self.clock.setStyleSheet("color:darkGreen")
                self.current_status = "Rest"
                if self.round % 4 == 0:
                    self.second_remain = self.round_rest * 60
                else:
                    self.second_remain = self.rest * 60
            else:
                for i in range(10):
                    #playsound.playsound(os.path.join(BASE_DIR, 'drip.ogg'))
                    self.playSound('resource/drip.mp3')
                self.pe.setColor(QPalette.Window, Qt.darkRed)
                self.clock.setStyleSheet("color:none")
                self.current_status = "Work"
                self.second_remain = self.work * 60
            self.timer.start()

        self.labelRound.setPalette(self.pe)
        self.labelRound.setText("Round {0}-{1}".format(self.round + 1, self.current_status))
        self.clock.display("%2d:%02d" % (self.second_remain // 60, self.second_remain % 60))
        self.tipAction.setText("%s/%d > %2d:%02d" % (self.current_status, self.round + 1, self.second_remain // 60, self.second_remain % 60))

    def start(self):
        # 启动定时器
        self.timer.start()
        # 设置功能按钮
        self.startButton.setEnabled(False)
        self.pauseButton.setEnabled(True)
        self.stopButton.setEnabled(True)

    def stop(self):
        self.round = 0
        self.second_remain = self.work * 60
        self.current_status = 'Work'
        self.clock.display("%2d:%02d" % (self.work, 0))
        # self.startButton.setEnabled(True)
        # self.pauseButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.timer.stop()
        self.startPauseButton.setText('开始')
        self.pe.setColor(QPalette.Window, Qt.darkRed)
        self.clock.setStyleSheet("color:none")
        self.labelRound.setPalette(self.pe)

    def pause(self):
        self.startButton.setEnabled(True)
        self.pauseButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.timer.stop()

    def toggleStartPause(self):
        t = self.startPauseButton.text()
        if t == '开始' or t == '继续':
            # 启动定时器
            self.timer.start()
            # 设置功能按钮
            self.stopButton.setEnabled(True)
            self.startPauseButton.setText('暂停')
        elif t == '暂停':
            self.stopButton.setEnabled(True)
            self.timer.stop()
            self.startPauseButton.setText('继续')

    def toggleTopHint(self):
        t  = self.topHintButton.text()
        self.is_top_hint = True if not self.is_top_hint else False # 取反
        if self.is_top_hint:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            self.topHintButton.setText('取消置顶')
            self.toggleHideSome()
        else:
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
            self.topHintButton.setText('置顶')
            self.toggleHideSome()
        # self.show() # fix 窗体消失问题
        self.setVisible(True)

    def toggleHideSome(self, is_hide=None):
        """比如在置顶时, 隐藏一些非重要部件"""
        is_hide = is_hide if is_hide is not None else self.is_top_hint
        if is_hide:
            self.startPauseButton.setVisible(False)
            self.stopButton.setVisible(False)
            self.topHintButton.setVisible(False)
            self.labelRound.setVisible(False)
        else:
            self.startPauseButton.setVisible(True)
            self.stopButton.setVisible(True)
            self.topHintButton.setVisible(True)
            self.labelRound.setVisible(True)

    def enterEvent(self, event: QtCore.QEvent) -> None:
        if self.is_top_hint:
            self.setWindowOpacity(1)
        self.toggleHideSome(False)

    def leaveEvent(self, event: QtCore.QEvent) -> None:
        # 若是"置顶", 鼠标离开降低透明度
        if self.is_top_hint:
            self.setWindowOpacity(OPACITY)
        self.toggleHideSome()

    # 添加 复写 窗口状态改变 函数
    # def changeEvent(self, event):
    #     print(event)

if __name__ == "__main__":
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    tomato = Tomato(app)
    sys.exit(app.exec_())
