import os
import tkinter as tk
from tkinter import *  # without this we cant us the uppercase tk.constants
from tkinter import messagebox
from PIL import Image, ImageTk
import psutil
import sys

# =======================================================Globals====================================================== #

Image.MAX_IMAGE_PIXELS = 933120000  # without this line we will get an error when we will try to access the user folder
                                    # from windows
# those are some file extensions
audio_extensions = ['aif', 'cda', 'mid', 'midi', 'mp3', 'mpa', 'ogg', 'wav', 'wma', 'wpl']
video_extensions = ['3g2', '3gp', 'avi', 'flv', 'h264', 'm4v', 'mkv', 'mov', 'mp4', 'mpg', 'mpeg', 'rm', 'swf', 'vob',
                    'wmv']

# =======================================================Classes====================================================== #


class Element:
    def __init__(self, name):
        self.name = name
        self.raw_name = name
        self.index = 0
        self.isSelected = False
        self.representation = []
        self.process_name()

    def process_name(self):
        for i in range(100-(len(self.name))//2):
            self.name += '  '

    def show(self, index):
        e0 = tk.Label(main_frame_bg, text=self.name, bg='#f2f2f2')  # file name
        e0.grid(row=index, column=2, sticky=W)
        e0.bind("<Button-1>", lambda event: app.select(self, event))
        e0.bind("<Double-Button-1>", lambda event: app.open(event))
        self.representation.append(e0)

    def select(self):
        # by selecting we change the background color
        if not self.isSelected:
            self.isSelected = True
            for i in self.representation:
                i.config(bg='#78c3de')
            app.set_selected_element(self)
        else:
            self.deselect()

    def deselect(self):
        self.isSelected = False
        for i in self.representation:
            i.config(bg='#f2f2f2')

    def set_index(self, index):
        self.index = index

    def get_name(self):
        return self.name[:get_last_character(self.name)+1]

    def delete(self):
        for i in self.representation:
            i.grid_forget()
        self.representation.clear()

    def __repr__(self):
        return f'{self.name}'


class Folder(Element):
    def __init__(self, name):
        Element.__init__(self, name)
        self.isBackFolder = False

    def is_back_folder(self):
        return self.isBackFolder

    def show(self, index):
        Element.show(self, index)
        e2 = tk.Label(main_frame_bg, image=folder_img, height=17)
        e2.grid(row=index, column=1)
        e2.bind("<Button-1>", lambda event: app.select(self, event))
        e2.bind("<Double-Button-1>", lambda event: app.open(event))
        self.representation.append(e2)

    def back_folder(self):
        self.isBackFolder = True
        e0 = tk.Label(main_frame_bg, image=back_folder_img, height=17, bg='#f2f2f2')
        e0.grid(row=0, column=1)
        e0.bind("<Button-1>", lambda event: app.select(self, event))
        e1 = tk.Label(main_frame_bg, text='Back'+self.name, bg='#f2f2f2')
        e1.grid(row=0, column=2, sticky=W)
        e1.bind("<Button-1>", lambda event: app.select(self, event))
        e1.bind("<Double-Button-1>", lambda event: app.open(event))
        self.representation.append(e0)
        self.representation.append(e1)


class File(Element):
    def __init__(self, name, extension):
        Element.__init__(self, name)
        self.extension = extension[0]
        self.extension_index = extension[1]

    def show(self, index):
        Element.show(self, index)
        e2 = tk.Label(main_frame_bg, image=file_img, height=17)
        e2.grid(row=index, column=1)
        e2.bind("<Button-1>", lambda event: app.select(self, event))
        self.representation.append(e2)

    def get_extension(self):
        return self.extension

    def get_name(self):
        return self.name[:self.extension_index+(len(self.extension)+1)]


class ImageFile(File):
    def __init__(self, name, extension):
        File.__init__(self, name, extension)

    def show(self, index):
        Element.show(self, index)
        e2 = tk.Label(main_frame_bg, image=image_img, height=17)
        e2.grid(row=index, column=1)
        e2.bind("<Button-1>", lambda event: app.select(self, event))
        self.representation.append(e2)


class AudioFile(File):
    def __init__(self, name, extension):
        File.__init__(self, name, extension)

    def show(self, index):
        Element.show(self, index)
        e2 = tk.Label(main_frame_bg, image=audio_img, height=17)
        e2.grid(row=index, column=1)
        e2.bind("<Button-1>", lambda event: app.select(self, event))
        self.representation.append(e2)


class VideoFile(File):
    def __init__(self, name, extension):
        File.__init__(self, name, extension)

    def show(self, index):
        Element.show(self, index)
        e2 = tk.Label(main_frame_bg, image=video_img, height=17)
        e2.grid(row=index, column=1)
        e2.bind("<Button-1>", lambda event: app.select(self, event))
        self.representation.append(e2)


class Browser:
    def __init__(self):
        self.files = []
        self.folders = []
        self.images = []
        self.audios = []
        self.videos = []
        self.path = os.getcwd()
        self.back_folder = None
        self.new_folder_name = ''
        self.index = 0
        self.selected_element = None
        self.update()
        self.show_all()

    def set_partition(self, event=None):
        partition_selector.bind("<Configure>", lambda event: self.change_partition(partitions.get(), event))

    def change_partition(self, which, event=None):
        os.chdir(which)
        change_entry_path(which)
        self.deselect()
        self.refresh()

    @staticmethod
    def get_partitions():
        s = []
        for partition in psutil.disk_partitions():
            s.append(partition[0])
        return s
        pass

    def get_current_partition(self):
        for i in self.get_partitions():
            if i in os.getcwd():
                return i

    def open(self, event=None):
        if self.selected_element is not None:
            if isinstance(self.selected_element, Folder):  # we will check if it is a folder
                if self.selected_element.is_back_folder():
                    go_back()
                    self.path = get_back_folder(self.path)
                else:
                    try:
                        open_folder(self.selected_element.get_name())
                    except PermissionError:  # if we are not allowed to enter the folder
                        go_back()
                        self.path = get_back_folder(self.path)
                        messagebox.showwarning("Access denied", "You don't have the permission to open this folder")
                scroll_bar.config(commad=bg_canvas.yview("moveto", 0))  # this function sets the viewport at the
                #                                                        beginning of the folder
            elif isinstance(self.selected_element, File):
                print(f"opening {self.selected_element.get_name()}, {self.selected_element.get_extension()}")
            self.deselect()

    def deselect(self):
        if self.selected_element:  # if it is not None
            self.selected_element.deselect()
            self.selected_element = None
            name_entry.configure(state='normal')
            name_entry.delete(0, 'end')
            name_entry.configure(state='readonly')

    def select(self, which, event=None):
        if self.selected_element is not None:
            self.deselect()
        self.selected_element = which
        which.select()
        name_entry.configure(state='normal')
        name_entry.delete(0, 'end')
        name_entry.insert(0, which.raw_name)
        name_entry.configure(state='readonly')

    def get_type(self, selected_element=None):
        if selected_element is None:
            selected_element = self.selected_element
        if selected_element in self.folders:
            return 0
        elif selected_element in self.files:
            return 1
        elif selected_element in self.images:
            return 2
        elif selected_element in self.audios:
            return 3
        elif selected_element in self.videos:
            return 4

    def get_list(self, p=-1):
        if p == -1:
            p = self.get_type()
        if p == 0:
            return self.folders
        elif p == 1:
            return self.files
        elif p == 2:
            return self.images
        elif p == 3:
            return self.audios
        else:
            return self.videos

    def get_first_element(self):
        if len(self.folders) > 0:
            return self.folders[0]
        elif len(self.files) > 0:
            return self.files[0]
        elif len(self.images) > 0:
            return self.images[0]
        elif len(self.audios) > 0:
            return self.audios[0]
        elif len(self.videos) > 0:
            return self.videos[0]
        else:
            return None

    def get_last_element(self):
        if len(self.videos) > 0:
            return self.videos[-1]
        elif len(self.audios) > 0:
            return self.audios[-1]
        elif len(self.images) > 0:
            return self.images[-1]
        elif len(self.files) > 0:
            return self.files[-1]
        elif len(self.folders) > 0:
            return self.folders[-1]
        else:
            return None

    def get_index(self):
        return self.get_list().index(self.selected_element)

    @staticmethod
    def get_scroll_length():
        return bg_canvas.yview()[1]-bg_canvas.yview()[0]

    def get_unit(self):
        return self.get_scroll_length()/21  # there are 21 elements listed once a time

    def scroll(self, where):  # 0 - up, 1 - down
        unit = self.get_unit()
        if where == 0:
            if self.selected_element == self.get_first_element():
                bg_canvas.yview('moveto', 0)
            elif bg_canvas.yview()[0] != 0 and bg_canvas.yview()[0] > unit:
                if self.selected_element.index*unit < bg_canvas.yview()[0]:
                    bg_canvas.yview('moveto', bg_canvas.yview()[0] - unit)
        else:
            if self.selected_element == self.get_last_element():
                bg_canvas.yview('moveto', 1)
            elif bg_canvas.yview()[0] != 1 and bg_canvas.yview()[0] < 1:
                if self.selected_element.index*unit > bg_canvas.yview()[0]+unit*20:
                    bg_canvas.yview('moveto', bg_canvas.yview()[0] + unit)

    def go_to_last(self, event=None):
        if self.selected_element is None:
            self.select(self.back_folder)
        else:
            if self.selected_element != self.back_folder:
                if self.get_type() == 0 and self.get_index() == 0:
                    self.select(self.back_folder)
                else:
                    l = self.get_list()
                    if len(l) == 1:
                        return False
                    try:
                        if self.get_index() == 0:
                            raise IndexError  # we are raising this exception 'cause we want to get into except branch
                        else:
                            l[self.get_index()-1]
                    except IndexError:
                        a = self.get_type()
                        while a != 0:
                            li = self.get_list(a - 1)
                            if len(li) > 0:
                                self.select(li[-1])
                                self.scroll(0)
                                return True
                            a -= 1
                        return False
                    else:
                        self.select(l[self.get_index() - 1])
                        self.scroll(0)

    def go_to_next(self, event=None):
        if self.selected_element is None:
            self.select(self.back_folder)
        else:
            if self.selected_element == self.back_folder:
                if len(self.folders) > 0:
                    self.select(self.folders[0])
                elif len(self.files) > 0:
                    self.select(self.files[0])
                elif len(self.images) > 0:
                    self.select(self.images[0])
                elif len(self.audios) > 0:
                    self.select(self.audios[0])
                elif len(self.videos) > 0:
                    self.select(self.videos[0])
            elif self.selected_element is None:
                self.select(self.back_folder)
            else:
                l = self.get_list()
                if self.get_type() != 4 or self.get_index() != 0:
                    if len(l) == 1:
                        return False
                    try:
                        l[self.get_index()+1]
                    except IndexError:
                        a = self.get_type()
                        while a != 4:
                            li = self.get_list(a+1)
                            if len(li) > 0:
                                self.select(li[0])
                                self.scroll(1)
                                return True
                            a += 1
                        return False
                    else:
                        self.select(l[self.get_index() + 1])
                        self.scroll(1)

    def make_folder(self, name):
        self.folders.append(Folder(name))

    def set_new_folder_name(self, event):
        name_entry.unbind("<Return>")
        if os.path.isdir(name_entry.get()):
            done = False
            s = 1
            while not done:
                try:
                    if name_entry.get()[-1] == ')':
                        index = 0
                        for i in range(len(name_entry.get())-1, 0, -1):
                            if name_entry.get()[i] == '(' and i < len(name_entry.get()) - 2:
                                index = i
                                break
                        if index != 0:
                            os.mkdir(os.getcwd() + f'\\{name_entry.get()[:index]} ({s})')
                        else:
                            os.mkdir(os.getcwd()+f'\\{name_entry.get()} ({s})')
                    else:
                        os.mkdir(os.getcwd() + f'\\{name_entry.get()} ({s})')
                except FileExistsError:
                    s += 1
                else:
                    done = True
        else:
            os.mkdir(os.getcwd() + f'\\{name_entry.get()}')
        name_entry.delete(0, 'end')
        name_entry.configure(state='readonly')
        self.refresh()
        root.bind("<Return>", lambda event: app.open(event))

    def new_folder(self):
        name_entry.configure(state='normal')
        name_entry.delete(0, 'end')
        name_entry.bind("<Return>", lambda event: self.set_new_folder_name(event))
        root.unbind("<Return>")
        self.deselect()

    def set_selected_element(self, element):
        self.selected_element = element

    def get_selected_element(self):
        return self.selected_element

    def save(self):
        pass

    def make_file(self, name, extension):
        self.files.append(File(name, extension))

    def make_image(self, name, extension):
        self.images.append(ImageFile(name, extension))

    def make_audio(self, name, extension):
        self.audios.append(AudioFile(name, extension))

    def make_video(self, name, extension):
        self.videos.append(VideoFile(name, extension))

    def update(self):
        for item in os.listdir(os.getcwd()):
            if os.path.isdir(item):
                self.make_folder(item)
            elif os.path.isfile(item):
                if is_audio(item):
                    self.make_audio(item, get_extension(item))
                elif is_video(item):
                    self.make_video(item, get_extension(item))
                elif is_image(os.getcwd()+'\\'+item):
                    self.make_image(item, get_extension(item))
                else:
                    self.make_file(item, get_extension(item))

    def show_files(self):
        for file in self.files:
            if file.isSelected:
                file.select()
            file.show(self.index)
            file.set_index(self.index)
            self.index += 1

    def show_images(self):
        for image in self.images:
            if image.isSelected:
                image.select()
            image.show(self.index)
            image.set_index(self.index)
            self.index += 1

    def show_audios(self):
        for audio in self.audios:
            if audio.isSelected:
                audio.select()
            audio.show(self.index)
            audio.set_index(self.index)
            self.index += 1

    def show_videos(self):
        for video in self.videos:
            if video.isSelected:
                video.select()
            video.show(self.index)
            video.set_index(self.index)
            self.index += 1

    def create_back(self):
        if how_many_bfolders(os.getcwd()) > 0:  # check if we can go back
            self.back_folder = Folder("")
            self.back_folder.back_folder()
            self.back_folder.set_index(0)
            self.index += 1

    def show_folders(self):
        for folder in self.folders:
            if folder.isSelected:
                folder.select()
            folder.show(self.index)
            folder.set_index(self.index)
            self.index += 1

    def show_all(self):
        self.create_back()
        self.show_folders()
        self.show_files()
        self.show_images()
        self.show_audios()
        self.show_videos()
        self.index = 0

    def hide_files(self):
        for file in self.files:
            file.delete()
        self.files.clear()

    def hide_folders(self):
        for folder in self.folders:
            folder.delete()
        self.folders.clear()

    def hide_images(self):
        for image in self.images:
            image.delete()
        self.images.clear()

    def hide_audios(self):
        for audio in self.audios:
            audio.delete()
        self.audios.clear()

    def hide_videos(self):
        for video in self.videos:
            video.delete()
        self.videos.clear()

    def hide_all(self):
        self.hide_files()
        self.hide_folders()
        self.hide_images()
        self.hide_audios()
        self.hide_videos()

    def refresh(self):
        self.hide_all()
        self.update()
        self.show_all()


# ======================================================Functions===================================================== #

def scroll_function(event):
    bg_canvas.configure(scrollregion=bg_canvas.bbox("all"), width=610, height=435)


def add_data():
    # global main_frame_bg
    for i in range(50):
        Label(main_frame_bg, text=i).grid(row=i, column=0)
        Label(main_frame_bg, text=f"file {i}").grid(row=i, column=1, sticky=W)
        Label(main_frame_bg, text=" ... ").grid(row=i, column=2)


def how_many_bfolders(string, i=0):
    if check_back(string):
        i += 1
        return how_many_bfolders(get_back_folder(string), i)
    else:
        return i


def get_back_folder(string):
    l = string.split('\\')
    if len(l) > 2:
        return '\\'.join(l[0:-1])
    else:
        return l[0] + '\\'


def check_back(string):  # with this function we will see if we can get out from the current directory
    if get_back_folder(string) != string:
        return True
    else:
        return False


def navigate_back(string):
    if check_back(string):
        return get_back_folder(string)
    return string


def change_entry_path(string):
    path_entry.configure(state='normal')
    path_entry.delete(0, 'end')
    path_entry.insert(0, string)
    path_entry.configure(state='readonly')


def select_element(event, element):
    element.select()


def go_back(event=None):
    if check_back(os.getcwd()):
        os.chdir(navigate_back(os.getcwd()))
        change_entry_path(os.getcwd())
        app.refresh()


def change_directory(path):
    os.chdir(path)
    app.refresh()


def open_folder(name):
    path = os.getcwd()
    if path[-1] != '\\':
        path += '\\' + name
    else:
        path += name
    change_directory(path)
    change_entry_path(path)


def get_last_character(string, character=None):
    last_character = 0
    if character is not None:
        for i in range(len(string)):
            if string[i] == character:
                last_character = i
    else:
        for i in range(len(string)):
            if string[i] != ' ':
                last_character = i
    return last_character


def get_extension(name):
    last_dot = get_last_character(name, '.')
    return name[last_dot::], last_dot-1


def is_image(path):
    try:
        Image.open(path)
    except IOError:
        return False
    return True


def is_audio(name):
    if get_extension(name)[0][1::] in audio_extensions:
        return True
    else:
        return False


def is_video(name):
    if get_extension(name)[0][1::] in video_extensions:
        return True
    else:
        return False


def is_partition(name):
    for i in psutil.disk_partitions():
        if name == str(i.device):
            return True
    return False


# this function will convert our paths to be able to use in the executable, im using pyinstaller to create the .exe
def resource_path(relative_path):
    # source: https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile/13790741#13790741
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# =========================================================GUI======================================================== #

root = tk.Tk()
root.geometry("800x500")
root.title("File Browser")
root.resizable(False, False)
root.configure(bg='#d1d1d1')

# frames

path_frame = tk.Frame(root, bg='#d1d1d1', width=653, height=30)
path_frame.place(x=0, y=0)

partition_frame = tk.Frame(root, bg='#d1d1d1', width=35, height=18, bd=0, relief=RAISED)
partition_frame.place(x=623, y=6)

main_frame = tk.Frame(root, bg='#ededed', relief=GROOVE, width=630, height=440)
main_frame.place(x=20, y=30)

name_frame = tk.Frame(root, bg='#d1d1d1', width=650, height=30)
name_frame.place(x=0, y=470)

command_frame = tk.Frame(root, bg='#d1d1d1', width=150, height=540)
command_frame.place(x=650, y=0)

command_frame_btns = tk.Frame(command_frame, bg='#d1d1d1', width=130, height=540)
command_frame_btns.place(x=command_frame.winfo_reqwidth()*.075, rely=0)

# scroll part

bg_canvas = tk.Canvas(main_frame, width=630, height=440, bg='#f2f2f2')
main_frame_bg = tk.Frame(bg_canvas)

scroll_bar = tk.Scrollbar(main_frame, orient="vertical", command=bg_canvas.yview)

bg_canvas.configure(yscrollcommand=scroll_bar.set)
scroll_bar.pack(side='right', fill='y')
bg_canvas.pack(side='left')
bg_canvas.create_window((0, 0), window=main_frame_bg, anchor='nw')
main_frame_bg.bind("<Configure>", scroll_function)

# buttons

new_folder_btn = tk.Button(command_frame_btns, text='New Folder', bg='gray', fg='white', width=18
                           , command=lambda: app.new_folder())
new_folder_btn.place(x=0, y=4)

open_btn = tk.Button(command_frame_btns, text='Open', bg='gray', fg='white', width=18, command=lambda: app.open())
open_btn.place(x=0, rely=.8)

cancel_btn = tk.Button(command_frame_btns, text='Cancel', bg='gray', fg='white', width=18, command=lambda: sys.exit())
cancel_btn.place(x=0, rely=.8678)

# entries

path_entry = tk.Entry(path_frame, bg='white', text='s', width=110)
path_entry.place(x=20, y=5)
path_entry.insert(0, os.getcwd())
path_entry.configure(state='readonly')

name_entry = tk.Entry(name_frame, bg='white', width=110)
name_entry.place(x=20, y=5)
name_entry.configure(state='readonly')

# images

folder_img = ImageTk.PhotoImage(Image.open(resource_path("assets/folder.png")))
back_folder_img = ImageTk.PhotoImage(Image.open(resource_path("assets/back_folder.png")))
file_img = ImageTk.PhotoImage(Image.open(resource_path("assets/file.png")))
image_img = ImageTk.PhotoImage(Image.open(resource_path("assets/image.png")))
audio_img = ImageTk.PhotoImage(Image.open(resource_path("assets/audio.png")))
video_img = ImageTk.PhotoImage(Image.open(resource_path("assets/video.png")))

# binds

root.bind("<Return>", lambda event: app.open(event))
root.bind("<Escape>", lambda event: sys.exit())
root.bind("<Button-2>", scroll_function)
root.bind("<Up>", lambda event: app.go_to_last(event))
root.bind("<Down>", lambda event: app.go_to_next(event))

app = Browser()

# partitions

partitions = Variable(partition_frame)
partitions.set(app.get_current_partition())
partition_selector = OptionMenu(partition_frame, partitions, *app.get_partitions())
partition_selector.config(bd=0, bg='white', relief='raised', font=('Arial', 8), pady=0)
partition_selector.pack()
partition_selector.bind("<Button-1>", lambda event: app.set_partition(event))

root.mainloop()
