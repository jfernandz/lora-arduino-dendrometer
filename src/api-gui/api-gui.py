#!/usr/bin/python

import requests
import tkinter as tk
from tkinter import ttk
from string import hexdigits
import json

# These are customizable patterns, actually
fiware_service = 'atosioe'
fiware_servicepath = '/lorattn'

header_iot_device = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "fiware-service": f"{fiware_service}",
    "fiware-servicepath": f"{fiware_servicepath}"
}

header_orion = {
    "fiware-service": f"{fiware_service}",
    "fiware-servicepath": f"{fiware_servicepath}"
}


def use_api(url, method=requests.get, header=None, body=None):
    """
    Generic function to attack the FIWARE API
    :param url:
    :param method:
    :param header:
    :param body:
    :return:
    """
    body = json.dumps(body) if body else None

    response = method(url, headers=header, data=body)
    # print(url, method, response.status_code, response.text)

    return response


def is_hex(string) -> bool:
    """
    Function to check whether a string is hexadecimal
    :param string:
    :return:
    """
    return all([char in hexdigits for char in string])


class Application(tk.Frame):

    devices = entities = list()
    default_device = default_entity = 'node_0'

    subscriptions = list()

    # These are application unique
    TTN_app_id = None
    TTN_app_pw = None
    TTN_app_eui = None

    # These are device unique
    TTN_app_skey = None
    TTN_dev_eui = None

    def __init__(self):
        # TKINTER constructor
        self.gui = tk.Tk()
        self.gui.title('Fiware Client')
        super().__init__(self.gui)
        self.gui.minsize(640, 480)
        # self.gui.geometry("640x480")
        self.pack()

        # Tabs
        self.notebook = ttk.Notebook(self.gui)  # Tab controller
        self.tab_app_keys = ttk.Frame(self.notebook)
        self.tab_devices_management = ttk.Frame(self.notebook)
        self.tab_about = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_app_keys, text='Applications Keys')
        self.notebook.add(self.tab_devices_management, text='Devices Management')
        self.notebook.add(self.tab_about, text='About')
        self.notebook.tab(1, state='disabled')  # disabled by default until the app data is introduced
        self.notebook.pack(expand=1, fill="both")

        # Labels
        self.label_dev_ent_id = None
        self.label_ttn_app_id = None
        self.label_ttn_app_pw = None
        self.label_ttn_app_eui = None
        self.label_app_skey = None
        self.label_dev_eui = None
        self.label_title_devices = None
        self.label_title_entities = None
        self.label_title_subscriptions = None
        self.label_devices = None
        self.label_entities = None
        self.label_subscriptions = None
        self.label_orion_ver = None
        self.label_iot_ver = None
        self.label_quantumleap_ver = None

        # Inputs
        self.entry_dev_ent_id = None
        self.entry_ttn_app_id = None
        self.entry_ttn_app_pw = None
        self.entry_ttn_app_eui = None
        self.entry_app_skey = None
        self.entry_dev_eui = None

        # Buttons
        self.set_app_keys = None
        self.button_create_device = None
        self.button_delete_device = None

        # Listbox
        self.listbox_devices = None

        # Widgets
        self.set_devices_management_widgets()
        self.set_about_widgets()
        self.set_applications_keys_widgets()

        # Initial get request
        self.api_get_devices_and_entities()

    def set_about_widgets(self) -> None:
        """
        Sets up the About tab where versions are shown
        :return:
        """
        self.label_orion_ver = tk.Label(self.tab_about,
                                        text='Orion version: ' + use_api('http://localhost:1026/version')
                                        .json()['orion']['version'])
        self.label_iot_ver = tk.Label(self.tab_about, text='IoT version: ' + use_api('http://localhost:4061/iot/about')
                                      .json()['libVersion'])
        self.label_quantumleap_ver = tk.Label(self.tab_about,
                                              text='QuantumLeap version: ' +
                                                   use_api('http://localhost:8668/v2/version').json()['version'])
        self.label_orion_ver.place(x=10, y=10)
        self.label_iot_ver.place(x=10, y=30)
        self.label_quantumleap_ver.place(x=10, y=50)

    def set_applications_keys_widgets(self) -> None:
        """
        Set labals, entries and buttons for application keys tab
        :return:
        """
        # Labels
        self.label_ttn_app_id = tk.Label(self.tab_app_keys, text='TTN Application ID')
        self.label_ttn_app_pw = tk.Label(self.tab_app_keys, text='TTN Application Access Key')
        self.label_ttn_app_eui = tk.Label(self.tab_app_keys, text='TTN Application EUI')
        self.label_ttn_app_id.place(x=10, y=10)
        self.label_ttn_app_pw.place(x=10, y=50)
        self.label_ttn_app_eui.place(x=10, y=90)

        # Entries
        self.entry_ttn_app_id = tk.Entry(self.tab_app_keys)
        self.entry_ttn_app_pw = tk.Entry(self.tab_app_keys, width=60)
        self.entry_ttn_app_eui = tk.Entry(self.tab_app_keys, width=17)
        self.entry_ttn_app_id.place(x=10, y=30)
        self.entry_ttn_app_pw.place(x=10, y=70)
        self.entry_ttn_app_eui.place(x=10, y=110)

        # Button
        self.set_app_keys = tk.Button(self.tab_app_keys, text='Update Keys', command=self.update_app_keys)
        self.set_app_keys.place(x=10, y=150)

    def set_devices_management_widgets(self) -> None:
        """
        Sets and places the widgets that are needed to manage devices
        :return: None
        """
        # Listbox
        self.listbox_devices = tk.Listbox(self.tab_devices_management, height=10, width=20)
        self.listbox_devices.place(x=460, y=30)
        self.listbox_devices.bind('<<ListboxSelect>>', self.enable_delete_button)

        # Buttons
        self.button_create_device = tk.Button(self.tab_devices_management, text='Create device and entity',
                                              command=self.api_create_device_and_entity)
        self.button_delete_device = tk.Button(self.tab_devices_management, text='Delete device and entities',
                                              command=self.api_delete_device_and_entity, state='disabled')
        self.button_create_device.place(x=10, y=150)
        self.button_delete_device.place(x=10, y=200)

        # Labels
        self.label_dev_ent_id = tk.Label(self.tab_devices_management, text='Device and entity ID')
        self.label_app_skey = tk.Label(self.tab_devices_management, text='Application Session Key')
        self.label_dev_eui = tk.Label(self.tab_devices_management, text='Device EUI')
        self.label_title_devices = tk.Label(self.tab_devices_management, text='DEVICES')
        self.label_title_entities = tk.Label(self.tab_devices_management, text='ENTITIES')
        self.label_title_subscriptions = tk.Label(self.tab_devices_management, text='SUBSCRIPTIONS')
        self.label_devices = tk.Label(self.tab_devices_management)
        self.label_entities = tk.Label(self.tab_devices_management)
        self.label_subscriptions = tk.Label(self.tab_devices_management)

        self.label_dev_ent_id.place(x=10, y=10)
        self.label_app_skey.place(x=10, y=50)
        self.label_dev_eui.place(x=10, y=90)
        self.label_title_devices.place(x=10, y=250)
        self.label_title_entities.place(x=100, y=250)
        self.label_title_subscriptions.place(x=190, y=250)
        self.label_devices.place(x=10, y=270)
        self.label_entities.place(x=100, y=270)
        self.label_subscriptions.place(x=190, y=270)

        # Inputs
        self.entry_dev_ent_id = tk.Entry(self.tab_devices_management)
        self.entry_app_skey = tk.Entry(self.tab_devices_management, width=33)
        self.entry_dev_eui = tk.Entry(self.tab_devices_management, width=17)
        self.entry_dev_ent_id.place(x=10, y=30)
        self.entry_app_skey.place(x=10, y=70)
        self.entry_dev_eui.place(x=10, y=110)

    def enable_delete_button(self, event) -> None:
        """
        Enables delete buton when any element is chosen in the Listbox
        :param event:
        :return:
        """
        self.button_delete_device.config(state="normal")

    def update_app_keys(self) -> None:
        """
        Sets up the labels colors when there is not valid a key, stores these inside variables and enables
        Devices management key
        :return:
        """
        # get the values
        app_id = self.entry_ttn_app_id.get()
        app_pw = self.entry_ttn_app_pw.get()
        app_eui = self.entry_ttn_app_eui.get().upper()

        error = False
        if len(app_id) < 3:
            self.label_ttn_app_id.config(fg='red')
            error = True
        else:
            # Update the labels
            self.label_ttn_app_id['text'] = self.label_ttn_app_id['text'].split('  ->  ')[0] + '  ->  ' + app_id
            self.label_ttn_app_id.config(fg='black')
        if not app_pw.startswith('ttn-account'):
            self.label_ttn_app_pw.config(fg='red')
            error = True
        else:
            # Update the label
            self.label_ttn_app_pw['text'] = self.label_ttn_app_pw['text'].split('  ->  ')[0] + '  ->  ' + app_pw
            self.label_ttn_app_pw.config(fg='black')
        if len(app_eui) != 16 or not is_hex(app_eui):
            self.label_ttn_app_eui.config(fg='red')
            error = True
        else:
            # Update the label
            self.label_ttn_app_eui['text'] = self.label_ttn_app_eui['text'].split('  ->  ')[0] + '  ->  ' + app_eui
            self.label_ttn_app_eui.config(fg='black')

        if error:
            self.notebook.tab(1, state='disabled')
            return

        # Update the vars
        Application.TTN_app_id = app_id
        Application.TTN_app_pw = app_pw
        Application.TTN_app_eui = app_eui

        self.notebook.tab(1, state='normal')

    def api_get_devices_and_entities(self) -> None:
        """
        Uses diverse APIs to retrieve data and update the application
        :return: None
        """
        entities = use_api('http://localhost:1026/v2/entities', header=header_orion).json()
        devices = use_api('http://localhost:4061/iot/devices', header=header_iot_device).json()['devices']
        subscriptions = use_api('http://localhost:1026/v2/subscriptions', header=header_orion).json()

        Application.entities = list()
        Application.devices = list()
        Application.subscriptions = list()

        self.listbox_devices.delete(0, tk.END)
        self.label_devices['text'] = ''
        self.label_entities['text'] = ''

        for entity in entities:
            Application.entities.append(entity['id'])
        for device in devices:
            Application.devices.append(device['device_id'])
            self.listbox_devices.insert(tk.END, device['device_id'])

        for subscription in subscriptions:
            Application.subscriptions.append(subscription['id'])

        self.label_devices['text'] = '\n'.join(Application.devices)
        self.label_entities['text'] = '\n'.join(Application.entities)
        self.label_subscriptions['text'] = '\n'.join(Application.subscriptions)

    def api_create_device_and_entity(self) -> None:
        """
        Validates that the device keys are intruduceded and attacks the iot API to create a device, and then creates
        a subscription to that device
        :return:
        """
        dev_ent_id = self.entry_dev_ent_id.get()
        app_skey = self.entry_app_skey.get()
        dev_eui = self.entry_dev_eui.get()

        error = False
        if len(dev_ent_id) < 3:
            self.label_dev_ent_id.config(fg='red')
            error = True
        else:
            # Update label device entity ID
            self.label_dev_ent_id['text'] = self.label_dev_ent_id['text'].split('  ->  ')[0] + '  ->  ' + dev_ent_id
            self.label_dev_ent_id.config(fg='black')
        if len(app_skey) != 32 or not is_hex(app_skey):
            self.label_app_skey.config(fg='red')
            error = True
        else:
            # update the label
            self.label_app_skey['text'] = self.label_app_skey['text'].split('  ->  ')[0] + '  ->  ' + app_skey
            self.label_app_skey.config(fg='black')
        if len(dev_eui) != 16 or not is_hex(dev_eui):
            self.label_dev_eui.config(fg='red')
            error = True
        else:
            # Update the label
            self.label_dev_eui['text'] = self.label_dev_eui['text'].split('  ->  ')[0] + '  ->  ' + dev_eui
            self.label_dev_eui.config(fg='black')

        if error:
            return
        # Update the vars
        Application.devices = Application.entities = dev_ent_id
        Application.TTN_app_skey = app_skey
        Application.TTN_dev_eui = dev_eui

        # creates the device and entity
        use_api('http://localhost:4061/iot/devices', method=requests.post, header=header_iot_device,
                body=Application.get_iot_body())
        self.api_get_devices_and_entities()

        # creates the subscription
        entity = Application.entities[-1]
        body = {
            "description": f"A subscription to get info about {entity}",
            "subject": {
                "entities": [
                    {
                        "id": f"{entity}",
                        "type": "LoraDevice"
                    }
                ],
                "condition": {
                    "attrs": [
                        "analog_in_1"
                    ]
                }
            },
            "notification": {
                "http": {
                    "url": "http://quantumleap:8668/v2/notify"
                },
                "attrs": [
                    "analog_in_1"
                ],
                "metadata": ["dateCreated", "dateModified"]
            },
            "throttling": 5
        }
        use_api('http://localhost:1026/v2/subscriptions', method=requests.post, header=header_iot_device, body=body)
        self.api_get_devices_and_entities()

    def api_delete_device_and_entity(self) -> None:
        """
        Deletes the chosen devices in Listbox
        :return:
        """
        device = self.listbox_devices.get(tk.ACTIVE)
        if device:
            index = Application.devices.index(device)
            entity = Application.entities[index]
            subscription = Application.subscriptions[index]

            use_api(f'http://localhost:1026/v2/entities/{entity}', method=requests.delete,
                    header={"fiware-service": f"{fiware_service}", "fiware-servicepath": f"{fiware_servicepath}"})
            use_api(f'http://localhost:4061/iot/devices/{device}', method=requests.delete, header=header_iot_device)
            use_api(f'http://localhost:1026/v2/subscriptions/{subscription}', method=requests.delete,
                    header=header_orion)
        self.button_delete_device.config(state='disabled')
        self.api_get_devices_and_entities()

    @staticmethod
    def get_iot_body():
        """
        It composes the body as a payload to send in creation device and entity process
        Be careful!! This body is not used to create the subscription, the body to create
        the subscription is declared in the api_create_device_and_entity() function because
        it's simpler.
        :return:
        """

        if len(Application.devices) == 0:
            device = Application.default_device
        else:
            device = Application.devices

        return {
            "devices": [
                {
                    "device_id": f"{device}",
                    "entity_name": f"{device}",
                    "entity_type": "LoraDevice",
                    "timezone": "Europe/Madrid",
                    "attributes": [
                        {
                            "object_id": "analog_in_1",
                            "name": "analog_in_1",
                            "type": "Number"
                        }
                    ],
                    "internal_attributes": {
                        "lorawan": {
                            "application_server": {
                                "host": "eu.thethings.network",
                                "username": f"{Application.TTN_app_id}",
                                "password": f"{Application.TTN_app_pw}",
                                "provider": f"TTN"
                            },
                            "dev_eui": f"{Application.TTN_dev_eui}",
                            "app_eui": f"{Application.TTN_app_eui}",
                            "application_id": f"{Application.TTN_app_id}",
                            "application_key": f"{Application.TTN_app_skey}"
                        }
                    }
                }
            ]
        }


Application().mainloop()
