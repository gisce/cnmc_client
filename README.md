# CNMC client

It provides a Python client desired to interact with the CNMC API.

## Usage

Simply configure the KEY and the SECRET as exported environment vars, or attach it at Client initialization time

### ENV vars

Just define the needed ENV vars:
```
$ export CNMC_CONSUMER_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxxxx
$ export CNMC_CONSUMER_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxxx

```

, and instantiate the Client without any parameter:

```
from cnmc_client import Client
client = Client()
``` 

### Passed config

Instantiate the Client passing the key and secret oauth tokens:

```python

from cnmc_client import Client

oauth_config = {
    'key': "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxxxx",
    'secret': "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxxxx",
}

client = Client(**oauth_config)
```

## Available methods

- [Test](#test-method)
- [List](#list-method)
- [Fetch](#fetch-method)
- [Download](#download-method)


### Test method
Method desired to test the connection with the API using the `echoseguro` resource.

```python
client.test(message="This is a test message!")
```


### List method

List downloaded files or files able to be downloaded, with the capacity of filter it by:
- start_date
- end_date
- status in ["DISPONIBLE", "DESCARGADO"]

```python
STATUS = "DISPONIBLE"
date_start = 
date_end = 

client.list(status=STATUS, date_start=date_start, date_end=date_end)
```

### Fetch method

Define the list of CUPS to analyze and the desired file type.

List of types:
- SIPS2_PS_ELECTRICIDAD
- SIPS2_CONSUMOS_ELECTRICIDAD
- SIPS2_PS_GAS
- SIPS2_CONSUMOS_GAS

```python
the_cups = [ "CUPSA", "CUPSB" ]
the_type = "SIPS2_PS_ELECTRICIDAD"

client.fetch(cups=the_cups, file_type=the_type)
```


### Download method

```python
```
