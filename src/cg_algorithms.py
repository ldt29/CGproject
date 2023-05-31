#!/usr/bin/env python
# -*- coding:utf-8 -*-

# 本文件只允许依赖math库
import math


def draw_line(p_list, algorithm):
    """绘制线段
    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'，此处的'Naive'仅作为示例，测试时不会出现
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    result = []
    if algorithm == 'Naive':
        if x0 == x1:
            for y in range(y0, y1 + 1):
                result.append([x0, y])
        else:
            if x0 > x1:
                x0, y0, x1, y1 = x1, y1, x0, y0
            k = (y1 - y0) / (x1 - x0)
            for x in range(x0, x1 + 1):
                result.append([x, int(y0 + k * (x - x0))])
    elif algorithm == 'DDA':
        if x0 == x1:
            for y in range(min(y0, y1), max(y0, y1) + 1):
                result.append([x0, y])
        elif y0 == y1:
            for x in range(min(x0, x1), max(x0, x1) + 1):
                result.append([x, y0])
        else:
            k = (y1 - y0) / (x1 - x0)
            if abs(k) <= 1:
                if x0 > x1:  # make sure x is adding
                    x0, y0, x1, y1 = x1, y1, x0, y0
                yi = y0
                for x in range(x0, x1 + 1):
                    result.append([x, round(yi)])
                    yi += k
            else:
                if y0 > y1:  # make sure y is adding
                    x0, y0, x1, y1 = x1, y1, x0, y0
                xi = x0
                for y in range(y0, y1 + 1):
                    result.append([xi, round(y)])
                    xi += 1 / k
    elif algorithm == 'Bresenham':
        if x0 == x1:
            for y in range(min(y0, y1), max(y0, y1) + 1):
                result.append([x0, y])
        elif y0 == y1:
            for x in range(min(x0, x1), max(x0, x1) + 1):
                result.append([x, y0])
        else:
            dy, dx, ex = abs(y1 - y0), abs(x1 - x0), 0
            if dy > dx:  # the |k| > 1, need exchange x, y
                dx, dy = dy, dx
                ex = 1
                x0, y0, x1, y1 = y0, x0, y1, x1
            if x0 > x1:  # make sure x is adding
                x0, y0, x1, y1 = x1, y1, x0, y0
            s = (1 if y0 < y1 else -1)
            p = 2 * dy - dx
            y = y0
            for x in range(x0, x1 + 1):
                if ex == 1:  # exchange x, y
                    result.append([y, x])
                else:
                    result.append([x, y])
                if p > 0:
                    p = p + 2 * dy - 2 * dx
                    y += s
                else:
                    p = p + 2 * dy

    return result


def draw_polygon(p_list, algorithm):
    """绘制多边形

    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 多边形的顶点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'DDA'和'Bresenham'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    for i in range(len(p_list)):
        line = draw_line([p_list[i - 1], p_list[i]], algorithm)
        result += line
    return result


def draw_ellipse(p_list):
    """绘制椭圆（采用中点圆生成算法）

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 椭圆的矩形包围框左上角和右下角顶点坐标
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    result = []
    x0, y0 = p_list[0]
    x1, y1 = p_list[1]
    a, b = int(abs(x1 - x0) / 2), int(abs(y0 - y1) / 2)
    a2, b2 = a * a, b * b
    x, y = 0, b
    xc, yc = int((x0 + x1) / 2), int((y0 + y1) / 2)  # vector need to be added
    # p_k = b2 * pow((x + 1), 2) + a2 * pow((y - 1 / 2), 2) - a2 * b2
    p_k = b2 - a2 * y + a2 / 4
    result.append([x, y])
    while 2 * b2 * x < 2 * a2 * y:
        if p_k < 0:
            p_k = p_k + 2 * b2 * x + 3 * b2
        else:
            p_k = p_k + 2 * b2 * x - 2 * a2 * y + 2 * a2 + 3 * b2
            y -= 1
        x += 1
        result.append([x, y])
    p_k = b2 * pow((x + 1 / 2), 2) + a2 * pow((y - 1), 2) - a2 * b2
    while y > 0:
        if p_k > 0:
            p_k = p_k - 2 * a2 * y + 3 * a2
        else:
            x += 1
            p_k = p_k + 2 * b2 * x - 2 * a2 * y + 2 * b2 + 3 * a2
        y -= 1
        result.append([x, y])

    result2, result3, result4 = [], [], []
    for p in result:
        result2.append([-p[0], p[1]])
        result3.append([-p[0], -p[1]])
        result4.append([p[0], -p[1]])

    result += result2 + result3 + result4
    result = [[p[0] + xc, p[1] + yc] for p in result]
    return result


def draw_curve(p_list, algorithm):
    """绘制曲线
    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 曲线的控制点坐标列表
    :param algorithm: (string) 绘制使用的算法，包括'Bezier'和'B-spline'（三次均匀B样条曲线，曲线不必经过首末控制点）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 绘制结果的像素点坐标列表
    """
    res = []
    if algorithm == 'Bezier':
        n = len(p_list) - 1
        loc = [[[0, 0]] * (n + 1)] * (n + 1)  # 阶数r从0~n共(n+1)阶，每一阶的点数为(n+1-r)
        loc[0] = p_list  # 初始化0阶点为控制点
        for v in range(1001):
            u = v / 1000  # u取值(0, 1)
            for r in range(1, n + 1):  # 从上到下，阶数从1到n
                for i in range(0, n - r + 1):  # 从左到右
                    loc[r][i] = [(1 - u) * loc[r - 1][i][0] + u * loc[r - 1][i + 1][0],
                                 (1 - u) * loc[r - 1][i][1] + u * loc[r - 1][i + 1][1]]
            res.append([round(loc[n][0][0]), round(loc[n][0][1])])
        return res
    elif algorithm == 'B-spline':
        def curve_point(i, u):  # 第i条曲线上参数为u的点坐标
            t = []
            point = [0, 0]
            t += [-u ** 3 + 3 * u ** 2 - 3 * u + 1, 3 * u ** 3 - 6 * u ** 2 + 4,
                  -3 * u ** 3 + 3 * u ** 2 + 3 * u + 1, u ** 3]
            for j in range(4):  # 每条曲线涉及4个控制点
                point[0] += t[j] * p_list[i + j][0]
                point[1] += t[j] * p_list[i + j][1]
            point[0], point[1] = point[0] / 6, point[1] / 6
            return point

        n = len(p_list) - 1  # 控制点从0开始编号
        for i in range(n - 2):  # k=4为阶数，一共n+1-(k-1)=n-2条三次曲线
            for v in range(1001):
                u = v / 1000  # 每条曲线上u从(0, 1)
                p = curve_point(i, u)
                res.append([round(p[0]), round(p[1])])
    return res


def translate(p_list, dx, dy):
    """平移变换
    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param dx: (int) 水平方向平移量
    :param dy: (int) 垂直方向平移量
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    return [[x + dx, y + dy] for [x, y] in p_list]


def rotate(p_list, x, y, r):
    """旋转变换（除椭圆外）
    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 旋转中心x坐标
    :param y: (int) 旋转中心y坐标
    :param r: (int) 顺时针旋转角度（°）
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    res = []
    theta = math.radians(r)
    cos = math.cos(theta)
    sin = math.sin(theta)
    for p in p_list:
        x1 = x + (p[0] - x) * cos - (p[1] - y) * sin
        y1 = y + (p[0] - x) * sin + (p[1] - y) * cos
        res.append([round(x1), round(y1)])
    return res


def scale(p_list, x, y, s):
    """缩放变换
    :param p_list: (list of list of int: [[x0, y0], [x1, y1], [x2, y2], ...]) 图元参数
    :param x: (int) 缩放中心x坐标
    :param y: (int) 缩放中心y坐标
    :param s: (float) 缩放倍数
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1], [x_2, y_2], ...]) 变换后的图元参数
    """
    res = []
    for p in p_list:
        res.append([round(x + (p[0] - x) * s), round(y + (p[1] - y) * s)])
    return res


def clip(p_list, x_min, y_min, x_max, y_max, algorithm):
    """线段裁剪

    :param p_list: (list of list of int: [[x0, y0], [x1, y1]]) 线段的起点和终点坐标
    :param x_min: 裁剪窗口左上角x坐标
    :param y_min: 裁剪窗口左上角y坐标
    :param x_max: 裁剪窗口右下角x坐标
    :param y_max: 裁剪窗口右下角y坐标
    :param algorithm: (string) 使用的裁剪算法，包括'Cohen-Sutherland'和'Liang-Barsky'
    :return: (list of list of int: [[x_0, y_0], [x_1, y_1]]) 裁剪后线段的起点和终点坐标
    """
    x1, y1 = p_list[0]
    x2, y2 = p_list[1]

    if y_min > y_max:
        y_max, y_min = y_min, y_max

    def encode(x, y):  # 给定点[x, y]返回编码
        code = 0
        if y > y_max:
            code |= 8
        elif y < y_min:
            code |= 4
        if x > x_max:
            code |= 2
        elif x < x_min:
            code |= 1
        return code

    if algorithm == 'Cohen-Sutherland':
        c1, c2 = encode(x1, y1), encode(x2, y2)
        if c1 == 0 and c2 == 0:  # 全部保留
            return p_list

        while True:  # 不断裁剪知道全部保留或舍弃
            if c1 & c2 != 0:  # 全部舍弃
                return []
            elif c1 == 0 and c2 == 0:  # 全部保留
                return [[round(x1), round(y1)], [round(x2), round(y2)]]

            if c1 == 0:  # 找到边界外的那个点
                x1, x2, y1, y2 = x2, x1, y2, y1
                c1, c2 = c2, c1

            if c1 & 8 == 8:  # 上边界外
                x1 = x1 + (y_max - y1) * (x2 - x1) / (y2 - y1)
                y1 = y_max
            elif c1 & 4 == 4:  # 下边界外
                x1 = x1 + (y_min - y1) * (x2 - x1) / (y2 - y1)
                y1 = y_min
            elif c1 & 2 == 2:  # 右边界外
                y1 = y1 + (y2 - y1) * (x_max - x1) / (x2 - x1)
                x1 = x_max
            elif c1 & 1 == 1:  # 左边界外
                y1 = y1 + (y2 - y1) * (x_min - x1) / (x2 - x1)
                x1 = x_min
            c1 = encode(x1, y1)  # 更新c1和c2的编码
            c2 = encode(x2, y2)

    elif algorithm == 'Liang-Barsky':
        dx, dy = x2 - x1, y2 - y1
        p = [-dx, dx, -dy, dy]
        q = [x1 - x_min, x_max - x1, y1 - y_min, y_max - y1]
        u1, u2 = 0, 1
        for k in range(4):
            if p[k] == 0 and q[k] < 0:  # 全部舍弃
                return []
            elif p[k] < 0:  # 入边
                u1 = max(u1, q[k] / p[k])
            elif p[k] > 0:  # 出边
                u2 = min(u2, q[k] / p[k])
        if u1 > u2:  # 全部舍弃
            return []
        return [[round(x1 + u1 * (x2 - x1)), round(y1 + u1 * (y2 - y1))],
                [round(x1 + u2 * (x2 - x1)), round(y1 + u2 * (y2 - y1))]]


class Node:
    def __init__(self, x=0, dx=0.0, y_max=0, nxt=None):
        self.x = x
        self.dx = dx
        self.y_max = y_max
        self.next = nxt

    def set_next(self, nxt):
        self.next = nxt


def create_net(y_max, y_min, p_list, n):
    NET = []
    for i in range(0, y_max + 1):
        node = Node()
        NET.append(node)
    for i in range(y_min, y_max + 1):  # 从下到上创建NET
        for j in range(0, n):
            if p_list[j][1] == i:  # 遇到一个顶点将其作为边中的较低点
                x0, y0 = p_list[j]
                x1, y1 = p_list[(j - 1 + n) % n]  # 左右两条边
                if y1 > y0:
                    node = Node(x0, float((x1 - x0) / (y1 - y0)), y1, NET[i].next)
                    NET[i].set_next(node)
                x1, y1 = p_list[(j + 1 + n) % n]
                if y1 > y0:
                    node = Node(x0, float((x1 - x0) / (y1 - y0)), y1, NET[i].next)
                    NET[i].set_next(node)
    return NET


def fill_polygon(p_list):
    result = []
    y_max, y_min = -9999, 9999
    for x, y in p_list:
        if y > y_max:
            y_max = y
        if y < y_min:
            y_min = y

    AET = Node()

    n = len(p_list)
    NET = create_net(y_max, y_min, p_list, n)  # 创建NET

    for i in range(y_min, y_max + 1):  # 从下到上处理扫描线
        node1 = NET[i].next
        node2 = AET
        while node1 is not None:  # 将NET对应边插入AET中,并在插入时对x进行排序
            while node2.next is not None and node1.x >= node2.next.x:
                node2 = node2.next
            temp = node1.next
            node1.set_next(node2.next)
            node2.set_next(node1)
            node1 = temp
            node2 = AET

        node1 = AET  # 删除y_max == y_k的边否则保留
        node2 = node1.next
        while node2 is not None:
            if node2.y_max == i:
                node1.set_next(node2.next)
                node2 = node1.next
            else:
                node1 = node1.next
                node2 = node2.next

        node = AET.next

        while node is not None:  # 计算AET中扫描线和边交点的横坐标x = x + 1/m
            node.x = node.x + node.dx
            node = node.next

        node1 = AET  # 对AET表按照x重新排序
        node2 = AET.next
        node1.set_next(None)
        while node2 is not None:
            while node1.next is not None and node2.x >= node1.next.x:
                node1 = node1.next
            temp = node2.next
            node2.set_next(node1.next)
            node1.set_next(node2)
            node2 = temp
            node1 = AET

        node = AET.next
        while node is not None and node.next is not None:
            x = int(node.x)
            while x <= node.next.x:
                result.append([x, i])
                x = x + 1
            node = node.next.next  # 将一对点之间的像素点加入到结果中

    return result


def is_inside(p1, p2, q):
    """
    判断点q是否在线段p1p2的内侧
    """
    R = (p2[0] - p1[0]) * (q[1] - p1[1]) - (p2[1] - p1[1]) * (q[0] - p1[0])
    if R <= 0:
        return True
    else:
        return False


def compute_intersection(p1, p2, p3, p4):
    """
    计算p1p2和p3p4两条线段的交点
    """
    if p2[0] - p1[0] == 0:
        x = p1[0]
        m2 = (p4[1] - p3[1]) / (p4[0] - p3[0])
        b2 = p3[1] - m2 * p3[0]
        y = m2 * x + b2

    elif p4[0] - p3[0] == 0:
        x = p3[0]
        m1 = (p2[1] - p1[1]) / (p2[0] - p1[0])
        b1 = p1[1] - m1 * p1[0]
        y = m1 * x + b1
    else:
        m1 = (p2[1] - p1[1]) / (p2[0] - p1[0])
        b1 = p1[1] - m1 * p1[0]

        m2 = (p4[1] - p3[1]) / (p4[0] - p3[0])
        b2 = p3[1] - m2 * p3[0]

        x = (b2 - b1) / (m1 - m2)
        y = m1 * x + b1

    return [x, y]


def clip_polygon(p_list, clip_list):
    """
    p_list是被裁减多边形的顶点参数
    clip_list是裁剪窗口的顶点参数
    返回裁剪后的多边形的顶点参数
    """
    result = p_list.copy()

    for i in range(len(clip_list)):
        # 一条边一条边迭代裁剪
        next_polygon = result.copy()

        result = []

        # 下面两个点确定裁剪窗口的一条边
        c_edge_start = clip_list[i - 1]
        c_edge_end = clip_list[i]

        for j in range(len(next_polygon)):

            # 下面两个点确定被裁减多边形的一条边
            s_edge_start = next_polygon[j - 1]
            s_edge_end = next_polygon[j]

            if is_inside(c_edge_start, c_edge_end, s_edge_end):
                if not is_inside(c_edge_start, c_edge_end, s_edge_start): #终点在窗口内起点在窗口外
                    intersection = compute_intersection(s_edge_start, s_edge_end, c_edge_start, c_edge_end)
                    result.append(intersection)
                result.append(s_edge_end) # 结果为交点和终点
            elif is_inside(c_edge_start, c_edge_end, s_edge_start): # 终点在外起点在窗口内
                intersection = compute_intersection(s_edge_start, s_edge_end, c_edge_start, c_edge_end)
                result.append(intersection)

    result = [[round(p[0]), round(p[1])] for p in result]
    return result
