import os
import re

import PySimpleGUI as sg

class FileOperatorGui(object):
    def __init__(self):
        pass

    def folder_select_window(self, title='Folder Select'):
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
        s_window = SelectWindowClass(title, selected_folder, self.run_command)
        s_window.open_new_window()

        while True:
            if s_window.event_handler() == 'Finish':
                break
        s_window.close()
        
    def run_command(self, values):
        raise NotImplementedError

class SelectWindowClass(object):
    def __init__(self, title, selected_folder, run_command):
        self.title = title
        self.window = None
        self.allfiles = []
        for cur, d, files in os.walk(selected_folder):
            self.allfiles = self.allfiles + [os.path.join(cur,x) for x in files]
        self.filters = {'value':'', 'case':False}
        self.exfilters = {'value':'', 'case':False}
        self.run_command = run_command

    def open_new_window(self, size=(600, 600)):
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
        
        self.window = sg.Window(self.title, layout)

    def event_handler(self):
        event, values = self.window.read()

        if event == sg.WINDOW_CLOSED or event == '-CLOSE-':
            return 'Finish'
        
        self.filters['value'] = values['-FILTER-']
        self.filters['case'] = values['-FILTERCASE-']
        self.exfilters['value'] = values['-EXFILTER-']
        self.exfilters['case'] = values['-EXFILTERCASE-']
        
        if event == '-CHECK-ALL-':
            for f in self._filtered_files():
                self.window[f].update(True)
        elif event == '-UNCHECK-ALL-':
            for f in self._filtered_files():
                self.window[f].update(False)
        elif event == '-APPLY-FILTER-':
            self._reflesh_window()
        elif event == '-RUN-':
            v = {}
            v['all files'] = self.allfiles
            v['filtered files'] = self._filtered_files()
            v['selected files'] = [x for x in self._filtered_files() if values[x]]
            self.run_command(v)

        return 'Continue'

    def close(self):
        self.window.close()

    def _reflesh_window(self):
        self.window.close()
        self.open_new_window()

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
