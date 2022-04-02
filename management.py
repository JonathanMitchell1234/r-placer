import bot
import parse_image
import json
from queue import Queue
from PIL import Image
from io import BytesIO
from csv import reader
from requests import get
from websocket import create_connection


class manager:
    def __init__(self, image_dir, location):
        self.image = parse_image.parse_image(image_dir, *location)
        self.accounts = []
        with open('accounts.csv', 'r') as f:
            for row in reader(f):
                email, username, password = row
                self.accounts.append({
                    'email': email,
                    'username': username,
                    'password': password,
                    'class': bot.account(username, password)
                })

    def get_board(self):  # from https://github.com/rdeepak2002/reddit-place-script-2022/blob/main/main.py
        self.accounts[0]['class'].get_auth_token()
        ws = create_connection(
            "wss://gql-realtime-2.reddit.com/query",
            origin="https://hot-potato.reddit.com",
        )
        ws.send(
            json.dumps(
                {
                    "type": "connection_init",
                    "payload": {"Authorization": self.accounts[0]['class'].auth_token},
                }
            )
        )
        ws.recv()
        ws.send(
            json.dumps(
                {
                    "id": "1",
                    "type": "start",
                    "payload": {
                        "variables": {
                            "input": {
                                "channel": {
                                    "teamOwner": "AFD2022",
                                    "category": "CONFIG",
                                }
                            }
                        },
                        "extensions": {},
                        "operationName": "configuration",
                        "query": "subscription configuration($input: SubscribeInput!) {\n  subscribe(input: $input) {\n    id\n    ... on BasicMessage {\n      data {\n        __typename\n        ... on ConfigurationMessageData {\n          colorPalette {\n            colors {\n              hex\n              index\n              __typename\n            }\n            __typename\n          }\n          canvasConfigurations {\n            index\n            dx\n            dy\n            __typename\n          }\n          canvasWidth\n          canvasHeight\n          __typename\n        }\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
                    },
                }
            )
        )
        ws.recv()
        ws.send(
            json.dumps(
                {
                    "id": "2",
                    "type": "start",
                    "payload": {
                        "variables": {
                            "input": {
                                "channel": {
                                    "teamOwner": "AFD2022",
                                    "category": "CANVAS",
                                    "tag": "0",
                                }
                            }
                        },
                        "extensions": {},
                        "operationName": "replace",
                        "query": "subscription replace($input: SubscribeInput!) {\n  subscribe(input: $input) {\n    id\n    ... on BasicMessage {\n      data {\n        __typename\n        ... on FullFrameMessageData {\n          __typename\n          name\n          timestamp\n        }\n        ... on DiffFrameMessageData {\n          __typename\n          name\n          currentTimestamp\n          previousTimestamp\n        }\n      }\n      __typename\n    }\n    __typename\n  }\n}\n",
                    },
                }
            )
        )

        file = ""
        while True:
            temp = json.loads(ws.recv())
            if temp["type"] == "data":
                msg = temp["payload"]["data"]["subscribe"]
                if msg["data"]["__typename"] == "FullFrameMessageData":
                    file = msg["data"]["name"]
                    break

        ws.close()
        return BytesIO(get(file, stream=True).content)

    def get_image_state(self):
        canvas = Image.open(self.get_board())
        # more stuff coming

    def stage_events(self):  # get all unset pixels from get_image_state. create a queue of events that can that the accounts can execute.
        pass


if __name__ == '__main__':
    m = manager('/Users/shum/Desktop/Screenshot 2022-04-03 at 3.16.13 AM.png', (0, 0))
    m.get_board()
