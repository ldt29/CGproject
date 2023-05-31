#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import sys

import numpy as np
from PIL import Image

import cg_algorithms as alg

input_file = sys.argv[1]
output_dir = sys.argv[2]
os.makedirs(output_dir, exist_ok=True)
item_dict = {}
pen_color = np.zeros(3, np.uint8)
width = 0
height = 0


def reset_canvas(line):
    global width, height, item_dict
    width = int(line[1])
    height = int(line[2])
    item_dict = {}


def save_canvas(line):
    global height, width, item_dict
    save_name = line[1]
    canvas = np.zeros([height, width, 3], np.uint8)
    canvas.fill(255)
    for item_type, p_list, algorithm, color in item_dict.values():
        if item_type == 'line':
            pixels = alg.draw_line(p_list, algorithm)
            for x, y in pixels:
                canvas[y, x] = color
        elif item_type == 'polygon':
            pixels = alg.draw_polygon(p_list, algorithm)
            for x, y in pixels:
                canvas[y, x] = color
        elif item_type == 'ellipse':
            pixels = alg.draw_ellipse(p_list)
            for x, y in pixels:
                canvas[int(y), int(x)] = color
        elif item_type == 'curve':
            pixels = alg.draw_curve(p_list, algorithm)
            for x, y in pixels:
                canvas[y, x] = color
    Image.fromarray(canvas).save(os.path.join(output_dir, save_name + '.bmp'), 'bmp')


def set_color(line):
    global pen_color
    pen_color[0] = int(line[1])
    pen_color[1] = int(line[2])
    pen_color[2] = int(line[3])


def draw_line(line):
    global item_dict
    item_id = line[1]
    x0 = int(line[2])
    y0 = int(line[3])
    x1 = int(line[4])
    y1 = int(line[5])
    algorithm = line[6]
    item_dict[item_id] = ['line', [[x0, y0], [x1, y1]], algorithm, np.array(pen_color)]


# TODO: 以下内容均在11月修改
def draw_polygon(line):
    global item_dict
    item_id = line[1]
    p_list = []
    for i in range(2, len(line) - 2, 2):
        p_list.append([int(line[i]), int(line[i + 1])])
    # print(f"poly p_list is {p_list}")
    algorithm = line[-1]
    item_dict[item_id] = ['polygon', p_list, algorithm, np.array(pen_color)]


def draw_ellipse(line):
    global item_dict
    item_id = line[1]
    p_list = [[int(line[2]), int(line[3])], [int(line[4]), int(line[5])]]
    item_dict[item_id] = ['ellipse', p_list, None, np.array(pen_color)]


def draw_curve(line):
    global item_dict
    item_id = line[1]
    p_list = []
    for i in range(2, len(line) - 2, 2):
        p_list.append([int(line[i]), int(line[i + 1])])
    algorithm = line[-1]
    item_dict[item_id] = ['curve', p_list, algorithm, np.array(pen_color)]


def translate(line):
    global item_dict
    item_id = line[1]
    p_list = item_dict[item_id][1]  # 图元原本的参数
    dx, dy = int(line[2]), int(line[3])
    item_dict[item_id][1] = alg.translate(p_list, dx, dy)  # 修改成平移后的参数


def rotate(line):
    global item_dict
    item_id = line[1]
    p_list = item_dict[item_id][1]  # 图元原本的参数
    x, y, r = int(line[2]), int(line[3]), float(line[4])
    item_dict[item_id][1] = alg.rotate(p_list, x, y, r)  # 修改成旋转后的参数


def scale(line):
    global item_dict
    item_id = line[1]
    p_list = item_dict[item_id][1]  # 图元原本的参数
    x, y, s = int(line[2]), int(line[3]), float(line[4])
    item_dict[item_id][1] = alg.scale(p_list, x, y, s)  # 修改成缩放后的参数


def clip(line):
    global item_dict
    item_id = line[1]
    p_list = [item_dict[item_id][1][0], item_dict[item_id][1][1]]  # 图元原本的参数，p_list是线段的起点和终点
    x_min, y_min, x_max, y_max, algorithm = int(line[2]), int(line[3]), int(line[4]), int(line[5]), line[6]
    item_dict[item_id][1] = alg.clip(p_list, x_min, y_min, x_max, y_max, algorithm)  # 修改成裁剪后的参数


func_dict = {
    'resetCanvas': reset_canvas,
    'saveCanvas': save_canvas,
    'setColor': set_color,
    'drawLine': draw_line,
    'drawPolygon': draw_polygon,
    'drawEllipse': draw_ellipse,
    'drawCurve': draw_curve,
    'translate': translate,
    'rotate': rotate,
    'scale': scale,
    'clip': clip,
}

if __name__ == '__main__':

    with open(input_file, 'r') as fp:
        line = fp.readline()
        while line:
            line = line.strip().split(' ')
            try:
                func_dict[line[0]](line)
            except KeyError:
                print(f'[ERROR] :You call the nonexistent func: {line[0]}!!!')
                exit()
            # print(width, height, item_dict, pen_color)
            line = fp.readline()
