#!/usr/bin/env python
# coding=utf-8
# @Time    : 2020/10/19 19:20
# @Author  : 江斌
# @Software: PyCharm

from PyQt5.Qt import *
import sys


def get_ico(style):
    """

    :param style: QStyle.SP_arrow
    :return:
    """
    return QApplication.style().standardIcon(style)


def test_tool_button():
    app = QApplication(sys.argv)
    menu = QMenu()  # 创建菜单
    sub_menu = QMenu(menu)  # 创建子菜单
    sub_menu.setTitle("子菜单")
    sub_menu.setIcon(get_ico(QStyle.SP_TitleBarMaxButton))
    menu.addMenu(sub_menu)
    action = QAction(get_ico(QStyle.SP_ArrowForward), "行为", menu)
    menu.addAction(action)
    action.triggered.connect(lambda: print("点击了 action"))

    w = QWidget()
    layout = QVBoxLayout()
    w.setLayout(layout)
    w.setWindowTitle("QToolButton")
    w.resize(300, 300)

    tb = QToolButton()
    tb.setFixedWidth(100)
    tb.setFixedHeight(100)
    tb.setIcon(get_ico(QStyle.SP_MessageBoxWarning))
    tb.setIconSize(QSize(100,100))
    tb.setAutoRaise(True)
    tb.setMenu(menu)  # 添加菜单 到 QToolBool
    tb.setPopupMode(QToolButton.MenuButtonPopup)  # 设置菜单模式

    label = QLabel("Introduction")
    label.setFixedHeight(20)
    label.setPixmap(get_ico(QStyle.SP_MessageBoxWarning).pixmap(QSize(100,100)))
    label2 = QLabel("Introduction2")

    layout.addWidget(label)
    layout.addWidget(tb)
    layout.addWidget(label2)

    w.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    test_tool_button()
