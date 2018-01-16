# CNCM client

It provides a Python client desired to interact with the CNMC API.

## Usage

Simply configure the KEY and the SECRET as exported environment vars, or attach it at Client initialization time

### ENV vars

```
$ export CNMC_CONSUMER_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxxxx
$ export CNMC_CONSUMER_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxxx

```

### Passed config

```
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

```
self.client.test(message="This is a test message!")
```


### List method

```
```


### Fetch method

Define the list of CUPS to analyze and the desired file type.

List of types:
- SIPS2_PS_ELECTRICIDAD
- SIPS2_CONSUMOS_ELECTRICIDAD
- SIPS2_PS_GAS
- SIPS2_CONSUMOS_GAS

```
the_cups = [ "CUPSA", "CUPSB" ]
the_type = "SIPS2_PS_ELECTRICIDAD"

self.client.fetch(cups=the_cups, file_type=the_type)
```


### Download method

```
```
