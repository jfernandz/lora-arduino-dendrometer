import requests
import tkinter as tk
import json


def use_api(url, method=requests.get, header=None, body=None):
    body = json.dumps(body) if body else None

    response = method(url, headers=header, data=body)
    print(url, method, response.status_code, response.text)

    return response


# These are customizable patterns, actually
fiware_service = 'atosioe'
fiware_servicepath = '/lorattn'

# These are application unique
TTN_app_id = 'dendrometer'
TTN_app_pw = 'ttn-account-v2.173lH8wwDiIRC8E2JgM9ScXyuNRlPpMefpazS0TIhnU'
TTN_app_eui = '70B3D57ED0030B5D'

# These are device unique
TTN_app_skey = '7AF6B9A29EAF893F66C0F4360BA8DD5B'
TTN_dev_eui = '00EC51D264A6F8FD'

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


class Application(tk.Frame):
    entities = list()
    default_entity = 'LORA-N-0'

    devices = list()
    default_device = 'node_0'

    subscriptions = list()

    def __init__(self):
        self.gui = tk.Tk()
        self.gui.title('Fiware Client')
        super().__init__(self.gui)
        self.gui.geometry("640x480")
        self.pack()
        main_frame = tk.Frame(self.gui)
        main_frame.pack(fill=tk.BOTH, expand=tk.YES)

        self.label_orion_ver = tk.Label(main_frame, text='Orion version: ' + use_api('http://localhost:1026/version')
                                        .json()['orion']['version'])
        self.label_iot_ver = tk.Label(main_frame, text='IoT version: ' + use_api('http://localhost:4061/iot/about')
                                      .json()['libVersion'])
        self.label_quantumleap_ver = tk.Label(main_frame,
                                              text='QuantumLeap version: ' +
                                                   use_api('http://localhost:8668/v2/version').json()['version'])

        self.label_orion_ver.place(x=10, y=10)
        self.label_iot_ver.place(x=10, y=30)
        self.label_quantumleap_ver.place(x=10, y=50)

        self.listbox_devices = tk.Listbox(main_frame, height=5, width=20)
        self.listbox_devices.place(x=200, y=90)

        self.create_device = tk.Button(main_frame, text='Create device and entity',
                                       command=self.api_create_device_and_entity)
        self.delete_device = tk.Button(main_frame, text='Delete device and entities',
                                       command=self.api_delete_device_and_entity)
        self.create_device.place(x=10, y=90)
        self.delete_device.place(x=10, y=140)

        self.label_title_devices = tk.Label(main_frame, text='DEVICES')
        self.label_title_entities = tk.Label(main_frame, text='ENTITIES')
        self.label_title_subscriptions = tk.Label(main_frame, text='SUBSCRIPTIONS')

        self.label_devices = tk.Label(main_frame)
        self.label_entities = tk.Label(main_frame)
        self.label_subscriptions = tk.Label(main_frame)

        self.label_title_devices.place(x=10, y=190)
        self.label_title_entities.place(x=100, y=190)
        self.label_title_subscriptions.place(x=190, y=190)

        self.label_devices.place(x=10, y=210)
        self.label_entities.place(x=100, y=210)
        self.label_subscriptions.place(x=190, y=210)

        self.api_get_devices_and_entities()

    def api_get_devices_and_entities(self):
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

    def api_create_device_and_entity(self):
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

    def api_delete_device_and_entity(self):
        device = self.listbox_devices.get(tk.ACTIVE)
        if device:
            index = Application.devices.index(device)
            entity = Application.entities[index]
            subscription = Application.subscriptions[index]

            use_api(f'http://localhost:1026/v2/entities/{entity}', requests.delete,
                    header={"fiware-service": f"{fiware_service}", "fiware-servicepath": f"{fiware_servicepath}"})
            use_api(f'http://localhost:4061/iot/devices/{device}', method=requests.delete, header=header_iot_device)
            use_api(f'http://localhost:1026/v2/subscriptions/{subscription}', method=requests.delete,
                    header=header_orion)
        self.api_get_devices_and_entities()

    @staticmethod
    def get_iot_body():
        if len(Application.devices) == 0:
            device = Application.default_device
        else:
            last_device = Application.devices[-1]
            last_id = int(last_device.split('_')[-1])
            device = last_device.split('_')[0] + '_' + str(last_id + 1)

        if len(Application.entities) == 0:
            entity = Application.default_entity
        else:
            last_entity = Application.entities[-1]
            last_id = int(last_entity.split('-')[-1])
            entity = '-'.join(last_entity.split('-')[:-1]) + '-' + str(last_id + 1)

        return {
            "devices": [
                {
                    "device_id": f"{device}",
                    "entity_name": f"{entity}",
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
                                "username": f"{TTN_app_id}",
                                "password": f"{TTN_app_pw}",
                                "provider": f"TTN"
                            },
                            "dev_eui": f"{TTN_dev_eui}",
                            "app_eui": f"{TTN_app_eui}",
                            "application_id": f"{TTN_app_id}",
                            "application_key": f"{TTN_app_skey}"
                        }
                    }
                }
            ]
        }


Application().mainloop()
