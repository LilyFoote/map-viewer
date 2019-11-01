import pathlib
import sys
import tkinter as tk

from PIL import Image, ImageTk


def handle_command(command, active_tiles):
    operation, sep, tile = command.rpartition(' ')
    try:
        tile_path = TILES[tile]
    except KeyError:
        return

    if operation == '':
        if tile_path in active_tiles:
            operation = 'hide'
        else:
            operation = 'show'

    if operation == 'show':
        active_tiles.add(tile_path)
    elif operation == 'hide':
        active_tiles.discard(tile_path)


def get_image(active_tiles):
    new_image = Image.open(BLACK)
    for path in active_tiles:
        image = Image.open(path)
        new_image.paste(image, (0, 0), image)
    return ImageTk.PhotoImage(new_image)


class ScrollCanvas(tk.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._starting_drag_position = ()
        self._addMouseBindings()
        self.pack(fill=tk.BOTH, expand=tk.YES)

    def _addMouseBindings(self):
        self.bind("<Button-1>", self.__start_scroll)
        self.bind("<B1-Motion>", self.__update_scroll)
        self.bind("<ButtonRelease-1>", self.__stop_scroll)

    def __start_scroll(self, event):
        # set the scrolling increment.
        # value of 0 is unlimited and very fast
        # set it to 1,2,3 or whatever to make it slower
        self.config(yscrollincrement=3)
        self.config(xscrollincrement=3)
        self._starting_drag_position = (event.x, event.y)

    def __update_scroll(self, event):
        deltaX = event.x - self._starting_drag_position[0]
        deltaY = event.y - self._starting_drag_position[1]
        self.xview('scroll', -deltaX, 'units')
        self.yview('scroll', -deltaY, 'units')
        self._starting_drag_position = (event.x, event.y)

    def __stop_scroll(self, event):
        # set scrolling speed back to 0, so that mouse scrolling
        # works as expected.
        self.config(xscrollincrement=0)
        self.config(yscrollincrement=0)


if __name__ == '__main__':
    try:
        directory = sys.argv[1]
    except IndexError:
        print('You need to provide a directory containing the map images.')

    images = pathlib.Path(directory).glob('*.png')
    TILES = {path.stem: path.as_posix() for path in images}
    print('Available tile names:', ', '.join(sorted(TILES.keys())))
    BLACK = TILES['black']

    window = tk.Tk()
    background = Image.open(BLACK)
    width, height = background.size
    canvas = ScrollCanvas(window, width=width, height=height, background='black')

    active_tiles = set()
    while True:
        window.update()
        try:
            command = input()
        except EOFError:
            sys.exit()

        handle_command(command, active_tiles)
        new_image = get_image(active_tiles)
        rendered_map = canvas.create_image(0, 0, anchor=tk.NW, image=new_image)
