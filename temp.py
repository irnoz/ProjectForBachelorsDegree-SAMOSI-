from os import listdir
from os.path import isfile, join
import os
import PySimpleGUI as sg
from PIL import Image


def convertJPG(fnames):
    new_fnames = []
    for file_name in fnames:
        if file_name.lower().endswith(".jpg"):
            im1 = Image.open(file_name)
            new_file_name = file_name[:-3] + "png"
            im1.save(new_file_name)
            os.remove(file_name)
            new_fnames.append(new_file_name)
        else:
            new_fnames.append(file_name)
    return new_fnames


def resize(file_list, folder):
    for file in file_list:
        path = os.path.join(folder, file)
        if os.path.isfile(path) and file.lower().endswith((".png", ".jpg")):
            img = Image.open(path)
            img = img.resize((200, 250), Image.ANTIALIAS)

            resized_folder = folder + "/resized/"
            os.makedirs(resized_folder, exist_ok=True)

            img.save(resized_folder + file)

            onlyfiles = [f for f in listdir(folder) if isfile(join(folder, f))]
            for element in onlyfiles:
                if element.startswith("resized"):
                    os.remove(join(folder, element))

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

window = sg.Window("Image Viewer", layout)

resized_folder = ""

chosen_image = ""
chosen_images = []
result = {}

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

        fnames = [
            file
            for file in file_list
            if os.path.isfile(os.path.join(folder, file)) and file.lower().endswith((".png", ".jpg"))
        ]
        new_fnames = convertJPG(fnames)

        window["-FILE LIST-"].update(new_fnames)

        resize(file_list, folder)

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
            chosen_images.append(chosen_image)
            print("images chosen so far: ", chosen_images)
        except:
            print("error selecting image")
            pass
    elif event == "-FINISH-":
        break

print("images chosen so are: ", chosen_images)
set_of_chosen_images = set(image for image in chosen_images)
print(len(set_of_chosen_images))
window.close()
