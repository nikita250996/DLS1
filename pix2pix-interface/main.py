from tkinter import *
from datetime import datetime

import cv2
import numpy as np
from PIL import ImageTk, ImageColor, ImageDraw, Image
from make_height_map import proceed_sketch

canvas_width = 256
canvas_height = 256
brush_size = 10
hex_colour = "#000000"
rgb_colour = (0, 0, 0)
current_time = str(datetime.time(datetime.now())).replace(":", "")
sketch_name = "sketch.png"
height_map_name = "height_map.png"


# Пики —  #00ff00,
# впадины — #005c00,
# дороги — #ffdb00,
# плоские возвышенности — #ad1dd8,
# хребты — #ff0000,
# реки — #0000ff.


class Info:
    def __init__(self, input_file, model_dir, output_file):
        self.input_file = input_file
        self.model_dir = model_dir
        self.output_file = output_file


def reset_coordinates(event):
    canvas.x = None
    canvas.y = None


def paint(event):
    if hex_colour in ["#00ff00", "#005c00"]:
        canvas.create_rectangle(
            event.x,
            event.y,
            event.x + brush_size,
            event.y,
            fill=hex_colour,
            outline=hex_colour,
        )
        draw.rectangle([event.x, event.y, event.x + brush_size, event.y], rgb_colour)
    elif canvas.x and canvas.y:
        canvas.create_line(
            canvas.x, canvas.y, event.x, event.y, fill=hex_colour, width=brush_size
        )
        draw.line([canvas.x, canvas.y, event.x, event.y], rgb_colour, brush_size)
    canvas.x = event.x
    canvas.y = event.y


def save_sketch():
    global current_time
    global sketch_name
    current_time = str(datetime.time(datetime.now())).replace(":", "")
    sketch_name = "sketch_" + current_time + ".png"
    image.save(sketch_name)
    sketch = cv2.imread(sketch_name, -1)
    sketch = np.array(sketch, dtype=np.uint16)
    sketch = cv2.normalize(sketch, None, 0, 65535, cv2.NORM_MINMAX)
    cv2.imwrite(sketch_name, sketch)


def use_net():
    global height_map_name
    save_sketch()
    height_map_name = "height_map_" + current_time + ".png"
    weights_folder = "export"
    a = Info(sketch_name, weights_folder, height_map_name)
    proceed_sketch(a)
    height_map = cv2.imread(height_map_name, -1)[:, :, 0]
    reload_result()
    height_map = cv2.GaussianBlur(height_map, (5, 5), 0)
    cv2.imwrite(height_map_name, height_map)


def load_image():
    try:
        return ImageTk.PhotoImage(Image.open(height_map_name))
    except FileNotFoundError:
        return ImageTk.PhotoImage(
            image=Image.fromarray(np.zeros((256, 256, 3), dtype=np.uint8))
        )


def reload_result():
    global result_image
    result_image = load_image()
    result.configure(image=result_image)
    result.image = result_image


def clear_image():
    global image
    global draw
    image = Image.new("RGB", (canvas_width, canvas_height), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    cv2.imwrite(height_map_name, np.zeros((256, 256, 3), dtype=np.uint16))
    reload_result()


def change_colour(new_colour):
    global hex_colour
    global rgb_colour
    global brush_size
    hex_colour = new_colour
    rgb_colour = ImageColor.getrgb(new_colour)
    brush_size = 10 if hex_colour == "#000000" else 1


root = Tk()
root.title("Генератор ландшафтов")
root.resizable(False, False)

left = Frame()  # buttons are attached here

canvas = Canvas(width=canvas_width, height=canvas_height, bg="#000000")

eraser = Button(left, width=20, text="Ластик", command=lambda: change_colour("#000000"))
ridge = Button(left, width=20, text="Хребет", command=lambda: change_colour("#ff0000"))
river = Button(left, width=20, text="Река", command=lambda: change_colour("#0000ff"))
peak = Button(left, width=20, text="Пик", command=lambda: change_colour("#00ff00"))
basin = Button(left, width=20, text="Впадина", command=lambda: change_colour("#005c00"))
road = Button(left, width=20, text="Дорога", command=lambda: change_colour("#ffdb00"))
tower = Button(
    left,
    width=20,
    text="Плоская возвышенность",
    command=lambda: change_colour("#ad1dd8"),
)
clear = Button(
    left,
    width=20,
    text="Стереть всё",
    command=lambda: [canvas.delete("all"), clear_image()],
)
convert = Button(left, width=20, text="→", command=lambda: use_net())

result_image = load_image()
result = Label(image=result_image)

left.pack(side=LEFT)

canvas.pack(side=LEFT)

eraser.pack()
ridge.pack()
river.pack()
peak.pack()
basin.pack()
road.pack()
tower.pack()
clear.pack()
convert.pack()

result.pack(side=RIGHT)

canvas.bind("<B1-Motion>", paint)
canvas.bind("<Button-1>", paint)
canvas.bind("<ButtonRelease-1>", reset_coordinates)

image = Image.new("RGB", (canvas_width, canvas_height), (0, 0, 0))
draw = ImageDraw.Draw(image)

canvas.x = None
canvas.y = None

root.iconbitmap("icon.ico")
root.mainloop()
