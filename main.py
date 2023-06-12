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


# форматирование координат вершин к нужному виду
def normalization_coordinate(list_data, string):
    for item in list_data:
        string += ",".join(map(str, item[0])) + ';'
    return string.rstrip(';')


# подготовка данных для записи, перевод в строку
def data_preparation(data):
    string = ''
    for item in data:
        if item.get('shapename') == "круг":
            string += '@' + str(item.get('start')).strip('[]') + '$' + str(item.get('radius'))
        else:
            string += '!' + ",".join(map(str, item.get('start'))) + '$' + normalization_coordinate(item.get('vertex'),
                                                                                                   '')
        string += '#\n'
    return string.replace(' ', '')


# запись в файл
def write_to_file(data):
    file = open('output.txt', 'w')
    try:
        string_data = data_preparation(data)
        file.write(string_data)
    finally:
        file.close()


# число точек персечения с описанным квадратом
def count_find_data(array_find, data_array):
    count_exists = 0
    for item in array_find:
        if item in data_array:
            count_exists += 1
    return count_exists


# функция определяющая окружность это или нет
def is_circle(approx, x, y, width, height):
    array_data_x = []
    array_data_y = []

    for item in approx:
        array_data_x.append(item[0][0])
        array_data_y.append(item[0][1])

    array_x = [x - 1, x, x + 1, x + width - 1, x + width, x + width + 1]
    array_y = [y - 1, y, y + 1, y + height - 1, y + height, y + height + 1]
    count_exists = count_find_data(array_x, array_data_x)
    count_exists += count_find_data(array_y, array_data_y)

    return 4 <= count_exists <= 6


# распознование фигур и их данные
def shape_recognition(contours, image):
    i = 0
    print('Количество фигур на картинке: ', len(contours))
    data = []

    for contour in contours:

        # максимальное расстояние от исходного контура до приблизительного. Это параметр точности
        epsilon = 0.01 * cv2.arcLength(contour, True)
        # приближает форму контура к другой форме контура, состоящей из меньшего количества точек
        approx = cv2.approxPolyDP(contour, epsilon, True)
        x, y, width, height = cv2.boundingRect(approx)

        shape_dict = {}
        shape_name = ''

        isSquare = -15 < width - height < 15

        if len(approx) == 3:
            shape_name = "треугольник"
            cv2.drawContours(image, [contour], 0, (0, 255, 0), -1)  # зеленый
        elif len(contour) == 4 and isSquare:
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
        elif len(approx) > 13 and is_circle(approx, x, y, width, height):
            shape_name = "круг"
            template_string = Template('${i} - это ${shapename} \n' +
                                       'Координата начала фигуры (центр): ${start} \n' +
                                       'Радиус:\n ${radius} \n' +
                                       '------------------')
            radius = float(width / 2)
            shape_dict = {'i': i + 1, 'shapename': shape_name, 'start': [float(x + radius), float(y + radius)],
                          'radius': radius}
            cv2.drawContours(image, [contour], 0, (0, 255, 255), -1)  # желтый
        else:
            shape_name = "другая фигура"
            cv2.drawContours(image, [contour], 0, (0, 150, 255), -1)  # оранжевый

        if len(shape_dict) == 0:
            template_string = Template('${i} - это ${shapename} \n' +
                                       'Координата в пикселях начала фигуры: ${start} \n' +
                                       'Координаты всех вершин фигуры:\n ${vertex} \n' +
                                       '------------------')
            shape_dict = {'i': i + 1, 'shapename': shape_name, 'start': approx[0][0], 'vertex': approx}
        data.append(shape_dict)
        prepared_string = template_string.substitute(**shape_dict)
        print(prepared_string)
        i += 1
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
