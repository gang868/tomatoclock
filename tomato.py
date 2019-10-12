#!/usr/bin/python3
# -*- coding: utf-8 -*-

'''
Date: 2018-07-20
Author: Lin Gang
Email: gang868@gmail.com
Description: Tomato alarm clock
Version: 1.1
'''

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLCDNumber, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPalette, QFont, QIcon
import sys, playsound, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Tomato(QWidget):
    def __init__(self):
        super().__init__()
        self.work = 25  # 番茄钟时间25分钟
        self.second_remain = self.work * 60
        self.round = 1
        self.rest = 5  # 休息时间5分钟
        self.round_rest = 30  # 1轮4个番茄钟休息30分钟
        self.current_status = "Work"
        self.initUI()

    def initUI(self):
        self.setWindowTitle("番茄工作法计时器")
        self.setGeometry(0, 0, 400, 250)
        # 设置番茄图标（程序和托盘）
        self.icon = QIcon(os.path.join(BASE_DIR, 'tomato.svg'))
        self.setWindowIcon(self.icon)
        # 设置托盘功能（显示计时、还原窗体和退出程序）
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon)
        self.tray_menu = QMenu(QApplication.desktop())
        self.restoreAction = QAction('显示', self, triggered=self.show)
        self.quitAction = QAction('退出', self, triggered=app.quit)

        self.tipAction = QAction("%s/%d > %2d:%02d" % (self.current_status, self.round, self.second_remain // 60, self.second_remain % 60), self, triggered=self.show)
        self.tray_menu.addAction(self.tipAction)
        self.tray_menu.addAction(self.restoreAction)
        self.tray_menu.addAction(self.quitAction)
        self.tray.setContextMenu(self.tray_menu)
        # 设置定时器
        self.timer = QTimer()  # 初始化计时器
        self.timer.setInterval(1000)  # 每秒跳1次
        self.timer.timeout.connect(self.onTimer)  # 绑定定时触发事件

        vbox = QVBoxLayout()
        # 提示标签
        self.labelRound = QLabel(self)  # 提示标签
        self.labelRound.setText("准备开始番茄钟")
        self.labelRound.setFixedHeight(50)
        self.labelRound.setAlignment(Qt.AlignCenter)
        self.pe = QPalette()
        self.pe.setColor(QPalette.Window, Qt.darkRed)  # 蓝底白字
        self.pe.setColor(QPalette.WindowText, Qt.white)
        self.labelRound.setAutoFillBackground(True)
        self.labelRound.setPalette(self.pe)
        self.labelRound.setFont(QFont("Courier", 20, QFont.Courier))

        vbox.addWidget(self.labelRound)
        # 倒计时显示器
        self.clock = QLCDNumber(self)  # 剩余时间显示组件
        self.clock.display("%2d:%02d" % (self.work, 0))
        vbox.addWidget(self.clock)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)
        # 功能按钮
        self.startButton = QPushButton("开始")
        self.startButton.clicked.connect(self.start)
        hbox.addWidget(self.startButton)

        self.stopButton = QPushButton("停止")
        self.stopButton.setEnabled(False)
        self.stopButton.clicked.connect(self.stop)
        hbox.addWidget(self.stopButton)

        self.pauseButton = QPushButton("暂停")
        self.pauseButton.setEnabled(False)
        self.pauseButton.clicked.connect(self.pause)
        hbox.addWidget(self.pauseButton)

        self.setLayout(vbox)

        self.tray.show()
        self.show()

    def closeEvent(self, event):
        # 禁止关闭按钮退出程序
        event.ignore()
        # 点击关闭按钮即隐藏主窗体
        self.hide()

    def onTimer(self):
        # 工作状态
        self.second_remain -= 1
        if self.second_remain == 0:
            self.timer.stop()
            self.clock.display("%2d:%02d" % (self.second_remain // 60, self.second_remain % 60))
            if self.current_status == "Work":
                for i in range(10):
                    playsound.playsound(os.path.join(BASE_DIR, 'bark.mp3'))
                self.pe.setColor(QPalette.Window, Qt.darkGreen)
                self.current_status = "Rest"
                if self.round!=0 and self.round % 4 == 0:
                    self.second_remain = self.round_rest * 60
                else:
                    self.second_remain = self.rest * 60
            else:
                self.round += 1
                for i in range(10):
                    playsound.playsound(os.path.join(BASE_DIR, 'drip.mp3'))
                self.pe.setColor(QPalette.Window, Qt.darkRed)
                self.current_status = "Work"
                self.second_remain = self.work * 60
            self.timer.start()

        self.labelRound.setPalette(self.pe)
        self.labelRound.setText("Round {0}-{1}".format(self.round, self.current_status))
        self.clock.display("%2d:%02d" % (self.second_remain // 60, self.second_remain % 60))
        self.tipAction.setText("%s/%d > %2d:%02d" % (self.current_status, self.round, self.second_remain // 60, self.second_remain % 60))

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
        self.pe.setColor(QPalette.Window, Qt.darkRed)
        self.labelRound.setText("准备开始番茄钟")
        self.labelRound.setPalette(self.pe)
        self.clock.display("%2d:%02d" % (self.work, 0))
        self.startButton.setEnabled(True)
        self.pauseButton.setEnabled(False)
        self.stopButton.setEnabled(False)
        self.timer.stop()

    def pause(self):
        self.startButton.setEnabled(True)
        self.pauseButton.setEnabled(False)
        self.stopButton.setEnabled(True)
        self.timer.stop()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tomato = Tomato()
    sys.exit(app.exec_())
