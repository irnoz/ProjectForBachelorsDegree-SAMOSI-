from gui import GUI
import PySimpleGUI as sg
import pandas as pd
import os
import platform

from model import Imgproc, predict
import cv2 as cv

gui = GUI()

sg.theme('SandyBeach')

window = sg.Window("Image Viewer", gui.set_layout())

gui.execute_loop(window)

list_of_results = gui.result
# set_of_chosen_images = gui.get_chosen_images()
# print("images chosen are: ", set_of_chosen_images)
# print(len(set_of_chosen_images))
window.close()

layout = [
    [sg.Text('please enter the name of the excel file you want to write to')],
    [sg.Text('Name', size=(15, 1)), sg.InputText()],
    [sg.Submit(), sg.Cancel()],
]

window = sg.Window('Simple data entry window', layout)
event, value = window.read()
excel_file_name = value[0]
window.close()

if platform.system() == "Windows":
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
else:
    desktop_path = os.path.join(os.path.join(os.path.expanduser('~')), 'Desktop')

sheet_index = 1
path = desktop_path + "/" + excel_file_name + ".xlsx"
writer = pd.ExcelWriter(path, engine='xlsxwriter')

for result in list_of_results:
    values = []
    indices = []

    for values_as_tuple in result:

        values.append(values_as_tuple[0])
        indices.append(values_as_tuple[1])
    df = pd.DataFrame([int(value) for value in values], index=indices)
    sheet_name = "Sheet" + str(sheet_index)
    workbook = writer.book
    writer.sheets = {sheet_name: workbook.add_worksheet()}
    worksheet = writer.sheets[sheet_name]
    df.to_excel(writer, sheet_name=sheet_name, index=True)
    chart = workbook.add_chart({'type': 'column'})
    chart.add_series({'values': '='+sheet_name+'!$B$3:$B$9'})
    worksheet.insert_chart('D1', chart)
    sheet_index += 1
writer.close()



# for result in list_of_results:
#     values = []
#     indices = []
#     for values_as_tuple in result:
#         values.append(values_as_tuple[0])
#         indices.append(values_as_tuple[1])
#     df = pd.DataFrame(values, index=indices)
#     df.to_excel(desktop_path + "/" + excel_file_name + ".xlsx", sheet_name="Sheet" + str(sheet_index))
#     sheet_index += 1

# path = 'pandas_to_excel.xlsx'


# with pd.ExcelWriter(path) as writer:
#     writer.book = openpyxl.load_workbook(path)
#     df.to_excel(writer, sheet_name='new_sheet1')
#     df2.to_excel(writer, sheet_name='new_sheet2')


# image = cv.imread("/Users/noza/PycharmProjects/pythonProjectForBach/res/290978592_410423371050212_1989803757001338259_n.jpg")
# model = Imgproc(image)
# list = predict(image, "/Users/noza/PycharmProjects/pythonProjectForBach/model")
# print(list)