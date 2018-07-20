from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QLCDNumber, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPalette, QFont, QIcon
import sys, playsound


class Tomato(QWidget):
    def __init__(self):
        super().__init__()
        self.work = 25  # 番茄钟时间25分钟
        self.current_work_remain = self.work * 60
        self.second_remain = self.work * 60
        self.round = 0
        self.rest = 5  # 休息时间5分钟
        self.round_rest = 30  # 1轮4个番茄钟休息30分钟
        self.current_status = "Work"
        self.initUI()

    def initUI(self):
        self.setWindowTitle("番茄工作法计时器")
        self.setGeometry(0, 0, 400, 250)

        self.icon = QIcon('tomato.svg')
        self.setWindowIcon(self.icon)

        self.tray = QSystemTrayIcon()
        self.tray.setIcon(self.icon)
        self.tray_menu = QMenu(QApplication.desktop())
        self.restoreAction = QAction('还原', self, triggered=self.show)
        self.quitAction = QAction('退出', self, triggered=app.quit)

        self.tipAction = QAction("%s/%d > %2d:%02d" % (self.current_status, self.round, self.second_remain // 60, self.second_remain % 60), self, triggered=self.show)
        self.tray_menu.addAction(self.tipAction)
        self.tray_menu.addAction(self.restoreAction)
        self.tray_menu.addAction(self.quitAction)
        self.tray.setContextMenu(self.tray_menu)

        self.timer = QTimer()  # 初始化计时器
        self.timer.setInterval(1000)  # 每秒跳1次
        self.timer.timeout.connect(self.onTimer)  # 绑定定时触发事件

        vbox = QVBoxLayout()

        self.labelRound = QLabel(self)  # 提示标签
        self.labelRound.setText("准备开始番茄钟")
        self.labelRound.setFixedHeight(50)
        self.labelRound.setAlignment(Qt.AlignCenter)
        pe = QPalette()
        pe.setColor(QPalette.Window, Qt.darkBlue)  # 蓝底白字
        pe.setColor(QPalette.WindowText, Qt.white)
        self.labelRound.setAutoFillBackground(True)
        self.labelRound.setPalette(pe)
        self.labelRound.setFont(QFont("Courier", 20, QFont.Courier))

        vbox.addWidget(self.labelRound)

        self.clock = QLCDNumber(self)  # 剩余时间显示组件
        self.clock.display("%2d:%02d" % (self.work, 0))
        vbox.addWidget(self.clock)

        hbox = QHBoxLayout()
        vbox.addLayout(hbox)

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
        event.ignore()
        self.hide()

    def start(self):
        self.timer.start()
        self.startButton.setEnabled(False)
        self.pauseButton.setEnabled(True)
        self.stopButton.setEnabled(True)

    def onTimer(self):
        if self.current_status == 'Work':
            self.current_work_remain -= 1
            self.second_remain = self.current_work_remain
            if self.current_work_remain == 0:
                self.alarm(self.current_status)
                self.current_status = 'Rest'
                self.round += 1
                if self.round % 4 == 0:
                    self.current_rest_remain = self.round_rest * 60
                else:
                    self.current_rest_remain = self.rest * 60
                    self.second_remain = self.current_rest_remain
        else:
            self.current_rest_remain -= 1
            self.second_remain = self.current_rest_remain
            if self.current_rest_remain == 0:
                self.alarm(self.current_status)
                self.current_status = 'Work'
                self.current_work_remain = self.work * 60
                self.second_remain = self.current_work_remain
        self.labelRound.setText("Round {0}-{1}".format(self.round + 1, self.current_status))
        self.clock.display("%2d:%02d" % (self.second_remain // 60, self.second_remain % 60))
        self.tipAction.setText("%s/%d > %2d:%02d" % (self.current_status, self.round, self.second_remain // 60, self.second_remain % 60))

    def stop(self):
        self.round = 0
        self.current_work_remain = self.work * 60
        self.current_status = 'Work'
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

    def alarm(self, status, times=10):
        if status == 'Work':
            for i in range(times):
                playsound.playsound('bark.ogg')
        else:
            for i in range(times):
                playsound.playsound('drip.ogg')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    tomato = Tomato()
    sys.exit(app.exec_())
