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
        self.r_bump = None
        self.r_delete = None
        self.r_get = None
        self.r_node_info = None
        self.r_pending = None
        self.r_place = None
        self.r_queued = None
        self.r_sent = None
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
            self.r_place = self.handle_response(response)
            self.auth_token = self.r_place['auth_token']
            self.uuid = self.r_place['uuid']
            return
        return response.status_code, response.reason, response.text

    def bump(self, bid_increase):
        """Increase the bid for an order sitting in the transmission queue.

        A Lightning invoice is returned for it and, when it is paid, the increase is added to the
        current bid.
        """
        data = {"bid_increase": bid_increase,
                "auth_token": self.auth_token}
        response = requests.post(url=f"{self.satellite_url}/order/{self.uuid}/bump", data=data)
        self.api_status_code = response.status_code
        if response.status_code == 200:
            self.r_bump = self.handle_response(response)
            return
        return response.status_code, response.reason, response.text

    def get(self):
        """Retrieve an order by UUID.
        """
        headers = {"X-Auth-Token": self.auth_token}
        response = requests.get(url=f"{self.satellite_url}/order/{self.uuid}", headers=headers)
        self.api_status_code = response.status_code
        if response.status_code == 200:
            self.r_get = self.handle_response(response)
            return
        return response.status_code, response.reason, response.text

    def delete(self):
        """To cancel an order.
        """
        data = {"auth_token": self.auth_token}
        response = requests.delete(url=f"{self.satellite_url}/order/{self.uuid}", data=data)
        self.api_status_code = response.status_code
        if response.status_code == 200:
            self.r_delete = self.handle_response(response)
            return
        return response.status_code, response.reason, response.text

    def pending(self, before_iso8601=None):
        """Retrieve a list of 20 orders awaiting payment ordered by creation time.

        For pagination, optionally specify a before parameter (in ISO 8601 format) that specifies
        that the 20 orders immediately prior to the given time be returned.
        """
        if before_iso8601:
            response =  requests.get(url=f"{self.satellite_url}/orders/pending?before={before_iso8601}")
        else:
            response = requests.get(url=f"{self.satellite_url}/orders/pending")
        self.api_status_code = response.status_code
        if response.status_code == 200:
            self.r_pending = self.handle_response(response)
            return
        return response.status_code, response.reason, response.text

    def queued(self, limit=None):
        """Retrieve a list of paid, but unsent orders in descending order of bid-per-byte.
        Both pending orders and the order currently being transmitted are returned.
        Optionally, accepts a parameter specifying how many queued order to return.
        """
        if limit:
            response = requests.get(url=f"{self.satellite_url}/orders/queued?limit={limit}")
        else:
            response = requests.get(url=f"{self.satellite_url}/orders/queued")
        self.api_status_code = response.status_code
        if response.status_code == 200:
            self.r_queued = self.handle_response(response)
            return
        return response.status_code, response.reason, response.text

    def sent(self, before_iso8601=None):
        """Retrieves a list of up to 20 sent orders in reverse chronological order.
        For pagination, optionally specify a before parameter (in ISO 8601 format) that specifies
        that the 20 orders immediately prior to the given time be returned.
        """
        if before_iso8601:
            response = requests.get(url=f"{self.satellite_url}/orders/sent?before={before_iso8601}")
        else:
            response = requests.get(url=f"{self.satellite_url}/orders/sent")
        self.api_status_code = response.status_code
        if response.status_code == 200:
            self.r_sent = self.handle_response(response)
            return
        return response.status_code, response.reason, response.text

    def sat_ln_node_info(self):
        """Returns information about the c-lightning node where satellite API payments are
        terminated.
        """
        response = requests.get(url=f"{self.satellite_url}/info")
        self.api_status_code = response.status_code
        if response.status_code == 200:
            self.r_node_info = self.handle_response(response)
            return
        return response

