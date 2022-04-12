import PySimpleGUI as sg

def gui_initial():
    
    # Colour personalizations 
    sg.theme('DarkAmber')
    #Layout Initialization to get the overall GUI setup 
    layout =  [[sg.Text('Choose the Excel file in CDF form')],
               [sg.In() ,sg.FileBrowse(file_types=(("Excel Files", "*.xlsx"),))],  #File browser to select Excel file with data
               [sg.Text('Error Tolerance', size =(15, 1)), sg.Combo(['0.001','0.0001','0.00001','0.000001'],default_value='0.001',key='tol')] ,  #Error Tolerance text box so it can be changed as per specs of user
               [sg.Submit(), sg.Cancel()]]                                         #Buttons to submit/cancel
    window = sg.Window('Ladder Iterative Load Flow Calculator', layout)            #GUI heading
        
    while True:
        event, values = window.read()
        if((event =='Cancel') or (values['tol'] == None)):
            quit()                                                           # to be used to extract data by data parser.
        return event, values[0], float(values['tol'])       #Stored values of the excel file address and error tolerance
    window.close()