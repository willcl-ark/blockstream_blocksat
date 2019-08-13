import requests

SATELLITE_API = "https://api.blockstream.space"
TESTNET_SATELLITE_API = "https://api.blockstream.space/testnet"


def place(message, bid, sat_url):
    """Place an order for a message transmission.

    If successful, the response includes the JSON Lightning invoice as returned by
    Lightning Charge's POST /invoice and an authentication token that can be used to
    modify the order.
    """
    data = {"message": message, "bid": bid}
    return requests.post(url="{}/order".format(sat_url), data=data, timeout=30)


def bump_order(uuid, auth_token, bid_increase, sat_url):
    """Increase the bid for an order sitting in the transmission queue.

    A Lightning invoice is returned for it and, when it is paid, the increase is added
    to the current bid.
    """
    data = {"bid_increase": bid_increase, "auth_token": auth_token}
    return requests.post(
        url="{}/order/{}/bump".format(sat_url, uuid), data=data, timeout=30
    )


def get(uuid, auth_token, sat_url):
    """Retrieve an order by UUID.
    """
    headers = {"X-Auth-Token": auth_token}
    return requests.get(
        url="{}/order/{}".format(sat_url, uuid), headers=headers, timeout=30
    )


def delete(uuid, auth_token, sat_url):
    """To cancel an order.
    """
    data = {"auth_token": auth_token}
    return requests.delete(
        url="{}/order/{}".format(sat_url, uuid), data=data, timeout=30
    )


def pending_orders(sat_url, before_iso8601=None):
    """Retrieve a list of 20 orders awaiting payment ordered by creation time.

    For pagination, optionally specify a before parameter (in ISO 8601 format) that
    specifies that the 20 orders immediately prior to the given time be returned.
    """
    if before_iso8601:
        return requests.get(
            url="{}/orders/pending?before={}.".format(sat_url, before_iso8601),
            timeout=30,
        )
    else:
        return requests.get(url="{}/orders/pending".format(sat_url), timeout=30)


def queued_orders(sat_url, limit=None):
    """Retrieve a list of paid, but unsent orders in descending order of bid-per-byte.
    Both pending orders and the order currently being transmitted are returned.
    Optionally, accepts a parameter specifying how many queued order to return.
    """
    if limit:
        return requests.get(
            url="{}/orders/queued?limit={}".format(sat_url, limit), timeout=30
        )
    else:
        return requests.get(url="{}/orders/queued".format(sat_url), timeout=30)


def sent_orders(sat_url, before_iso8601=None):
    """Retrieves a list of up to 20 sent orders in reverse chronological order.
    For pagination, optionally specify a before parameter (in ISO 8601 format) that
    specifies that the 20 orders immediately prior to the given time be returned.
    """
    if before_iso8601:
        return requests.get(
            url="{}/orders/sent?before={}".format(sat_url, before_iso8601), timeout=30
        )
    else:
        return requests.get(url="{}/orders/sent".format(sat_url), timeout=30)


def sat_ln_node_info(sat_url):
    """Returns information about the c-lightning node where satellite API payments are
    terminated.
    """
    return requests.get(url="{}/info".format(sat_url), timeout=30)
