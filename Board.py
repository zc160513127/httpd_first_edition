"""
    Description: 风向风速复显仪
    Author     : 李昀哲
    Date       : 2021-09-06
"""
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from math import *
import sys


class Board(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Wind Speed and Direction Board")
        self.setMinimumWidth(600)
        self.setMinimumHeight(600)
        self.setFixedSize(self.width(), self.height())    # 禁止拉伸窗口大小
        # 风速LED
        self.lcdDisplay1 = QLCDNumber(self)
        self.lcdDisplay1.setDigitCount(4)
        self.lcdDisplay1.setMode(QLCDNumber.Dec)
        self.lcdDisplay1.setSegmentStyle(QLCDNumber.Flat)
        self.lcdDisplay1.setStyleSheet('border:2px solid green;color:green;background:silver')
        # 最大风速LED
        self.lcdDisplay2 = QLCDNumber(self)
        self.lcdDisplay2.setDigitCount(4)
        self.lcdDisplay2.setMode(QLCDNumber.Dec)
        self.lcdDisplay2.setSegmentStyle(QLCDNumber.Flat)
        self.lcdDisplay2.setStyleSheet('border:2px solid green;color:green;background:silver')
        # 参数设置
        self.startAngle = -90    # 以QPainter坐标方向为准
        self.endAngle = -90      # 以QPainter坐标方向为准
        self.scaleMainNum = 12   # 主刻度数
        self.scaleSubNum = 36    # 主刻度被分割份数
        self.decimals = 1        # 小数位数
        # 标签
        self.title1 = '风向风速复显仪'
        self.title2 = 'm/s'
        self.title3 = 'm/s'
        self.title4 = 'Wind'
        self.title5 = 'Speed'
        self.title6 = 'Max'
        # 传入数据
        self.WindSpeed = 14                   # 风速 m/s
        self.ShipHeading = 50                 # 风向（0~360）
        self.WindDirectionData = [1, 2, 3, 4, 5, 6, 20, 40, 50, 60, 40, 80]   # 风向全部历史数据
        self.WindDirectionSelect = 1          # 历史数据分钟选择 0-1分钟  1-2分钟  2-5分钟
        # 提取对应时间的历史数据
        self.WDmode = [60, 120, 300]  # 不同模式提取的数据数量
        self.HistoryData = []  # 风向选择后历史数据
        if len(self.WindDirectionData) >= self.WDmode[self.WindDirectionSelect]:
            for i in range(0, self.WDmode[self.WindDirectionSelect]):
                self.HistoryData.append(self.WindDirectionData[-1-i])
            self.HistoryData = list(reversed(self.HistoryData))
        else:
            self.HistoryData = self.WindDirectionData
        # 最大风速计算
        self.WindMax = 0       # 最大风速
        if self.WindSpeed > self.WindMax:
           self.WindMax = self.WindSpeed

    def paintEvent(self, event):
        side = min(self.width(), self.height())
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)  # painter坐标系原点移至widget中央
        painter.scale(side / 300, side / 300)  # 缩放painterwidget坐标系，使绘制的时钟位于widge中央
        self.drawGrayRing(painter)      # 画外框
        self.drawIndicator(painter)     # 画指针
        self.drawBlackDial(painter)     # 画表盘以及标签
        self.drawScaleNum(painter)      # 画刻度数字
        self.drawScaleLine(painter)     # 画外圈刻度线
        self.drawScaleLineIn(painter)   # 画内圈刻度线
        self.drawValue(painter)         # 画数显

    def drawGrayRing(self, p):
        # 灰色外侧环
        p.save()
        radius = 130
        lg = QLinearGradient(-radius, -radius, radius, radius)   # 渐变颜色设置
        lg.setColorAt(0, Qt.white)
        lg.setColorAt(1, Qt.black)
        p.setBrush(lg)
        p.setPen(Qt.NoPen)
        p.drawEllipse(-radius, -radius, radius * 2, radius * 2)
        p.restore()

    def drawBlackDial(self, p):
        # 黑色表盘
        p.save()
        p.setBrush(Qt.black)
        p.drawEllipse(-120, -120, 120 * 2, 120 * 2)
        # 各标签
        p.setPen(Qt.white)
        fm = QFontMetrics(p.font())
        w1 = fm.size(Qt.TextSingleLine, self.title1).width()
        p.drawText(int(-w1 / 2), -50, self.title1)
        w2 = fm.size(Qt.TextSingleLine, self.title2).width()
        p.drawText(int(-w2 / 2 + 45), -12, self.title2)
        w3 = fm.size(Qt.TextSingleLine, self.title3).width()
        p.drawText(int(-w3 / 2 + 45), 28, self.title3)
        w4 = fm.size(Qt.TextSingleLine, self.title4).width()
        p.drawText(int(-w4 / 2 - 50), -18, self.title4)
        w5 = fm.size(Qt.TextSingleLine, self.title5).width()
        p.drawText(int(-w5 / 2 - 50), -8, self.title5)
        w6 = fm.size(Qt.TextSingleLine, self.title6).width()
        p.drawText(int(-w6 / 2 - 50), 28, self.title6)
        p.restore()

    def drawScaleNum(self, p):
        # 刻度数字
        p.save()
        p.setPen(Qt.white)
        startRad = self.startAngle * (3.14 / 180)
        stepRad = (360 - (self.startAngle - self.endAngle)) * (3.14 / 180) / self.scaleMainNum
        fm = QFontMetricsF(p.font())
        kedu = [0, 30, 60, 90, 120, 150, 180, 150, 120, 90, 60, 30]
        for i in range(0, self.scaleMainNum):
            sina = sin(startRad + i * stepRad)
            cosa = cos(startRad + i * stepRad)
            tmpVal = kedu[i]
            s = '{:.0f}'.format(tmpVal)
            w = fm.size(Qt.TextSingleLine, s).width()
            h = fm.size(Qt.TextSingleLine, s).height()
            x = 98 * cosa - w / 2
            y = 98 * sina - h / 2
            p.drawText(QRectF(x, y, w, h), s)
        p.restore()

    def drawScaleLine(self, p):
        # 外圈刻度线
        p.save()
        p.rotate(self.startAngle)
        scaleNums = self.scaleMainNum * self.scaleSubNum
        angleStep = (360 - (self.startAngle - self.endAngle)) / scaleNums
        p.setPen(Qt.white)
        pen = QPen(Qt.white)
        for i in range(0, scaleNums + 1):
            if i % self.scaleMainNum == 0:
                pen.setWidth(1)
                p.setPen(pen)
                p.drawLine(120, 0, 108, 0)
            else:
                pen.setWidth(1)
                p.setPen(QColor(0, 102, 204))
                p.drawLine(120, 0, 110, 0)
            p.rotate(angleStep)
        p.restore()

    def drawScaleLineIn(self, p):
        # 内圈刻度线（一段时间的风向范围）
        p.save()
        p.rotate(self.startAngle)
        # 对历史数据进行处理
        HData = []
        for i in range(0,len(self.HistoryData)):
            if self.HistoryData[i] <= 180:
                HData.append(self.HistoryData[i] * 1.2)
            if self.HistoryData[i] > 180:
                HData.append((self.HistoryData[i]-360) * 1.2)
        HD_max = int(max(HData))
        HD_min = int(min(HData))
        History_max = int(max(self.HistoryData))
        History_min = int(min(self.HistoryData))
        scaleNums = self.scaleMainNum * self.scaleSubNum    # 12*36 = 432   432/360 = 1.2
        angleStep = (360 - (self.startAngle - self.endAngle)) / scaleNums
        p.setPen(Qt.white)
        pen = QPen(Qt.white)
        # 历史数据分布情况
        if HD_min >= 0 and HD_max >= 0:
            # 单独右边
            for i in range(0, HD_max):
                if i < HD_min:
                    pen.setWidth(1)
                    p.setPen(QColor(0, 0, 0))
                    p.drawLine(90, 0, 85, 0)
                    p.rotate(angleStep)
                if i >= HD_min:
                    pen.setWidth(1)
                    p.setPen(QColor(255, 153, 0))
                    p.drawLine(90, 0, 85, 0)
                    p.rotate(angleStep)
        if HD_min < 0 and HD_max < 0:
            # 单独左边
            for i in range(0, 432 + HD_max):
                if i < 432 + HD_min:
                    pen.setWidth(1)
                    p.setPen(QColor(0, 0, 0))
                    p.drawLine(90, 0, 85, 0)
                    p.rotate(angleStep)
                if i >= 432 + HD_min:
                    pen.setWidth(1)
                    p.setPen(QColor(255, 153, 0))
                    p.drawLine(90, 0, 85, 0)
                    p.rotate(angleStep)
        if HD_min < 0 and HD_max >= 0:
            # 左右都有
            Hmax = int(History_max * 1.2)
            Hmin = int(History_min * 1.2)
            # 判断是否为递增数据
            FlagNum1 = 0
            for j in range(0, len(self.HistoryData) - 1):
                if self.HistoryData[j] <= self.HistoryData[j + 1]:
                    FlagNum1 += 1
                else:
                    FlagNum1 = FlagNum1
            # 判断是否为递减数据
            FlagNum2 = 0
            for j in range(0, len(self.HistoryData) - 1):
                if self.HistoryData[j] >= self.HistoryData[j+1]:
                    FlagNum2 += 1
                else:
                    FlagNum2 = FlagNum2
            if FlagNum1 == len(self.HistoryData)-1 or FlagNum2 == len(self.HistoryData)-1:
                for i in range(0, Hmax):
                    if i < Hmin:
                        pen.setWidth(1)
                        p.setPen(QColor(0, 0, 0))
                        p.drawLine(90, 0, 85, 0)
                        p.rotate(angleStep)
                    if i >= Hmin:
                        pen.setWidth(1)
                        p.setPen(QColor(255, 153, 0))
                        p.drawLine(90, 0, 85, 0)
                        p.rotate(angleStep)
            else:
                # 左侧
                for i in range(0, 433):
                    if i < 433 + HD_min:
                        pen.setWidth(1)
                        p.setPen(QColor(0, 0, 0))
                        p.drawLine(90, 0, 85, 0)
                        p.rotate(angleStep)
                    if i >= 433 + HD_min:
                        pen.setWidth(1)
                        p.setPen(QColor(255, 153, 0))
                        p.drawLine(90, 0, 85, 0)
                        p.rotate(angleStep)
                # 右侧
                for i in range(0, HD_max):
                    pen.setWidth(1)
                    p.setPen(QColor(255, 153, 0))
                    p.drawLine(90, 0, 85, 0)
                    p.rotate(angleStep)
        if HD_min == HD_max:
            # 最大最小值一致
            pen.setWidth(1)
            p.setPen(QColor(255, 153, 0))
            p.drawLine(90, 0, 85, 0)
            p.rotate(angleStep)
        p.restore()

    def drawValue(self, p):
        # 风速和最大风速显示
        side = min(self.width(), self.height())
        w, h = side / 2 * 0.4, side / 2 * 0.2
        x1, y1 = self.width() / 2 - w / 2, self.height() / 2 + side / 2 * 0.55 - 230
        self.lcdDisplay1.setGeometry(int(x1), int(y1), int(w), int(h))
        x2, y2 = self.width() / 2 - w / 2, self.height() / 2 + side / 2 * 0.55 - 150
        self.lcdDisplay2.setGeometry(int(x2), int(y2), int(w), int(h))
        ss = '{:.' + str(self.decimals) + 'f}'
        self.lcdDisplay1.display(ss.format(self.WindSpeed))
        self.lcdDisplay2.display(ss.format(self.WindMax))

    def drawIndicator(self, p):
        # 外圈三角指示
        p.save()
        polygon = QPolygon([QPoint(0, 0), QPoint(120, 0), QPoint(130, -5), QPoint(130, 5), QPoint(120, 0)])
        if self.ShipHeading >= 0 and self.ShipHeading <= 90:
            degRotate = 270 + self.ShipHeading
        else:
            degRotate = self.ShipHeading - 90
        p.rotate(degRotate)
        halogd = QRadialGradient(0, 0, 120, 0, 0)
        halogd.setColorAt(0, QColor(255, 0, 51))
        halogd.setColorAt(1, QColor(255, 153, 0))
        p.setPen(Qt.white)
        p.setBrush(halogd)
        p.drawConvexPolygon(polygon)
        p.restore()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gp = Board()
    gp.show()
    app.exec_()
