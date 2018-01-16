# CNCM client

It provides a Python client desired to interact with the CNMC API.

## Usage

Simply configure the KEY and the SECRET as exported environment vars, or attach it at Client initialization time

### ENV vars

```
export CNMC_CONSUMER_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxxxx
export CNMC_CONSUMER_SECRET=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxxx
```

### Passed config

oauth_config = {
    'key': "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxxxx",
    'secret': "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxxxxx",
}

