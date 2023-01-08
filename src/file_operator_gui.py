import datetime
import os
import re

import PySimpleGUI as sg

class FileOperatorGui(object):
    def __init__(self, custom_parameters=[]):
        self.custom_parameters = custom_parameters

    def folder_select_window(self, title='Folder Select'):
        layout = [[sg.Text('Folder'), sg.InputText(key='-SELECTED-FOLDER-', enable_events=True), sg.FolderBrowse()],
                  [sg.Text('Please select target folder', key='-FOLDER-SELECT-MSG-')]
                  ]

        for cp in self.custom_parameters:
            if cp['type'] == 'combo':
                cps = [sg.Text('{}: '.format(cp['name'])), sg.Combo(cp['values'], key = cp['name'])]
            elif cp['type'] == 'text':
                cps = [sg.Text('{}: '.format(cp['name'])), sg.InputText(key = cp['name'])]
            elif cp['type'] == 'checkbox':
                cps = [sg.Text('{}: '.format(cp['name'])), sg.Checkbox('', key = cp['name'])]
            else:
                raise ValueError('Undefined type is used as custom parameters')

            layout.append(cps)

        layout.append([sg.Button('Next', key='-NEXT-BUTTON-')])
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
                    self.file_select_window(values['-SELECTED-FOLDER-'], [{x['name']:values[x['name']]} for x in self.custom_parameters])

        window.close()

    def file_select_window(self, selected_folder, custom_parameters=[], title='File Select'):
        s_window = _SelectWindowClass(title, selected_folder, custom_parameters, self.custom_filter, self.run_command)
        s_window.open_new_window()

        while True:
            if s_window.event_handler() == 'Finish':
                break
        s_window.close()

    def custom_filter(self, filename):
        return True

    def run_command(self, values):
        raise NotImplementedError

class _SelectWindowClass(object):
    PROGRESS_BAR_MAX = 1000

    def __init__(self, title, selected_folder, custom_parameters, custom_condition, run_command):
        self.title = title
        self.selected_folder = '{}/'.format(selected_folder)
        self.custom_parameters = custom_parameters
        self.window = None
        self.allfiles = []
        for cur, d, files in os.walk(self.selected_folder):
            self.allfiles = self.allfiles + [os.path.join(cur,x) for x in files]
        self.allfiles.sort()
        self.filters = {'value':'', 'case':False}
        self.exfilters = {'value':'', 'case':False}
        self.custom_condition = custom_condition
        self.run_command = run_command

    def open_new_window(self, size=(600, 600)):
        checkboxes = [[sg.Checkbox(x.replace(self.selected_folder,''), key=x)] for x in self._filtered_files()]
        filter_frame = sg.Frame('Filter (white space delimiter)', [
            [sg.Text('File path contains'), sg.InputText(key='-FILTER-', default_text = self.filters['value']), sg.Checkbox('Case', key='-FILTERCASE-', default=self.filters['case'])],
            [sg.Text('File path does NOT contains'), sg.InputText(key='-EXFILTER-', default_text = self.exfilters['value']), sg.Checkbox('Case', key='-EXFILTERCASE-', default=self.exfilters['case'])],
            [sg.Button('Apply', key='-APPLY-FILTER-')],

        ])
        layout = [[sg.Button('Check all', key='-CHECK-ALL-'), sg.Button('Uncheck all', key='-UNCHECK-ALL-')],
                  [filter_frame],
                  [sg.Text('Folder Path:{}'.format(self.selected_folder))],
                  [sg.Column(checkboxes, scrollable=True, size=size)],
                  [sg.Button('Run', key='-RUN-'), sg.Text('', key='-MESSAGE-')]
                  ]
        
        self.window = sg.Window(self.title, layout)

    def event_handler(self):
        event, values = self.window.read()

        if event == sg.WINDOW_CLOSED:
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
            selected_files = [x for x in self._filtered_files() if values[x]]
            if selected_files:
                self.window['-MESSAGE-'].update('Running...', text_color='#000000')
                self._run(selected_files)
                self.window['-MESSAGE-'].update('', text_color='#000000')
            else:
                self.window['-MESSAGE-'].update('No file selected!!', text_color='#FFBBFF')

        return 'Continue'

    def _run(self, selected_files, title='Progress Window'):
        layout = [
            [sg.Text('Start', key='-STRTEXT-')],
            [sg.Text('End', key='-ENDTEXT-')],
            [sg.Text('Progress', key='-PRGTEXT-')],
            [sg.Text('File: ', key='-FILETEXT-')],
            [sg.ProgressBar(max_value = self.PROGRESS_BAR_MAX, key='-PROG-')],
            [sg.Button('STOP', key='-BUTTON-')]
        ]
        p_window =  sg.Window(title, layout)
        pe, pv = p_window.read(timeout=1)
        start_time = datetime.datetime.now()
        p_window['-STRTEXT-'].update('Start {}'.format(start_time.time().strftime('%X')))
        
        v = {}
        v['selected files'] = selected_files
        v['custom parameters'] = self.custom_parameters
        sfl = len(v['selected files'])

        for i, f in enumerate(v['selected files'], start=1):
            v['current file'] = f
            v['is last?'] = f is selected_files[-1]

            p_window['-FILETEXT-'].update(f)
            p_window['-PROG-'].update(i/sfl * self.PROGRESS_BAR_MAX)
            p_window['-PRGTEXT-'].update('Progress:{}/{} ({})%'.format(i, sfl, round((i/sfl)*100)))
            p_window['-ENDTEXT-'].update('will End {}'.format((start_time + (datetime.datetime.now() - start_time)/i*sfl).time().strftime('%X')))
            p_window.bring_to_front()

            self.run_command(v)

            pe, pv = p_window.read(timeout=10)

            if pe == sg.WINDOW_CLOSED:
                break
            elif pe == '-BUTTON-':
                stop_stime = datetime.datetime.now()
                p_window['-PRGTEXT-'].update('Stopped ({}/{})'.format(i, sfl))
                p_window['-BUTTON-'].update('Restart')
                pe, pv = p_window.read() # wait for any event (e.g. click close buttton)
                if pe == '-BUTTON-':
                    start_time += datetime.datetime.now() - stop_stime
                    continue
                elif pe == sg.WINDOW_CLOSED:
                    break
            elif v['is last?']:
                end_time = datetime.datetime.now()
                p_window['-ENDTEXT-'].update('End {} ({}s)'.format(end_time.time().strftime('%X'), (end_time - start_time).total_seconds()))
                p_window['-PRGTEXT-'].update('Completed {} files'.format(sfl))
                p_window['-BUTTON-'].update('CLOSE')
                p_window.read() # wait for any event (e.g. click close buttton)
                break

        p_window.close()

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

        filtered_files = [x for x in filtered_files if self.custom_condition(x)]
            
        return filtered_files
