# Lighthouse API — Tool usage stats

## URL

`/api/links/:id/usage`

`:id` — the ID of the tool

## GET

An HTTP GET request will return a JSON array of usage stats for the given 
tool's `:id`.

**Arguments**: The ID of the tool in the URL.

**Command-line example**:

    $ curl http://lighthouse_host/api/links/1/usage
    [
        {"user": "alice", "date": "2016-03-04T14:53:25.740Z"},
        {"user": "bob", "date": "2016-03-04T14:53:35.143Z"},
        {"user": "claire", "date": "2016-03-04T15:16:12.000Z"}
    ]

**Python example**:

    >>> import requests
    >>> response = requests.get('http://lighthouse_host/api/links/1/usage')
    >>> response.status_code
    200
    >>> response.json()
    [
        {u'user': 'alice', 'date': '2016-03-04T14:53:25.740Z'},
        {u'user': 'bob', 'date': '2016-03-04T14:53:35.143Z'},
        {u'user': 'claire', 'date': '2016-03-04T15:16:12.000Z'}
    ]

**Response codes**

* **200** data returned
* **404** no such link

## POST

An HTTP POST request will add a new usage statistic for the given 
tool's `:id`.

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
