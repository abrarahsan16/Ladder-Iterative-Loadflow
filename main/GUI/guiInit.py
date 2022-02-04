import PySimpleGUI as sg

def gui_initial():
    
    # Colour personalizations 
    sg.theme('SandyBeach')
    #Layout Initialization to get the overall GUI setup 
    layout =  [[sg.Text('Choose the Excel file in CDF form')],
            [sg.In() ,sg.FileBrowse(file_types=(("Excel Files", "*.xlsx"),))],  #File browser to select Excel file with data
               [sg.Text('error tolerance', size =(15, 1)), sg.InputText()] ,       #Error Tolerance text box so it can be changed as per specs of user
               [sg.Submit(), sg.Cancel()]]                                         #Buttons to submit/cancel
    window = sg.Window('Ladder Iterative Load Flow Calculator', layout)            #GUI heading
    event, values = window.read()
    window.close()

    if (values[1]==None):
        values[1]=0.0001                                                          # to be used to extract data by data parser.

    return event, values[0], values[1]                                          #Stored values of the excel file address and error tolerance