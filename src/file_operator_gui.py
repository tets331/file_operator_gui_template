import os
import re

import PySimpleGUI as sg

class FileOperatorGui(object):
    def __init__(self):
        self.allfiles = []
        self.filters = {'value':'', 'case':False}
        self.exfilters = {'value':'', 'case':False}

    def main_window(self, title):
        layout = [[sg.Text('Folder'), sg.InputText(key='-SELECTED-FOLDER-', enable_events=True), sg.FolderBrowse()],
                  [sg.Text('Please select target folder', key='-FOLDER-SELECT-MSG-')],
                  [sg.Button('Next', key='-NEXT-BUTTON-')]
                  ]
        window = sg.Window(title, layout)

        while True:
            event, values = window.read()
            
            if event == sg.WINDOW_CLOSED:
                break
            elif event == '-SELECTED-FOLDER-':
                if not os.path.exists(values['-SELECTED-FOLDER-']):
                    window['-FOLDER-SELECT-MSG-'].update('Folder is NOT exist!!')
                else:
                    window['-FOLDER-SELECT-MSG-'].update('Click Next')
            elif event == '-NEXT-BUTTON-':
                if os.path.exists(values['-SELECTED-FOLDER-']):
                    self.file_select_window(values['-SELECTED-FOLDER-'])

        window.close()

    def file_select_window(self, selected_folder, title='File Select'):

        for cur, d, files in os.walk(selected_folder):
            self.allfiles = self.allfiles + [os.path.join(cur,x) for x in files]
    
        window = self._open_file_select_window(title)

        while True:
            event, values = window.read()

            if event == sg.WINDOW_CLOSED or event == '-CLOSE-':
                break

            self.filters['value'] = values['-FILTER-']
            self.filters['case'] = values['-FILTERCASE-']
            self.exfilters['value'] = values['-EXFILTER-']
            self.exfilters['case'] = values['-EXFILTERCASE-']

            if event == '-CHECK-ALL-':
                for f in self._filtered_files():
                    window[f].update(True)
            elif event == '-UNCHECK-ALL-':
                for f in self._filtered_files():
                    window[f].update(False)
            elif event == '-APPLY-FILTER-':
                window.close()
                window = self._open_file_select_window(title)
            elif event == '-RUN-':
                v = {}
                v['all files'] = self.allfiles
                v['filtered files'] = self._filtered_files()
                v['selected files'] = [x for x in self._filtered_files() if values[x]]
                self.run_command(v)

        self._finish_file_select_window(window)

    def _open_file_select_window(self, title, size=(600, 600)):
        checkboxes = [[sg.Checkbox(x, key=x)] for x in self._filtered_files()]
        filter_frame = sg.Frame('Filter', [
            [sg.Text('File path contains'), sg.InputText(key='-FILTER-', default_text = self.filters['value']), sg.Checkbox('Case', key='-FILTERCASE-', default=self.filters['case'])],
            [sg.Text('File path does NOT contains'), sg.InputText(key='-EXFILTER-', default_text = self.exfilters['value']), sg.Checkbox('Case', key='-EXFILTERCASE-', default=self.exfilters['case'])],
            [sg.Button('Apply', key='-APPLY-FILTER-')],

        ])
        layout = [[sg.Button('Check all', key='-CHECK-ALL-'), sg.Button('Uncheck all', key='-UNCHECK-ALL-')],
                  [filter_frame],
                  [sg.Column(checkboxes, scrollable=True, size=size)],
                  [sg.Button('Run', key='-RUN-'), sg.Button('Close', key='-CLOSE-')]
                  ]
        
        window = sg.Window(title, layout)
        return window

    def _finish_file_select_window(self, window):
        self.allfiles = []
        self.filters = {'value':'', 'case':False}
        self.exfilters = {'value':'', 'case':False}
        window.close()
       
    def _filtered_files(self):
        filtered_files = self.allfiles
        if self.filters['value']:
            flags = re.IGNORECASE if self.filters['case'] == False else 0
            for fltr in self.filters['value'].split():
                filtered_files =  [x for x in filtered_files if re.search(fltr, x, flags=flags)]

        if self.exfilters['value']:
            flags = re.IGNORECASE if self.exfilters['case'] == False else 0
            for fltr in self.exfilters['value'].split():
                filtered_files =  [x for x in filtered_files if not re.search(fltr, x, flags=flags)]

        return filtered_files
        
    def run_command(self, values):
        raise NotImplementedError
        
