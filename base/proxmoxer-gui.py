import urllib3
import PySimpleGUI as sg
from proxmoxer import ProxmoxAPI

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)     # Unterdrückt Warnung für nicht überprüftes HTTPS-Zertifikat
sg.theme('DarkGrey14')

# Behandlung im Fenster
def show_error(exception):
    sg.Popup(f'An error occurred. \nError: {exception}', title='Error')

# Auslesen von Daten
def get_container_information():
    global lxc_inventory 
    lxc_inventory = {}      # Hinzugefügte oder gelöschte Einträge werden so mitbretrachtet
    for lxc in (prox.nodes(node_name).lxc.get()):
        lxc_inventory[str(lxc['vmid'])] = lxc['name'], lxc['status']
def get_vm_information():
    global vm_inventory
    vm_inventory = {}
    for vm in (prox.nodes(node_name).qemu.get()):
        vm_inventory[str(vm['vmid'])] = vm['name'], vm['status']

# Anzeigeaufbereitung
def inventory_to_rows(type):
    if type == 'lxc':
        get_container_information()
        sorted_inventory = dict(sorted(lxc_inventory.items()))
    if type == 'vm':
        get_vm_information()
        sorted_inventory = dict(sorted(vm_inventory.items()))    
    rows = []       # Verhindern von doppelten Einträgen
    for key, value in sorted_inventory.items():
        row = ['', '', ''] 
        row[0] = key
        row[1] = value[0]
        row[2] = value[1]
        rows.append(row)
    return rows

# Administrative Tätigkeiten
def perform_operation(id, inventory, operation_function):
    if id not in inventory:
        sg.Popup('The id is not valid for that operation', title='No valid id')
    else: 
        operation_function(id)
def start_lxc(id):
    try:
        prox.nodes(node_name).lxc(id).status('start').post()
    except Exception as e:
        show_error(e)
def shutdown_lxc(id):
    try:
        prox.nodes(node_name).lxc(id).status('shutdown').post()
    except Exception as e:
        show_error(e)
def stop_lxc(id):
    try:
        prox.nodes(node_name).lxc(id).status('stop').post()
    except Exception as e:
        show_error(e)
def start_vm(id):
    try:
        prox.nodes(node_name).qemu(id).status('start').post()
    except Exception as e:
        show_error(e)
def shutdown_vm(id):
    try:
        prox.nodes(node_name).qemu(id).status('shutdown').post()
    except Exception as e:
        show_error(e)
def stop_vm(id):
    try:
        prox.nodes(node_name).qemu(id).status('stop').post()
    except Exception as e:
        show_error(e)

# Grafische Oberfläche
def login_window():
    global prox, node_name, node_ip, node_user, node_token_id, node_token_value 
    layout = [  [sg.Text('Node name:', size=22), sg.InputText(key='-NAME-',justification='r')],
                [sg.Text('IP-Address:', size=22), sg.InputText(key='-IP-', justification='r')],
                [sg.Text('User@Realm:', size=22), sg.InputText(key='-USER-', justification='r')],
                [sg.Text('Token-ID:', size=22), sg.InputText(key='-TID-', justification='r')],
                [sg.Text('Token-Value:', size=22), sg.InputText(key='-TVAL-', justification='r')],
                [sg.Button('Apply', size = 10, bind_return_key = True), sg.Button('Exit', size=10)]   ]
    window = sg.Window('Login', layout)
    while True:
        event, values = window.read()        
        if event in (sg.WINDOW_CLOSED, 'Exit'):
            break
        if event == 'Apply':    
            node_name = values['-NAME-']
            node_ip = values['-IP-']
            node_user = values['-USER-']
            node_token_id = values['-TID-']
            node_token_value = values['-TVAL-']
            try:
                prox = ProxmoxAPI(node_ip, user=node_user, token_name=node_token_id, token_value=node_token_value, verify_ssl=False)
                prox.nodes(node_name).version.get()     # Dummy-Abfrage, um auf korrekte Verbindung zu prüfen
                window.close()
            except Exception as e:
                sg.popup(f'Connection not established. Check input. \nError: {e}', title='Error')
                continue
            main_window()
    window.close()

def admin_window():
    layout = [  [sg.T('Start or Shutdown'), sg.R('Start', 'changeStatus', key='-START-', default=True), sg.R('Shutdown', 'changeStatus', key='-SHUTDOWN-'), sg.R('Stop', 'changeStatus', key='-STOP-')],
                [sg.T('LXC or VM'), sg.R('LXC', 'type', key='-LXC-', default=True), sg.R('VM', 'type', key='-VM-')],
                [sg.T('ID'), sg.InputText(size=3, key='-ID-')],
                [sg.T('Hint: It takes a moment until the start or shutdown is visible.\nPlease wait briefly before clicking on the refresh-button.\nYou must close this window to be able to refresh.')],
                [sg.Button('Apply', bind_return_key=True), sg.Button('Cancel')]  ]

    window = sg.Window('Poweroptions', layout)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Cancel'):
            break
        if event == 'Apply':
            id = values['-ID-']
            if (values['-START-']):
                if (values['-LXC-']):
                    perform_operation(id, lxc_inventory, start_lxc)
                if (values['-VM-']):
                    perform_operation(id, vm_inventory, start_vm)
            if (values['-SHUTDOWN-']):
                if (values['-LXC-']):
                    perform_operation(id, lxc_inventory, shutdown_lxc)
                if (values['-VM-']):
                    perform_operation(id, vm_inventory, shutdown_vm)
            if (values['-STOP-']):
                if (values['-LXC-']):
                    perform_operation(id, lxc_inventory, stop_lxc)
                if (values['-VM-']):
                    perform_operation(id, vm_inventory, stop_vm)
    window.close()

def main_window():
    heading = ['ID', 'Name', 'Status']
    lxc_rows = inventory_to_rows('lxc')
    lxc_table = sg.Table(values=lxc_rows,
                         headings=heading,
                         auto_size_columns=False,
                         col_widths=[5, 20 ,10],
                         num_rows=20,
                         justification='center',
                         selected_row_colors='black on white')
    vm_rows = inventory_to_rows('vm')
    vm_table = sg.Table(values=vm_rows, 
                        headings=heading,
                        auto_size_columns=False,
                        col_widths=[5, 20 ,10],
                        num_rows=20,
                        justification='center',
                        selected_row_colors='black on white')
    
    left_panel = sg.Column([[sg.Text('Linux Container:')],
                            [lxc_table]])
    right_panel = sg.Column([[sg.Text('Virtual Machines:')],
                             [vm_table]])
    bottom_panel = [[sg.Button('Refresh', tooltip='Refreshes both tables'),sg.Button('Start/Stop'), sg.Button('Exit')]]
    
    layout = [  [left_panel, right_panel],
                [bottom_panel]]
    
    window = sg.Window('Proxmox Status', layout)

    while True:
        event, values = window.read()
        if event in ('Exit', sg.WIN_CLOSED):
            break
        if event == 'Refresh':
            lxc_rows = inventory_to_rows('lxc')
            lxc_table.update(values=lxc_rows)
            vm_rows = inventory_to_rows('vm')
            vm_table.update(values=vm_rows)
        if event == 'Start/Stop':
            admin_window()
    window.close()

def main():
    login_window()

if __name__ == '__main__':
    main()
