import functools
import json

import requests

SATELLITE_API = "https://api.blockstream.space"
TESTNET_SATELLITE_API = "https://api.blockstream.space/testnet"


# def handle_response(func):
#     """Return json.loads of response.text if successful, and response.status_code if unsuccessful
#     """
#
#     @functools.wraps(func)
#     def handle_response_wrapper(*args, **kwargs):
#         response = func(*args, **kwargs)
#         if response.status_code == 200:
#             response.attr = json.loads(response.text)
#             return
#         return response.status_code, response.reason, response.text
#
#     return handle_response_wrapper


class Order:

    def __init__(self, auth_token=None, message=None, network='mainnet', uuid=None):
        self.auth_token = auth_token
        self.api_status_code = None
        self.message = message
        self.network = network
        self.bump_order = None
        self.delete_order = None
        self.get_order = None
        self.node_info = None
        self.place_order = None
        self.queued_orders = None
        self.sent_orders = None
        self.satellite_url = None
        self.uuid = uuid
        if self.network == 'mainnet':
            self.satellite_url = SATELLITE_API
        elif self.network == 'testnet':
            self.satellite_url = TESTNET_SATELLITE_API

    @staticmethod
    def handle_response(response):
        return json.loads(response.text)

    def place(self, bid):
        """Place an order for a message transmission.

            If successful, the response includes the JSON Lightning invoice as returned by Lightning
            Charge's POST /invoice and an authentication token that can be used to modify the order.
            """
        data = {"message": self.message,
                "bid": bid}
        response = requests.post(url=f"{self.satellite_url}/order", data=data)
        self.api_status_code = response.status_code
        if response.status_code == 200:
            self.place_order = self.handle_response(response)
            self.auth_token = self.place_order['auth_token']
            self.uuid = self.place_order['uuid']
            return
        return response.status_code, response.reason, response.text

    def bump_order(self, bid_increase):
        """Increase the bid for an order sitting in the transmission queue.

        A Lightning invoice is returned for it and, when it is paid, the increase is added to the
        current bid.
        """
        data = {"bid_increase": bid_increase,
                "auth_token": self.auth_token}
        response = requests.post(url=f"{self.satellite_url}/order/{self.uuid}/bump", data=data)
        self.api_status_code = response.status_code
        if response.status_code == 200:
            self.bump_order = self.handle_response(response)
            return
        return response.status_code, response.reason, response.text

    def get(self):
        """Retrieve an order by UUID.
        """
        headers = {"X-Auth-Token": self.auth_token}
        response = requests.get(url=f"{self.satellite_url}/order/{self.uuid}", headers=headers)
        self.api_status_code = response.status_code
        if response.status_code == 200:
            self.get_order = self.handle_response(response)
            return
        return response.status_code, response.reason, response.text

    def delete(self):
        """To cancel an order.
        """
        data = {"auth_token": self.auth_token}
        response = requests.delete(url=f"{self.satellite_url}/order/{self.uuid}", data=data)
        self.api_status_code = response.status_code
        if response.status_code == 200:
            self.delete_order = self.handle_response(response)
            return
        return response.status_code, response.reason, response.text

    @classmethod
    def pending(cls, sat_url, before_iso8601=None):
        """Retrieve a list of 20 orders awaiting payment ordered by creation time.

        For pagination, optionally specify a before parameter (in ISO 8601 format) that specifies
        that the 20 orders immediately prior to the given time be returned.
        """
        if before_iso8601:
            response = requests.get(url=f"{sat_url}/orders/pending?before={before_iso8601}")
        else:
            response = requests.get(url=f"{sat_url}/orders/pending")
        if response.status_code == 200:
            return cls.handle_response(response)
        return response.status_code, response.reason, response.text

    @classmethod
    def queued(cls, sat_url, limit=None):
        """Retrieve a list of paid, but unsent orders in descending order of bid-per-byte.
        Both pending orders and the order currently being transmitted are returned.
        Optionally, accepts a parameter specifying how many queued order to return.
        """
        if limit:
            response = requests.get(url=f"{sat_url}/orders/queued?limit={limit}")
        else:
            response = requests.get(url=f"{sat_url}/orders/queued")
        if response.status_code == 200:
            return cls.handle_response(response)
        return response.status_code, response.reason, response.text

    @classmethod
    def sent(cls, sat_url, before_iso8601=None):
        """Retrieves a list of up to 20 sent orders in reverse chronological order.
        For pagination, optionally specify a before parameter (in ISO 8601 format) that specifies
        that the 20 orders immediately prior to the given time be returned.
        """
        if before_iso8601:
            response = requests.get(url=f"{sat_url}/orders/sent?before={before_iso8601}")
        else:
            response = requests.get(url=f"{sat_url}/orders/sent")
        if response.status_code == 200:
            return cls.handle_response(response)
        return response.status_code, response.reason, response.text

    @classmethod
    def sat_ln_node_info(cls, sat_url):
        """Returns information about the c-lightning node where satellite API payments are
        terminated.
        """
        response = requests.get(url=f"{sat_url}/info")
        if response.status_code == 200:
            return cls.handle_response(response)
        return response
