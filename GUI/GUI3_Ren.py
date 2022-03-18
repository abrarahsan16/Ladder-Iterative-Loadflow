#Save File GUI
import PySimpleGUI as sg
import pandas as pd 



sg.theme('SandyBeach')
layout = [[
    sg.InputText(key='File to Save', default_text='filename', enable_events=True),
    sg.InputText(key='Save As', do_not_clear=False, enable_events=True, visible=False),
    sg.FileSaveAs(initial_folder='/tmp')   
]]  
window = sg.Window('BV01.Save File', layout)

while True:
    event, values = window.Read()
    print("event:", event, "values: ",values)

    if event is None or event == 'Exit':
        break
    elif event == 'Save As':
        filename = values['Save As']
        if filename:
            window['File to Save'].update(value=filename)
    excel_data = pd.read_excel('output.xls')
    data = pd.DataFrame(excel_data, columns=['From Node', 'To Node', 'R', 'X',])
    print("The content of the file is:\n", data)
window.close()