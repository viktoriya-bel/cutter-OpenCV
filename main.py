import tkinter as tk
from string import Template
from tkinter.filedialog import askopenfilename
import cv2
import os


# Открытие картинки с геометрическими фигурами
def open_file():
    root = tk.Tk()
    filename = tk.filedialog.askopenfilename(
        title='Выберите файл...',
    )
    root.destroy()
    return cv2.imread(os.path.relpath(filename, start=None))


# получение контуров фигур
def get_contours(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(gray, 127, 255, 1)
    # поиск контуров
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
    return contours


# запись в файл
def write_to_file(data):
    pass


# распознование фигур и их данные
def shape_recognition(contours, image):
    i = 0
    print('len(contours)', len(contours))
    data = []
    for contour in contours:
        print('len(cnt)', len(contour))

        # максимальное расстояние от исходного контура до приблизительного. Это параметр точности
        epsilon = 0.01 * cv2.arcLength(contour, True)
        # приближает форму контура к другой форме контура, состоящей из меньшего количества точек
        approx = cv2.approxPolyDP(contour, epsilon, True)
        # print(len(approx))

        x, y, width, height = cv2.boundingRect(approx)
        # print('approx[0]', approx[0])
        # print('approx[1]', approx[1])
        # print('approx[len(approx) / 2]', approx[int(len(approx) / 2) - 1])
        # print('approx[len(approx)-1]', approx[len(approx) - 1])
        print('x', x)
        print('y', y)
        print('w', width)
        print('h', height)

        shape_dict = {}
        shape_name = ''

        if len(approx) == 3:
            shape_name = "треугольник"
            cv2.drawContours(image, [contour], 0, (0, 255, 0), -1)  # зеленый
        elif len(contour) == 4 & int(round(width / height)) == 1:
            shape_name = "квадрат"
            cv2.drawContours(image, [contour], 0, (0, 0, 255), -1)  # красный
        elif len(contour) == 4:
            shape_name = "прямоугольник"
            cv2.drawContours(image, [contour], 0, (255, 0, 255), -1)  # розовый
        elif len(approx) == 5:
            shape_name = "пятиугольник"
            cv2.drawContours(image, [contour], 0, 255, -1)  # синий
        elif len(approx) == 9:
            shape_name = "полукруг"
            cv2.drawContours(image, [contour], 0, (255, 255, 0), -1)  # бирюзовый
        # elif 9 < len(approx) < 15 & int(round(w / h)) != 1:
        #     print("овал")
        #     cv2.drawContours(image, [contour], 0, (0, 255, 150), -1)  # салатовый
        elif len(approx) > 15:
            shape_name = "круг"
            template_string = Template('${i} - это ${shapename} \n' +
                                       'Координата начала фигуры (центр): ${start} \n' +
                                       'Радиус:\n ${radius} \n' +
                                       '------------------')
            radius = float(width / 2)
            shape_dict = {'i': i, 'shapename': shape_name, 'start': [float(x + radius), float(y + radius)],
                          'radius': radius}
            cv2.drawContours(image, [contour], 0, (0, 255, 255), -1)  # желтый
            continue
        else:
            shape_name = "другая фигура"
            cv2.drawContours(image, [contour], 0, (0, 150, 255), -1)  # оранжевый
        if len(shape_dict) == 0:
            template_string = Template('${i} - это ${shapename} \n' +
                                       'Координата в пикселях начала фигуры: ${start} \n' +
                                       'Координата всех вершин фигуры:\n ${vertex} \n' +
                                       '------------------')
            shape_dict = {'i': i, 'shapename': shape_name, 'start': approx[0][0], 'vertex': approx}
        data.append(shape_dict)
        prepared_string = template_string.substitute(**shape_dict)
        print(prepared_string)
        i = i + 1
    write_to_file(data)


class Main:
    def __init__(self):
        super().__init__()
        self.init_main()

    def init_main(self):
        try:
            image = open_file()
        except Exception:
            print('Произошла ошибка открытия файла!')
        else:
            contours = get_contours(image)
            shape_recognition(contours, image)

            cv2.imshow('image', image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()


if __name__ == "__main__":
    Main()
