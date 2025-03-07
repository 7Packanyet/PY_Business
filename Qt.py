import sys
from PyQt5 import QtCore, QtGui, QtWidgets

app = QtWidgets.QApplication(sys.argv) # 创建app
widgetHello = QtWidgets.QWidget() # 创建窗体，选择QtWidget类
widgetHello.resize(280, 150) #设置窗体大小
widgetHello.setWindowTitle("Demo") # 设置窗体名称

LabHello = QtWidgets.QLabel(widgetHello) # 创建标签，指定父容器
LabHello.setText('Hello,World') # 设置标签内容
font = QtGui.QFont() # 创建字体font对象
font.setBold(True) # 加粗
font.setPointSize(12) # 字号
LabHello.setFont(font) # 设置标签字体
size = LabHello.sizeHint() # 获取最佳位置
LabHello.setGeometry(70,60,size.width(),size.height()) # 设置标签位置

widgetHello.show() # 显示窗体
sys.exit(app.exec_()) # 点菜单关闭才关闭窗口，否则运行完上述代码直接关闭窗口
