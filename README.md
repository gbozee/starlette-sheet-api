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

### Running it locally
spin up a local virtual environment using this command below for python3 in linux
` python3 -m venv env`

Activate the virtual environment by running this code
`source env/bin/activate`

Install the dependencies from the reqquirements.txt
`python3 -m pip install -r requirements.txt`

Running the app server
`uvicorn index:app --reload`

### Example usage
`POST request to BASE_URL/read-sheetnames`
with the body in the form of 
`{
	"link": google_spreadsheet_link
}`

The result is in the form 
`{
  "status": true,
  "data": {
    "title": "IELTS Video Lessons",
    "sheet_names": [
      "Reading",
      "Listening",
      "Speaking",
      "Writing"
    ]
  }
}`

`POST request to BASE_URL/read-single`
with the body in the form of 
`{
	"link": "https://docs.google.com/spreadsheets/d/1m_1dKUJjDeTPctDMWA3Iuxx29DHj4gLDVXB0yHOygUM/edit#gid=1515920062",
	"sheet": "Mathematics Mastersheet",
	"page": 2,
	"page_size": 20
}
`

The result is in the form 
`{
  "status": true,
  "data": {
    "page_size": 20,
    "page": 2,
    "next_page": 3,
    "prev_page": 1
    "total_row_count": 2548,
    "row_range": {
      "first": 128,
      "last": 254
    },
    "sheet_names": []
  }
    `