# https://developercenter.robotstudio.com/api/RWS?urls.primaryName=RAPID%20Service

import json
import time
from pprint import pprint as pp
import logging
import requests
from requests.auth import HTTPBasicAuth
from ws4py.client.threadedclient import WebSocketClient
import xml.etree.ElementTree as ET
from ws4py.messaging import TextMessage
from models import Task, Module
import urllib3
from dacite import from_dict
urllib3.disable_warnings()


HOST = '127.0.0.1'
# Jacobi
USER = 'Admin'
# alt 'Default User'
PWD = 'robotics'

basic_auth = HTTPBasicAuth(USER, PWD)

FORMAT = '%(asctime)-15s - %(message)s'
logging.basicConfig(format=FORMAT,level=logging.DEBUG)
logger = logging.getLogger('ability_tool')


class RobWebSocketClient(WebSocketClient):
    def __init__(self, url, headers, api, on_message=None):
        super().__init__(url,protocols=['rws_subscription'], headers=headers)
        self.on_message: callable = on_message
        self.api: Robot = api
        self.namespace = '{http://www.w3.org/1999/xhtml}'
        self.variables = []

    def opened(self):
        logger.info('Opened Websocket')

    def closed(self, code, reason=None):
        self.api.logout()
        self.close_connection()
        logger.info('Closed Websocket')

    def received_message(self, message: TextMessage):
        if not message.is_text:
            print("Not text", message)
            return
        root = ET.fromstring(message.data.decode("utf-8"))
        # Find variable url in message
        if root.findall(".//{0}li[@class='rap-value-ev']".format(self.namespace)):
            url = root.find(".//{0}li[@class='rap-value-ev']/{0}a".format(self.namespace)).attrib['href']
            if not url:
                print("No url found in message")
                return
            resp, code = self.api.get_rapid_variable(url=url)
            value = resp['state'][0]['value']
            self.on_message(self.api, url, value)

    def start(self):
        try:
            self.connect()
            if self.on_message:
                # Get initial values for all variables when connection is established
                # and call on_message for each variable
                for variable in self.variables:
                    url = f"/rw/rapid/symbol/RAPID/{variable}/data"
                    value = self.api.get_rapid_variable(variable=variable)
                    self.on_message(self.api, url, value)
            self.run_forever()
        finally:
            self.close()

class Robot:
    def __init__(self, ip="152.94.0.228", user='Default User', pwd='robotics', port=443, proto='https://'):
        self.header = {'Accept':'application/hal+json;v=2.0','Content-Type': 'application/x-www-form-urlencoded;v=2.0'}
        self.ip = ip
        self.port = port
        self.proto = proto
        self.user = user
        self.pwd = pwd
        self.cookie = ''
        self.url = self.proto + self.ip + ':' + str(self.port)
        self.conn = requests.Session()
        self.has_mastership = False
        self.login()

    def __str__(self):
        s = 'The object of class "Robot" contains:\n'
        s+= f'\tIP: "{self.ip}"\n'
        s+= f'\tport:{self.port}\n'
        s+= f'\tuser:{self.user}\n'
        s+= f'\tpwd:{self.pwd}\n'
        s+= f'\theader:{self.header}\n'
        return s

    def __POST(self, rq, data=None):
        return self.__request("POST", rq, data=data)

    def __GET(self, rq):
        return self.__request("GET", rq)

    def __request(self, method, rq='', data=None):
        try:
            url = self.url + rq
            match method:
                case 'GET':
                    resp = self.conn.get(url, headers=self.header, auth=basic_auth, verify=False)
                    if len(resp.content) > 0:
                        return json.loads(resp.content), resp.status_code
                    else:
                        return None, resp.status_code
                case 'POST':
                    resp = self.conn.post(url, data=data, headers=self.header, auth=basic_auth, verify=False)
                case _:
                    raise Exception("Method not supported")


        except Exception as error:
            logger.error(f"Error: {error}")
        
        return None, None

    def login(self):
            resp = self.conn.post(self.url, auth=basic_auth, headers=self.header, verify=False)
            logger.info('Login: Done!')
            session = resp.cookies['-http-session-']
            ABBCX = resp.cookies['ABBCX']
            self.cookie = f'-http-session-={session}; ABBCX={ABBCX}'
            logger.info('Cookie: %s', self.cookie)

    def logout(self):
        _, code = self.__GET('/logout')
        logger.info(f"Logout: {code}")

    def list_rapid_variables(self):
        ...

    def requires_mastership(self, func: callable):
        def wrapper(self, *args, **kwargs):
            if self.has_mastership:
                return func(self, *args, **kwargs)
            else:
                logger.info("You do not have mastership")
                return
        return wrapper

    def requires_manual_mode(self, func: callable):
        def wrapper(self, *args, **kwargs):
            if self.has_mastership:
                return func(self, *args, **kwargs)
            else:
                logger.info("You do not have mastership")
        return wrapper

    #@requires_mastership
    def get_tasks(self) -> list:
        content, code = self.__GET("/rw/rapid/tasks")
        # Unmarshal the received JSON into a list of Task objects
        tasks = []
        for task in content['_embedded']['resources']:
            tasks.append(from_dict(Task, task))
        return tasks

    def get_task_modules(self, task_name: str) -> list:
        content, code = self.__GET("/rw/rapid/tasks/" + task_name + "/modules")
        # Unmarshal the received JSON into a list of Module objects
        modules = []
        for module in content['state']:
            modules.append(from_dict(Module, module))
        return modules
    
    def get_task_service_routines(self, task_name) -> list:
        pp(self.__GET("/rw/rapid/tasks/" + task_name + "/serviceroutine"))

    def get_module_attributes(self, task_name, module_name) -> list:
        pp(self.__GET("/rw/rapid/tasks/" + task_name + "/modules/" + module_name))

    def get_module_symbol(self, task_name, module_name) -> list:
        pp(self.__GET("/rw/rapid/tasks/" + task_name + "/modules/" + module_name + "/symbol"))

    def get_module_routines(self, task_name, module_name) -> list:
        pp(self.__GET("/rw/rapid/tasks/" + task_name + "/modules/" + module_name + "/routine" + "?row=0&column=0"))

    #@requires_mastership
    def set_rapid_variable(self, variable, value):
        """ 
        Set a Rapid Variable with the given value.\n
        The variable must be a string in the format `task_name/module_name/variable_name`
        """
        self.__POST("/rw/rapid/symbol/RAPID/" + variable + "/data?mastership=implicit", data={"value": value})

    def get_rapid_variable(self, url=None, variable=None) -> tuple:
        if url is None:
            url = "/rw/rapid/symbol/RAPID/" + variable + "/data"
        return self.__GET(url)

    def request_mastership(self):
        """Request mastership on all domains."""
        _, code = self.__POST("/rw/mastership/request")
        if code == 204:
            self.has_mastership = True
            logger.info("You have mastership")
        else:
            raise Exception("Could not request mastership")

    def release_mastership(self):
        _, code = self.__POST("/rw/mastership/release")
        print(code)
        if code == 200:
            self.has_mastership = False
            logger.info("You have released mastership")

    def subscribe(self, variables: list[str], on_message: callable=None):
        """
            Subscribes to the given variables and calls the on_message function when a message is received.
            The `on_message` function receives the updated value of the variable.

            @param variables: The variables to subscribe to. Each variable must be a valid *path* to a RAPID variable.
            Example: `T_ROB1/main/Flag` for the variable `Flag` in the task `T_ROB1` in the `main` module.
            
            @param on_message: The function to call when a message is received.
            The function passed must accept one parameter, the updated value of the variable.
        """

        # Variable API endpoint
        payload = {}
        payload['resources'] = [str(i) for i in range(1, len(variables) + 1)]
        for i, variable in enumerate(variables):
            uri = "/rw/rapid/symbol/RAPID/" + variable + "/data;value"
            payload[str(i + 1)] = uri
            payload[f'{i + 1}-p'] = '1'

        print(payload)
        try:
            resp = self.conn.post(self.url + '/subscription', headers=self.header, auth=basic_auth, data=payload)

            # Status code 201 means that the subscription was successful
            if resp.status_code != 201:
                # If the subscription failed, log the error and exit
                logger.info('Error: %s', resp.status_code)
                return
            logger.info('Successfully subscribed to %s', variable)
            websock_headers = [('Cookie', self.cookie)]
            
            # Initialize and start the websocket
            robwebscoket = RobWebSocketClient(resp.headers['location'], websock_headers, self, on_message=on_message)
            for variable in variables:
                robwebscoket.variables.append(variable)
            robwebscoket.start()

        except Exception as error:
            logger.exception('Error: %s', error)

