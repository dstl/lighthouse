# Lighthouse API — Tool usage stats

## URL

`/api/links/:id/usage`

`:id` — the ID of the tool

## GET

An HTTP GET request will return a JSON array of usage stats for the given 
tool's `:id`. The data structure contains the following fields:

* `user` — the ID of the user
* `date` — the timestamp when the user started using the tool
* `duration` — how long they used it for. A value of 0 means that that
    tool does not update lighthouse during active usage.


**Arguments**: The ID of the tool in the URL.

**Command-line example**:

    $ curl http://lighthouse_host/api/links/1/usage
    [
        {"user": "alice", "date": "2016-03-04T14:53:25.740Z", "duration": 0},
        {"user": "claire", "date": "2016-03-04T15:16:12.000Z", "duration": 0}
    ]

    $ curl http://lighthouse_host/api/links/2/usage
    [
        {"user": "bob", "date": "2016-03-04T14:53:35.143Z", "duration": 3420}
    ]

**Python example**:

    >>> import requests
    >>> response = requests.get('http://lighthouse_host/api/links/1/usage')
    >>> response.status_code
    200
    >>> response.json()
    [
        {u'user': 'alice', 'date': '2016-03-04T14:53:25.740Z', 'duration': 0},
        {u'user': 'claire', 'date': '2016-03-04T15:16:12.000Z', 'duration': 0}
    ]

    >>> response = requests.get('http://lighthouse_host/api/links/2/usage')
    >>> response.json()
    [
        {u'user': 'bob', 'date': '2016-03-04T14:53:35.143Z', 'duration': 3420}
    ]

**Response codes**

* **200** data returned
* **404** no such link

## POST

An HTTP POST request will add a new usage statistic for the given 
tool's `:id`.

If it is received within one hour of the last time that user's usage stat was
posted it will cause lighthouse to update that usage with a duration, rather
than create a new usage data point.

**Arguments**: The ID of the tool in the URL. The `user` parameter, sent
form encoded.

**Command-line example**

    $ curl --data "user=dave" http://lighthouse_host/api/links/1/usage
    {"status": "ok"}

**Python example**

    >>> import requests
    >>> response = requests.post(
        'http://lighthouse_host/api/links/1/usage',
        data={'user': 'dave'}
    )
    >>> response.status_code
    201
    >>> response.json()
    {u'status': u'ok'}

**Response codes**

* **201** usage registered
* **400** incorrect arguments (more detail in JSON body)
* **404** no such link
