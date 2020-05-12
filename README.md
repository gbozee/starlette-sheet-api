# starlette-sheet-api
An api hosted on now.sh that makes it easy to process actions on a google sheet document


The following environmental variables are required to connect to google sheet when creating the server

```
export GOOGLE_PROJECT_ID=******
export GOOGLE_PRIVATE_KEY_ID=****
export GOOGLE_PRIVATE_KEY=$"-----BEGIN PRIVATE KEY -----\n****"
export GOOGLE_CLIENT_EMAIL=******
```

when adding the secret for the `google_private_key` on `now.sh`
use the following

```
now secret add google_private_key '"----BEGIN PRIVATE KEY ----\N***"'
```