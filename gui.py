from os import listdir
from os.path import isfile, join
import cv2 as cv
import os
import PySimpleGUI as sg
from PIL import Image

from model import Imgproc, predict


class GUI:
    chosen_images = []
    result = []

    @staticmethod
    def convert_jpg(file_names):
        new_file_names = []
        for file_name in file_names:
            if file_name.lower().endswith(".jpg"):
                im1 = Image.open(file_name)
                new_file_name = file_name[:-3] + "png"
                im1.save(new_file_name)
                os.remove(file_name)
                new_file_names.append(new_file_name)
            else:
                new_file_names.append(file_name)
        return new_file_names

    def resize(self, file_list, folder):
        for file in file_list:
            path = os.path.join(folder, file)
            if os.path.isfile(path) and file.lower().endswith((".png", ".jpg")):
                img = Image.open(path)
                img = img.resize((200, 250), Image.ANTIALIAS)

                resized_folder = folder + "/resized/"
                os.makedirs(resized_folder, exist_ok=True)

                img.save(resized_folder + file)

                only_files = [file for file in listdir(folder) if isfile(join(folder, file))]
                self.remove_duplicates(only_files, folder)

    @staticmethod
    def remove_duplicates(only_files, folder):
        for element in only_files:
            if element.startswith("resized"):
                os.remove(join(folder, element))

    def get_chosen_images(self):
        return set(image for image in self.chosen_images)

    @staticmethod
    def set_layout():
        file_list_column = [
            [
                sg.Text("Image Folder"),
                sg.In(size=(25, 1), enable_events=True, key="-FOLDER-"),
                sg.FolderBrowse(),
            ],
            [
                sg.Listbox(
                    values=[], enable_events=True, size=(40, 20),
                    key="-FILE LIST-"
                )
            ],
        ]

        image_viewer_column = [
            [sg.Text("Chose an image from the list on the left")],
            [sg.Text(size=(40, 1), key="-TOUT-")],
            [sg.Image(key="-IMAGE-")],
            [sg.Button(button_text="Select", key="-SELECT-")],
            [sg.Button(button_text="Finish", key="-FINISH-")],
        ]

        layout = [
            [
                sg.Column(file_list_column),
                sg.VSeparator(),
                sg.Column(image_viewer_column),
            ]
        ]

        return layout

    def execute_loop(self, window):
        while True:
            event, values = window.read()
            if event == "Exit" or event == sg.WIN_CLOSED:
                break
            if event == "-FOLDER-":
                folder = values["-FOLDER-"]
                try:
                    file_list = os.listdir(folder)
                except:
                    file_list = []

                file_names = [
                    file
                    for file in file_list
                    if os.path.isfile(os.path.join(folder, file)) and file.lower().endswith((".png", ".jpg"))
                ]
                new_file_names = self.convert_jpg(file_names)

                window["-FILE LIST-"].update(new_file_names)

                self.resize(file_list, folder)

            elif event == "-FILE LIST-":
                try:
                    filepath = os.path.join(
                        values["-FOLDER-"], values["-FILE LIST-"][0]
                    )
                    filepath_for_image = os.path.join(
                        values["-FOLDER-"] + "/resized/", values["-FILE LIST-"][0]
                    )
                    window["-TOUT-"].update(filepath)
                    window["-IMAGE-"].update(filename=filepath_for_image)
                except:
                    print("error updating file list")
                    pass
            elif event == "-SELECT-":
                try:
                    chosen_image = os.path.join(
                        values["-FOLDER-"], values["-FILE LIST-"][0]
                    )
                    self.chosen_images.append(chosen_image)
                    print("images chosen so far: ", self.chosen_images)
                except:
                    print("error selecting image")
                    pass
            elif event == "-FINISH-":
                set_of_chosen_images = self.get_chosen_images()
                # manual model tests
                # set_of_chosen_images.add(
                #     "/Users/noza/PycharmProjects/pythonProjectForBach/res/290978592_410423371050212_1989803757001338259_n.png")
                # set_of_chosen_images.add(
                #     "/Users/noza/PycharmProjects/pythonProjectForBach/res/291307308_830842587879300_6353551203256119599_n.png")
                # set_of_chosen_images.add(
                #     "/Users/noza/PycharmProjects/pythonProjectForBach/res/292558063_733013441086984_6023155613697219977_n.png")
                # set_of_chosen_images.add(
                #     "/Users/noza/PycharmProjects/pythonProjectForBach/res/292719156_594589688725836_5474120213232334654_n (1).png")
                # set_of_chosen_images.add(
                #     "/Users/noza/PycharmProjects/pythonProjectForBach/res/292778808_1694970860883792_3614812385310202276_n (1).png")

                for image_path in set_of_chosen_images:
                    read_image = cv.imread(image_path)
                    model = Imgproc(read_image)
                    os.listdir()

                    self.result.append(predict(read_image, os.getcwd() + "/model"))
                    # print(result)
                break

