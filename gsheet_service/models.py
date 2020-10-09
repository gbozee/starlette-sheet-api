import typing
from urllib.parse import quote_plus
import logging
import gspread
from gspread import models as g_models, utils
from oauth2client.service_account import ServiceAccountCredentials

DEFAULT_SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]


def build_credential_json(
    project_id: str = None,
    private_key_id: str = None,
    private_key=None,
    client_email=None,
    client_id: str = None,
):
    data = {
        "type": "service_account",
        "project_id": project_id,
        "private_key_id": private_key_id,
        "private_key": private_key,
        "client_email": client_email,
        "client_id": client_id,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{quote_plus(client_email.encode('utf-8'))}",
    }
    return data


def create_credentials_from_file(client_secret, additional_scopes=None):
    scope = (additional_scopes or []) + DEFAULT_SCOPES
    credentials = ServiceAccountCredentials.from_json_keyfile_name(client_secret, scope)

    gc = gspread.authorize(credentials)
    return gc


def create_credentials(additional_scopes=None, **kwargs):
    scope = (additional_scopes or []) + DEFAULT_SCOPES
    credential_dict = build_credential_json(**kwargs)
    #logging.info(credential_dict)
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(
        credential_dict, scope
    )

    gc = gspread.authorize(credentials)
    return gc


class GoogleSheetInterface:
    def __init__(
        self,
        key_location: str = None,
        project_id: str = None,
        private_key_id: str = None,
        private_key=None,
        client_email=None,
        client_id: str = None,
    ):
        if key_location:
            self.gc = create_credentials(key_location)
        else:
            self.gc = create_credentials(
                project_id=project_id,
                private_key=private_key,
                private_key_id=private_key_id,
                client_email=client_email,
                client_id=client_id,
            )
        self.file = None
        self.data = []

    def sheet_names(self):
        return [x.title for x in self.file.worksheets()]
    
    def get_sheet_names(self, url: str):
        self.file = self.gc.open_by_url(url)
        return [x.title for x in self.file.worksheets()]
    
    def get_spreadsheet_title(self, url: str):
        self.file = self.gc.open_by_url(url)
        return self.file.title


    def get_sheet_by_name(self, name) -> g_models.Worksheet:
        result = [
            x for x in self.file.worksheets() if name.lower() in x.title.strip().lower()
        ]
        if result:
            return result[0]

    def load_file(self, url: str, sheet_name: str):
        self.file = self.gc.open_by_url(url)
        self.sheet = self.get_sheet_by_name(sheet_name)
        return self

    def get_all_records(self):
        return self.sheet.get_all_records()
    
    def get_row_count(self):
        return len(self.sheet.get_all_values())

    def find_cell(self, cell):
        return self.sheet.find(cell)

    async def bulk_save(
        self, column_id: int = None, http_client_function: typing.Callable = None
    ) -> typing.Dict[str, typing.Any]:
        column_values = self.sheet.col_values(column_id)[1:]
        results = await http_client_function(column_values)
        return {x[0]: x[1] for x in zip(column_values, results)}

    def update_records(self, data: typing.List[typing.Any]):
        column_indices = self.get_indexes()
        index = self.get_row_to_write()
        keys = list(column_indices.keys())
        obj = {}
        for i, v in enumerate(data):
            column = keys[i]
            self.sheet.update_cell(index, i + 1, str(v))
            obj[column] = v
        return keys[0], obj

    def read_last_row(self):
        all_records = self.sheet.get_all_records()
        if len(all_records) > 0:
            return all_records[-1]
        return {}

    def get_row_to_write(self):
        all_values = self.sheet.get_all_values()
        return len(all_values) + 1

    def get_cell_identity(self, key, value):
        all_values = self.sheet.get_all_values()
        key_index = get_key_index(all_values, key)
        row_index = get_row_index(all_values, value)
        if row_index:
            return (row_index, key_index)
        raise ValueError("Missing Row Index")

    def get_indexes(self):
        all_values = self.sheet.get_all_values()
        keys = all_values[0]
        return {x: get_key_index(all_values, x) for x in keys}

    def get_row_cell_ids(self, key, value):
        all_values = self.sheet.get_all_values()
        keys = all_values[0]
        row_index = get_row_index(all_values, value)
        return {x: [row_index, get_key_index(all_values, x)] for x in keys}

    def update_existing_record(self, key, value, data, check=False):
        cell_ids_dict = self.get_row_cell_ids(key, value)
        if check:
            valid = all([p in cell_ids_dict.keys() for p in data.keys()])
            if not valid:
                raise KeyError("Invalid params passed")
        for x, y in data.items():
            coordinate = cell_ids_dict[x]
            self.sheet.update_cell(*coordinate, y)

    def fetch_groups(self, segments):
        results = [
            (self.sheet.get(x["cell_range"]), x.get("heading")) for x in segments
        ]
        return [as_dict(s[0], heading=s[1]) for s in results]
    


def get_key_index(all_values, key):
    return all_values[0].index(key) + 1


def get_row_index(all_values, value):
    row_index = None
    found_item = [(i, j) for i, j in enumerate(all_values) if value in j]
    if found_item:
        row_index = found_item[0][0] + 1
    return row_index


def as_dict(arr, heading=None):
    # keys = arr[0]
    keys = heading or arr[0]
    values = arr[1:]
    if heading:
        values = arr
    results = []
    for k in values:
        item = {}
        for i, j in enumerate(keys):
            item[j] = k[i]
        results.append(item)
    return results

def paginate_response(response, num_of_pages):
    avg = len(response) / float(num_of_pages)
    split_array = []
    last = 0.0

    while last < len(response):
        split_array.append(response[int(last):int(last + avg)])
        last += avg

    return split_array



