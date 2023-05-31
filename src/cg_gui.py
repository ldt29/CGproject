#!/usr/bin/env python
# -*- coding:utf-8 -*-

import sys
from typing import Optional

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QRectF, Qt
from PyQt5.QtGui import QPainter, QMouseEvent, QColor, QPixmap, QIcon, QPen
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    qApp,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsItem,
    QListWidget,
    QHBoxLayout,
    QWidget,
    QToolBar,
    QSpinBox,
    QLabel,
    QStyleOptionGraphicsItem, QColorDialog, QDialog, QMessageBox, QDialogButtonBox, QSlider, QFormLayout,
    QDoubleSpinBox, QFileDialog, QInputDialog)

import cg_algorithms as alg


class MyCanvas(QGraphicsView):
    """
    画布窗体类，继承自QGraphicsView，采用QGraphicsView、QGraphicsScene、QGraphicsItem的绘图框架
    """

    def __init__(self, *args):
        super().__init__(*args)
        self.main_window = None
        self.list_widget = None
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.begin = []  # 图形变换时选中的第一个控制点
        self.rawList = []  # 图形变换时原图元控制参数

        self.rotate_angle = 0  # 旋转角度
        self.scale_factor = 1  # 缩放比例

    def start_draw_line(self, algorithm, item_id):
        self.status = 'line'
        self.temp_algorithm = algorithm
        self.temp_id = 'line' + item_id

    # TODO: 以下内容为11月新修改
    def start_fill_polygon(self, item_id):
        self.status = 'fill_polygon'
        self.temp_algorithm = 'DDA'
        self.temp_id = 'fill_polygon' + item_id
        self.temp_item = None

    def start_draw_polygon(self, algorithm, item_id):
        self.status = 'polygon'
        self.temp_algorithm = algorithm
        self.temp_id = 'polygon' + item_id
        self.temp_item = None  # 防止p_list沿用上个多边形或者曲线的p_list

    def start_draw_ellipse(self, item_id):
        self.status = 'ellipse'
        self.temp_id = 'ellipse' + item_id

    def start_draw_curve(self, algorithm, item_id):
        self.status = 'curve'
        self.temp_algorithm = algorithm
        self.temp_id = 'curve' + item_id
        self.temp_item = None

    def start_translate(self):
        if self.selected_id == '':
            QMessageBox.warning(self, '注意', '请先在右侧选定图元', QMessageBox.Yes, QMessageBox.Yes)
            return
        self.status = 'translate'
        self.temp_item = self.item_dict[self.selected_id]  # 所要操作的是被选中图元
        self.rawList = self.temp_item.p_list

    def start_rotate(self):
        if self.selected_id == '':
            QMessageBox.warning(self, '注意', '请先在右侧选定图元', QMessageBox.Yes, QMessageBox.Yes)
            return
        if self.item_dict[self.selected_id].item_type == 'ellipse':  # 还没有选图元或者选椭圆不做任何动作
            QMessageBox.warning(self, '注意', '椭圆不提供旋转功能', QMessageBox.Yes, QMessageBox.Yes)
            return
        self.rotate_angle = 0  # 从0开始防止上次旋转角度的叠加
        self.status = 'rotate'
        self.temp_item = self.item_dict[self.selected_id]  # 所要操作的是被选中图元
        self.rawList = self.temp_item.p_list

    def start_scale(self):
        if self.selected_id == '':
            QMessageBox.warning(self, '注意', '请先在右侧选定图元', QMessageBox.Yes, QMessageBox.Yes)
            return
        self.scale_factor = 1  # 防止上次操作的叠加
        self.status = 'scale'
        self.temp_item = self.item_dict[self.selected_id]  # 所要操作的是被选中图元
        self.rawList = self.temp_item.p_list

    def start_remove(self):
        if self.selected_id == '':
            QMessageBox.warning(self, '注意', '请先在右侧选定图元', QMessageBox.Yes, QMessageBox.Yes)
            return
        self.delete_item()

    def start_clip(self, algorithm):
        if self.selected_id == '':
            QMessageBox.warning(self, '注意', '请先在右侧选定图元', QMessageBox.Yes, QMessageBox.Yes)
            return
        if self.item_dict[self.selected_id].item_type != 'line':
            QMessageBox.warning(self, '注意', '线段裁剪功能只针对线段才有效', QMessageBox.Yes, QMessageBox.Yes)
            return
        self.status = 'clip'
        self.temp_algorithm = algorithm

    def start_clip_polygon(self):
        if self.selected_id == '':
            QMessageBox.warning(self, '注意', '请先在右侧选定图元', QMessageBox.Yes, QMessageBox.Yes)
            return
        if self.item_dict[self.selected_id].item_type != 'polygon' \
                and self.item_dict[self.selected_id].item_type != 'fill_polygon':
            QMessageBox.warning(self, '注意', '多边形裁剪功能只针对多边形才有效', QMessageBox.Yes, QMessageBox.Yes)
            return
        self.status = 'clip_polygon'

    def finish_draw(self):
        self.temp_item = None
        self.temp_id = str(self.status) + self.main_window.get_id()

    def clear_selection(self):
        if self.selected_id != '':
            self.item_dict[self.selected_id].selected = False
            self.selected_id = ''
        self.main_window.beginx_box.setEnabled(False)
        self.main_window.beginy_box.setEnabled(False)
        self.main_window.factor_box.setEnabled(False)
        self.main_window.angle_box.setEnabled(False)

    def selection_changed(self, selected):
        if selected != '' and selected != self.selected_id and self.item_dict.__contains__(selected):
            self.main_window.statusBar().showMessage('图元选择： %s' % selected)
            if self.selected_id != '':
                self.item_dict[self.selected_id].selected = False
                self.item_dict[self.selected_id].update()
            self.selected_id = selected
            if len(self.item_dict) == 0:
                return
            if self.item_dict[selected] is None:
                self.delete_item()
            self.item_dict[selected].selected = True
            self.item_dict[selected].update()
            self.status = ''
            self.updateScene([self.sceneRect()])
            self.main_window.angle_box.setValue(0)  # 选择图元改变后从零开始
            self.main_window.factor_box.setValue(1)
            self.main_window.beginx_box.setEnabled(False)
            self.main_window.beginy_box.setEnabled(False)
            self.main_window.factor_box.setEnabled(False)
            self.main_window.angle_box.setEnabled(False)

    def save_canvas(self, filename, weight, height):
        painter = QPainter()
        pixmap = QPixmap(weight, height)
        pixmap.fill(QColor(255, 255, 255))  # 涂满白色
        painter.begin(pixmap)
        for item in self.item_dict:
            self.item_dict[item].paint(painter, QStyleOptionGraphicsItem)
        painter.end()
        pixmap.save(filename, "bmp", 100)

    def set_attr_window(self, x, y):
        self.main_window.beginx, self.main_window.beginy = x, y
        self.begin = [x, y]
        self.main_window.beginx_box.setValue(x)
        self.main_window.beginy_box.setValue(y)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        # print(f"the graph is {self.status}, the id is {self.temp_id}")
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.status == 'line':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm,
                                    self.main_window.pen_color, self.main_window.pen_width)
            self.scene().addItem(self.temp_item)

        elif self.status == 'polygon' or self.status == 'fill_polygon': # 增加填充多边形
            if self.temp_item is None:
                # print('a new polygon')
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm,
                                        self.main_window.pen_color, self.main_window.pen_width)
                self.scene().addItem(self.temp_item)
                self.setMouseTracking(True)  # 实时追踪鼠标位置
            else:
                # print(f"the p_list is {self.temp_item.p_list}")
                if event.button() == QtCore.Qt.RightButton:  # 按下鼠标右键停止绘制多边形
                    self.add_item()
                    self.setMouseTracking(False)
                else:
                    self.temp_item.p_list.append([x, y])  # 按左键表示继续增加本多边形的参数点

        elif self.status == 'ellipse':
            self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], None,
                                    self.main_window.pen_color, self.main_window.pen_width)
            self.scene().addItem(self.temp_item)

        elif self.status == 'curve':
            if self.temp_item is None:
                # print('a new curve')
                self.temp_item = MyItem(self.temp_id, self.status, [[x, y], [x, y]], self.temp_algorithm,
                                        self.main_window.pen_color, self.main_window.pen_width)
                self.scene().addItem(self.temp_item)
                self.setMouseTracking(True)  # 实时追踪鼠标位置
            else:
                # print(f"the p_list is {self.temp_item.p_list}")
                if event.button() == QtCore.Qt.RightButton:  # 按下鼠标右键停止绘制多边形
                    self.add_item()
                    self.setMouseTracking(False)
                else:
                    self.temp_item.p_list.append([x, y])  # 按左键表示继续增加本曲线的控制点

        elif self.status == 'translate':
            self.begin = [x, y]

        elif self.status == 'rotate':
            self.set_attr_window(x, y)
            self.rotate_angle = 0  # 每次选择新的旋转中心角度清零

        elif self.status == 'scale':
            self.set_attr_window(x, y)
            self.scale_factor = 1  # 每次选择新的缩放中心

        elif self.status == 'clip' or self.status == 'clip_polygon':
            self.temp_item = MyItem(None, 'polygon', [(x, y), (x, y), (x, y), (x, y)], 'DDA',
                                    QColor(0, 255, 0))  # 裁剪时画一个矩形框
            self.scene().addItem(self.temp_item)

        self.updateScene([self.sceneRect()])
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        pos = self.mapToScene(event.localPos().toPoint())
        x = int(pos.x())
        y = int(pos.y())
        if self.temp_item is None:
            return
        if self.status == 'line':
            self.temp_item.p_list[1] = [x, y]
        # TODO: 11月修改
        elif self.status == 'polygon' or self.status == 'fill_polygon':
            if self.temp_item is not None:
                self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'ellipse':
            if self.temp_item is not None:
                self.temp_item.p_list[1] = [x, y]
        elif self.status == 'curve':
            if self.temp_item is not None:
                self.temp_item.p_list[-1] = [x, y]
        elif self.status == 'translate':
            self.temp_item.p_list = alg.translate(self.rawList, x - self.begin[0], y - self.begin[1])
            # print(f"the p_list is {self.temp_item.p_list}")
        elif self.status == 'rotate':
            pass
        elif self.status == 'scale':
            pass
        elif self.status == 'clip' or self.status == 'clip_polygon':
            x0, y0 = self.temp_item.p_list[0]  # 裁剪矩形的一个顶点
            self.temp_item.p_list = [[x0, y0], [x0, y], [x, y], [x, y0]]  # 改变裁剪矩形框的顶点参数
        self.updateScene([self.sceneRect()])
        super().mouseMoveEvent(event)

    def add_item(self):
        self.item_dict[self.temp_id] = self.temp_item
        self.list_widget.addItem(self.temp_id)
        self.finish_draw()

    def delete_item(self):  # 删除当前selected的图元
        self.scene().removeItem(self.item_dict.pop(self.selected_id))
        self.selected_id = ''
        self.temp_id = ''
        self.list_widget.takeItem(self.list_widget.row(self.list_widget.selectedItems()[0]))
        self.list_widget.selectionModel().clear()
        self.clear_selection()
        self.main_window.statusBar().showMessage('空闲')
        self.status = ''
        # print(f"has deleted the line item!")

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if self.status == 'line':
            self.add_item()
        # TODO: 11月修改
        elif self.status == 'polygon' or self.status == 'fill_polygon':
            pass
        elif self.status == 'ellipse':
            self.add_item()
        elif self.status == 'curve':
            pass
        elif self.status == 'translate':
            self.rawList = self.temp_item.p_list
        elif self.status == 'rotate':
            self.rawList = self.temp_item.p_list
        elif self.status == 'scale':
            self.rawList = self.temp_item.p_list
        elif self.status == 'clip':
            x_min, y_min = self.temp_item.p_list[0]
            x_max, y_max = self.temp_item.p_list[2]
            if x_min > x_max:
                x_max, x_min = x_min, x_max
            if y_min > y_max:
                y_max, y_min = y_min, y_max
            self.scene().removeItem(self.temp_item)
            theline = self.item_dict[self.selected_id]
            theline.p_list = alg.clip(theline.p_list, x_min, y_min, x_max, y_max, self.temp_algorithm)
            if len(theline.p_list) == 0:
                self.delete_item()

        elif self.status == 'clip_polygon':
            x_min, y_min = self.temp_item.p_list[0]
            x_max, y_max = self.temp_item.p_list[2]
            if x_min > x_max:
                x_max, x_min = x_min, x_max
            if y_min > y_max:
                y_max, y_min = y_min, y_max
            self.scene().removeItem(self.temp_item)
            thepolygon = self.item_dict[self.selected_id]
            # print(f'!poly_list is {thepolygon.p_list}')
            thepolygon.p_list = alg.clip_polygon(thepolygon.p_list,
                                                 [[x_min, y_min], [x_min, y_max], [x_max, y_max], [x_max, y_min]])
            # print(f'!!poly_list is {thepolygon.p_list}')
            self.updateScene([self.sceneRect()])
            if len(thepolygon.p_list) == 0:
                self.delete_item()
        self.updateScene([self.sceneRect()])
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:  # 鼠标滚轮
        if self.begin == []:  # 还没有选择参考点
            return
        self.begin = self.main_window.beginx, self.main_window.beginy
        if self.status == 'rotate':
            if event.angleDelta().y() > 0:
                self.rotate_angle -= 1
                self.main_window.angle = self.rotate_angle
                self.main_window.angle_box.setValue(self.rotate_angle)
            elif event.angleDelta().y() < 0:
                self.rotate_angle += 1
                self.main_window.angle = self.rotate_angle
                self.main_window.angle_box.setValue(self.rotate_angle)
            self.temp_item.p_list = alg.rotate(self.rawList, self.begin[0], self.begin[1], self.rotate_angle)

        elif self.status == 'scale':
            if event.angleDelta().y() > 0:
                self.scale_factor += 0.1
                self.main_window.factor = self.scale_factor
                self.main_window.factor_box.setValue(self.scale_factor)
            elif event.angleDelta().y() < 0:
                self.scale_factor -= 0.1
                self.main_window.factor = self.scale_factor
                self.main_window.factor_box.setValue(self.scale_factor)
            self.temp_item.p_list = alg.scale(self.rawList, self.begin[0], self.begin[1], self.scale_factor)

        self.updateScene([self.sceneRect()])

    def clearCanvas(self):
        '''清空画布的所有图元，以及画布上的所有参数，用于重置画布时调用'''
        for id in self.item_dict:
            self.scene().removeItem(self.item_dict[id])
        self.item_dict = {}
        self.selected_id = ''

        self.status = ''
        self.temp_algorithm = ''
        self.temp_id = ''
        self.temp_item = None
        self.begin = []  # 图形变换时选中的第一个控制点
        self.rawList = []  # 图形变换时原图元控制参数
        self.rotate_angle = 0  # 旋转角度
        self.scale_factor = 1  # 缩放比例
        self.updateScene([self.sceneRect()])


class MyItem(QGraphicsItem):
    """
    自定义图元类，继承自QGraphicsItem
    """

    def __init__(self, item_id: str, item_type: str, p_list: list, algorithm: str = '', color=QColor(0, 0, 0), width = 1,
                 parent: QGraphicsItem = None):
        """

        :param item_id: 图元ID
        :param item_type: 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        :param p_list: 图元参数
        :param algorithm: 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        :param parent:
        """
        super().__init__(parent)
        self.id = item_id  # 图元ID
        self.item_type = item_type  # 图元类型，'line'、'polygon'、'ellipse'、'curve'等
        self.p_list = p_list  # 图元参数
        self.algorithm = algorithm  # 绘制算法，'DDA'、'Bresenham'、'Bezier'、'B-spline'等
        self.selected = False
        self.color = color  # 画笔颜色
        self.width = width # 画笔宽度

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = ...) -> None:
        if len(self.p_list) == 0: return
        if self.item_type == 'line':
            item_pixels = alg.draw_line(self.p_list, self.algorithm)
        elif self.item_type == 'polygon':
            item_pixels = alg.draw_polygon(self.p_list, self.algorithm)
        elif self.item_type == 'fill_polygon':
            item_pixels = alg.fill_polygon(self.p_list)
        elif self.item_type == 'ellipse':
            item_pixels = alg.draw_ellipse(self.p_list)
        elif self.item_type == 'curve':
            item_pixels = alg.draw_curve(self.p_list, self.algorithm)

        for p in item_pixels:
            painter.setPen(QPen(self.color, self.width))
            painter.drawPoint(*p)
        if self.selected:
            painter.setPen(QColor(255, 0, 0))
            painter.drawRect(self.boundingRect())


    def boundingRect(self, item_pixels=None) -> QRectF:
        if len(self.p_list) == 0: return QRectF()
        if self.item_type == 'line':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)
        elif self.item_type == 'polygon' or self.item_type == 'fill_polygon':
            x_list = [p[0] for p in self.p_list]
            y_list = [p[1] for p in self.p_list]
            x_min, x_max = min(x_list), max(x_list)
            y_min, y_max = min(y_list), max(y_list)
            return QRectF(x_min - 1, y_min - 1, x_max - x_min + 2, y_max - y_min + 2)

        elif self.item_type == 'ellipse':
            x0, y0 = self.p_list[0]
            x1, y1 = self.p_list[1]
            x = min(x0, x1)
            y = min(y0, y1)
            w = max(x0, x1) - x
            h = max(y0, y1) - y
            return QRectF(x - 1, y - 1, w + 2, h + 2)

        elif self.item_type == 'curve':
            x_list = [p[0] for p in self.p_list]
            y_list = [p[1] for p in self.p_list]
            x_min, x_max = min(x_list), max(x_list)
            y_min, y_max = min(y_list), max(y_list)
            return QRectF(x_min - 1, y_min - 1, x_max - x_min + 2, y_max - y_min + 2)


class MainWindow(QMainWindow):
    """
    主窗口类
    """

    def __init__(self):
        super().__init__()
        self.item_cnt = 0
        self.set_bezier_num = 4
        self.set_bspline_num = 3
        # 使用QListWidget来记录已有的图元，并用于选择图元。注：这是图元选择的简单实现方法，更好的实现是在画布中直接用鼠标选择图元
        self.list_widget = QListWidget(self)
        self.list_widget.setMinimumWidth(200)
        # 设置画布大小
        self.weight = 900
        self.height = 900

        # 使用QGraphicsView作为画布
        self.scene = QGraphicsScene(self)
        self.scene.setSceneRect(0, 0, self.weight, self.height)
        self.canvas_widget = MyCanvas(self.scene, self)
        self.canvas_widget.setFixedSize(self.weight, self.height)
        # self.canvas_widget.resize(self.weight, self.height)
        self.canvas_widget.main_window = self
        self.canvas_widget.list_widget = self.list_widget
        self.canvas_widget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.canvas_widget.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        # 设置画笔
        self.pen_color = QColor(0, 0, 0)
        self.pen_width = 1

        # 设置菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu('文件')
        set_pen_menu = file_menu.addMenu('设置画笔')
        set_pen_act = set_pen_menu.addAction('设置画笔颜色')
        set_pen_width_act = set_pen_menu.addAction('设置画笔宽度')
        reset_canvas_act = file_menu.addAction('重置画布')
        save_canvas_act = file_menu.addAction('保存画布')
        exit_act = file_menu.addAction('退出')
        draw_menu = menubar.addMenu('绘制')
        line_menu = draw_menu.addMenu('线段')
        line_naive_act = line_menu.addAction('Naive')
        line_dda_act = line_menu.addAction('DDA')
        line_bresenham_act = line_menu.addAction('Bresenham')
        polygon_menu = draw_menu.addMenu('多边形')
        fill_act = draw_menu.addAction('填充多边形')
        polygon_dda_act = polygon_menu.addAction('DDA')
        polygon_bresenham_act = polygon_menu.addAction('Bresenham')
        ellipse_act = draw_menu.addAction('椭圆')
        curve_menu = draw_menu.addMenu('曲线')
        curve_bezier_act = curve_menu.addAction('Bezier')
        curve_b_spline_act = curve_menu.addAction('B-spline')
        edit_menu = menubar.addMenu('编辑')
        translate_act = edit_menu.addAction('平移')
        rotate_act = edit_menu.addAction('旋转')
        scale_act = edit_menu.addAction('缩放')
        remove_act = edit_menu.addAction('删除')

        clip_menu_raw = edit_menu.addMenu('裁剪')
        clip_menu = clip_menu_raw.addMenu('线段裁剪')
        clip_cohen_sutherland_act = clip_menu.addAction('Cohen-Sutherland')
        clip_liang_barsky_act = clip_menu.addAction('Liang-Barsky')
        clip_polygon_act = clip_menu_raw.addAction('多边形裁剪')

        # 连接信号和槽函数
        exit_act.triggered.connect(qApp.quit)
        line_naive_act.triggered.connect(self.line_naive_action)
        self.list_widget.currentTextChanged.connect(self.canvas_widget.selection_changed)
        # TODO: 以下内容在11月修改
        save_canvas_act.triggered.connect(self.save_canvas_action)
        set_pen_act.triggered.connect(self.set_pen_action)
        set_pen_width_act.triggered.connect(self.set_pen_width_action)
        reset_canvas_act.triggered.connect(self.reset_canvas_action)
        line_dda_act.triggered.connect(self.line_dda_action)
        line_bresenham_act.triggered.connect(self.line_bresenham_action)
        polygon_dda_act.triggered.connect(self.polygon_dda_action)
        polygon_bresenham_act.triggered.connect(self.polygon_bresenham_action)
        ellipse_act.triggered.connect(self.ellipse_action)
        curve_bezier_act.triggered.connect(self.curve_bezier_action)
        curve_b_spline_act.triggered.connect(self.curve_b_spline_action)
        translate_act.triggered.connect(self.translate_action)
        rotate_act.triggered.connect(self.rotate_action)
        scale_act.triggered.connect(self.scale_action)
        remove_act.triggered.connect(self.remove_action)
        clip_cohen_sutherland_act.triggered.connect(self.clip_cohen_sutherland_action)
        clip_liang_barsky_act.triggered.connect(self.clip_liang_barsky_action)
        clip_polygon_act.triggered.connect(self.clip_polygon_action)
        fill_act.triggered.connect(self.fill_action)

        # 设置主窗口的布局
        self.hbox_layout = QHBoxLayout()
        self.hbox_layout.addWidget(self.canvas_widget)
        self.hbox_layout.addWidget(self.list_widget, stretch=1)
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.hbox_layout)
        self.setCentralWidget(self.central_widget)
        self.statusBar().showMessage('空闲')
        self.resize(self.weight, self.height)
        self.setWindowTitle('CG 画图')
        self.setWindowIcon(QIcon('./pics/icon.png'))
        # 设置左侧的图形变换时的参数显示
        self.beginx = 0
        self.beginy = 0
        self.angle = 0  # 旋转角度
        self.factor = 1  # 缩放比例
        self.setbar = QToolBar()
        self.addToolBar(Qt.LeftToolBarArea, self.setbar)

        self.beginx_box = QSpinBox()  # 横坐标
        self.beginx_box.setRange(0, self.weight)
        self.beginx_box.setSingleStep(1)
        self.beginx_box.setValue(self.beginx)
        self.beginy_box = QSpinBox()  # 纵坐标
        self.beginy_box.setRange(0, self.height)
        self.beginy_box.setSingleStep(1)
        self.beginy_box.setValue(self.beginy)
        self.angle_box = QSpinBox()  # 旋转角度
        self.angle_box.setRange(-7200, 7200)
        self.angle_box.setSingleStep(1)
        self.angle_box.setValue(self.angle)
        self.factor_box = QDoubleSpinBox()  # 缩放比例
        self.factor_box.setRange(-10, 10)
        self.factor_box.setSingleStep(0.1)
        self.factor_box.setValue(self.factor)
        # 布局
        self.setbar.addWidget(QLabel("图形变换中心x坐标"))
        self.setbar.addWidget(self.beginx_box)
        self.setbar.addWidget(QLabel("图形变换中心y坐标"))
        self.setbar.addWidget(self.beginy_box)
        self.setbar.addWidget(QLabel("旋转角度"))
        self.setbar.addWidget(self.angle_box)
        self.setbar.addWidget(QLabel("缩放比例"))
        self.setbar.addWidget(self.factor_box)

        self.setbar.addSeparator()  # 分隔

        self.beginx_box.setEnabled(False)
        self.beginy_box.setEnabled(False)
        self.factor_box.setEnabled(False)
        self.angle_box.setEnabled(False)

        # print(f"the begin is : {self.canvas_widget.begin}")
        # print(self.canvas_widget.begin)
        self.beginx_box.valueChanged.connect(self.change_beginx)
        self.beginy_box.valueChanged.connect(self.change_beginy)
        self.angle_box.valueChanged.connect(self.change_angle)
        self.factor_box.valueChanged.connect(self.change_factor)


    def change_beginx(self):
        # print(f'x in box is {self.beginx_box.value()}')
        # if self.canvas_widget.status == 'rotate':
        if self.canvas_widget.selected_id == '':
            self.beginx_box.setEnabled(False)
        if self.canvas_widget.selected_id != '':
            self.beginx_box.setEnabled(True)
            self.canvas_widget.begin[0] = self.beginx_box.value()
            self.canvas_widget.rotate_angle = 0
            self.canvas_widget.scale_factor = 1
            # self.angle_box.setValue(0)
            # self.factor_box.setValue(1)
            self.canvas_widget.rawList = self.canvas_widget.temp_item.p_list

    def change_beginy(self):
        # print(f'y in box is {self.beginy_box.value()}')
        # if self.canvas_widget.status == 'rotate':
        if self.canvas_widget.selected_id == '':
            self.beginy_box.setEnabled(False)
        if self.canvas_widget.selected_id != '':
            self.beginy_box.setEnabled(True)
            self.canvas_widget.begin[1] = self.beginy_box.value()
            self.canvas_widget.rotate_angle = 0
            self.canvas_widget.scale_factor = 1
            # self.angle_box.setValue(0)
            # self.factor_box.setValue(1)
            self.canvas_widget.rawList = self.canvas_widget.temp_item.p_list

    def change_angle(self):
        if self.canvas_widget.selected_id == '':
            QMessageBox.warning(self, '注意', '请先在右侧选定图元', QMessageBox.Yes, QMessageBox.Yes)
            return
        # if self.canvas_widget.selected_id != '':
        if self.canvas_widget.status == 'rotate':
            self.angle_box.setEnabled(True)
            self.angle_box.setVisible(True)
            self.factor_box.hide()
            self.factor_box.setEnabled(False)
            if self.canvas_widget.temp_item is None:
                self.rotate_action()
            self.canvas_widget.rotate_angle = self.angle_box.value()
            # print(f"the angle after changing is {self.canvas_widget.rotate_angle}")
            # self.canvas_widget.rawList = self.canvas_widget.temp_item.p_list
            self.canvas_widget.temp_item.p_list = alg.rotate(self.canvas_widget.rawList, self.beginx,
                                                             self.beginy, self.angle_box.value())
            self.canvas_widget.updateScene([self.canvas_widget.sceneRect()])

    def change_factor(self):
        if self.canvas_widget.selected_id == '':
            QMessageBox.warning(self, '注意', '请先在右侧选定图元', QMessageBox.Yes, QMessageBox.Yes)
            return
        # if self.canvas_widget.selected_id != '':
        if self.canvas_widget.status == 'scale':
            self.factor_box.setEnabled(True)
            self.factor_box.setVisible(True)
            self.angle_box.hide()
            self.angle_box.setEnabled(False)
            if self.canvas_widget.temp_item is None:
                self.scale_action()
            self.canvas_widget.scale_factor = self.factor_box.value()
            # self.canvas_widget.rawList = self.canvas_widget.temp_item.p_list
            self.canvas_widget.temp_item.p_list = alg.scale(self.canvas_widget.rawList, self.beginx,
                                                            self.beginy, self.factor_box.value())
            self.canvas_widget.updateScene([self.canvas_widget.sceneRect()])

    def get_id(self):
        _id = str(self.item_cnt)
        self.item_cnt += 1
        return _id

    def save_canvas_action(self):
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()
        self.statusBar().showMessage('保存画布')
        dialog = QFileDialog()
        filename = dialog.getSaveFileName(filter="Image Files(*.jpg *.png *.bmp)")
        if filename[0]:
            self.canvas_widget.save_canvas(filename[0], self.weight, self.height)

    def reset_canvas_action(self):
        self.statusBar().showMessage('重置画布')
        # 设置弹出窗口布局
        dialog = QDialog()
        dialog.setWindowTitle('重置画布')
        formlayout = QFormLayout(dialog)
        # 宽度和高度对话框及其对应的滑块
        box1 = QSpinBox(dialog)
        box1.setRange(100, 900)  # 范围在[100, 800]
        box1.setSingleStep(1)
        box1.setValue(self.weight)
        slider1 = QSlider(Qt.Horizontal)
        slider1.setRange(100, 900)
        slider1.setSingleStep(1)
        slider1.setValue(self.weight)
        slider1.setTickPosition(QSlider.TicksBelow)
        slider1.setTickInterval(100)
        box2 = QSpinBox(dialog)
        box2.setRange(100, 900)
        box2.setSingleStep(1)
        box2.setValue(self.height)
        slider2 = QSlider(Qt.Horizontal)
        slider2.setRange(100, 900)
        slider2.setSingleStep(1)
        slider2.setValue(self.height)
        slider2.setTickPosition(QSlider.TicksBelow)
        slider2.setTickInterval(100)
        slider1.valueChanged.connect(box1.setValue)  # 滑块和box关联
        box1.valueChanged.connect(slider1.setValue)
        slider2.valueChanged.connect(box2.setValue)
        box2.valueChanged.connect(slider2.setValue)
        formlayout.addRow('宽度 ', box1)
        formlayout.addRow(slider1)
        formlayout.addRow('高度 ', box2)
        formlayout.addRow(slider2)
        # 确定取消按钮
        box3 = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        box3.accepted.connect(dialog.accept)
        box3.rejected.connect(dialog.reject)
        formlayout.addRow(box3)

        if dialog.exec():
            self.weight = box1.value()
            self.height = box2.value()
            self.item_cnt = 0  # 清空图元
            self.list_widget.clearSelection()  # 清除图元列表的选择
            self.canvas_widget.clear_selection()  # 清除画布的选择
            self.canvas_widget.clearCanvas()  # 清空画布图元
            self.list_widget.clear()  # 清除图元列表
            self.scene = QGraphicsScene(self)
            self.scene.setSceneRect(0, 0, self.weight, self.height)
            self.canvas_widget.resize(self.weight, self.height)
            self.canvas_widget.setFixedSize(self.weight, self.height)
            self.statusBar().showMessage('空闲')
            # self.setMaximumSize(self.weight, self.height)
            self.setMaximumHeight(self.height)
            self.setMaximumWidth(self.weight)
            self.resize(self.weight, self.height)
            self.beginx_box.setValue(0)
            self.beginy_box.setValue(0)
            self.angle_box.setValue(0)
            self.factor_box.setValue(1)
            self.show()



    def set_pen_action(self):
        self.pen_color = QColorDialog.getColor()
        # print(f"color is : {self.pen_color}")
        self.statusBar().showMessage('设置画笔')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def set_pen_width_action(self):
        width, ok = QInputDialog.getInt(self, '调整粗细', '输入画笔粗细', value=1, min=1, max=10)
        if ok and width > 0:
            self.pen_width = width

    def line_naive_action(self):
        self.canvas_widget.start_draw_line('Naive', self.get_id())
        self.statusBar().showMessage('Naive算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_dda_action(self):
        self.canvas_widget.start_draw_line('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def line_bresenham_action(self):
        self.canvas_widget.start_draw_line('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制线段')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_dda_action(self):
        self.canvas_widget.start_draw_polygon('DDA', self.get_id())
        self.statusBar().showMessage('DDA算法绘制多边形 (按鼠标右键结束绘制)')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def polygon_bresenham_action(self):
        self.canvas_widget.start_draw_polygon('Bresenham', self.get_id())
        self.statusBar().showMessage('Bresenham算法绘制多边形 (按鼠标右键结束绘制)')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def fill_action(self):
        self.canvas_widget.start_fill_polygon(self.get_id())
        self.statusBar().showMessage('绘制填充多边形 (按鼠标右键结束绘制)')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def ellipse_action(self):
        self.canvas_widget.start_draw_ellipse(self.get_id())
        self.statusBar().showMessage('绘制椭圆')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_bezier_action(self):
        self.canvas_widget.start_draw_curve('Bezier', self.get_id())
        self.statusBar().showMessage('Bezier算法绘制曲线 (按鼠标右键结束绘制)')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def curve_b_spline_action(self):
        self.canvas_widget.start_draw_curve('B-spline', self.get_id())
        self.statusBar().showMessage('绘制B-spline曲线 (按鼠标右键结束绘制)')
        self.list_widget.clearSelection()
        self.canvas_widget.clear_selection()

    def unable_box(func): # 在类里定义一个装饰器装饰函数
        def wrapper(self):
            self.beginx_box.setEnabled(False)
            self.beginy_box.setEnabled(False)
            self.factor_box.setEnabled(False)
            self.angle_box.setEnabled(False)
            return func(self)
        return wrapper

    @unable_box
    def translate_action(self):
        self.canvas_widget.start_translate()
        self.statusBar().showMessage('平移操作')

    @unable_box
    def rotate_action(self):
        self.canvas_widget.start_rotate()
        self.statusBar().showMessage('旋转操作')

    @unable_box
    def scale_action(self):
        self.canvas_widget.start_scale()
        self.statusBar().showMessage('缩放操作')

    @unable_box
    def remove_action(self):
        self.canvas_widget.start_remove()
        self.statusBar().showMessage('删除操作')

    @unable_box
    def clip_cohen_sutherland_action(self):
        self.statusBar().showMessage('Cohen-Sutherland算法裁剪操作')
        self.canvas_widget.start_clip('Cohen-Sutherland')

    @unable_box
    def clip_liang_barsky_action(self):
        self.statusBar().showMessage('Liang-Barsky算法裁剪操作')
        self.canvas_widget.start_clip('Liang-Barsky')

    @unable_box
    def clip_polygon_action(self):
        self.statusBar().showMessage('多边形裁剪操作')
        self.canvas_widget.start_clip_polygon()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())
