# Local module
from src import file_operator_gui as fo_gui

class MyFolderSelectGui(fo_gui.FileOperatorGui):
    def run_command(self, values):
        # This function is invoked, when you push Run button.
        # You can implement anything from here 
        for filepath in values['selected files']:
            print(filepath)

if __name__ == '__main__':
    my_gui = MyFolderSelectGui()
    my_gui.folder_select_window()
