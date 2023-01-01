# Local module
from src import file_operator_gui as fo_gui

class MyFolderSelectGui(fo_gui.FileOperatorGui):
    def run_command(self, values):
        # This function is invoked, when you push Run button.
        # You can implement anything from here 
        print(values['custom parameters']) # hint: custom parameters is given like this.
        print(values['current file'])

if __name__ == '__main__':
    custom_parameters = [
        {'name':'sample2 param1', 'type': 'combo', 'values':['apple','banana','cherry']},
        {'name':'sample2 param2', 'type': 'text'},
        {'name':'sample2 param3', 'type': 'checkbox'},
    ]
    my_gui = MyFolderSelectGui(custom_parameters)
    my_gui.folder_select_window()
