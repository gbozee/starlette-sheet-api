import typing
from urllib.parse import quote_plus
import logging
import gspread
import re
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
    # logging.info(credential_dict)
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

    def populate_heading(self, heading):
        letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        cols = [k for (i, k) in enumerate(letters) if i in range(len(heading))]
        heading_range = f"{cols[0]}1:{cols[-1]}1"
        self.sheet.update(heading_range, [heading])

    def create_new_sheet(self, url: str, name: str, heading: typing.List[typing.Any]):
        self.file = self.gc.open_by_url(url)
        self.sheet = self.file.add_worksheet(title=name, rows="1000", cols="10")
        self.populate_heading(heading)
        # self.update_records(heading)
        result = [x.title for x in self.file.worksheets()]
        title = self.file.title
        return {"title": title, "sheet_names": result}

    def edit_sheet(self, url: str, name: str, heading: typing.List[typing.Any]):
        self.load_file(url, name)
        self.populate_heading(heading)
        result = [x.title for x in self.file.worksheets()]
        title = self.file.title
        return {"title": title, "sheet_names": result}

    def get_all_records(self):
        return self.sheet.get_all_records()

    def get_row_count(self):
        return self.sheet.row_count

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

    def get_row_cell_ids(self, key, value, addition=0):
        all_values = self.sheet.get_all_records()
        keys = all_values[0]
        row_index = 0
        for i, j in enumerate(all_values):
            if j[key] == value:
                row_index = i
        row_index = row_index + 1
        # import pdb; pdb.set_trace()
        # row_index = get_row_index(all_values, value, index=addition)
        # if row_index == None:
        #     row_index = 1
        # row_index = row_index + addition
        return {
            x: [row_index + addition, get_key_index(self.sheet.get_all_values(), x)]
            for x in keys
        }

    def update_existing_record(self, key, value, data, check=False):
        cell_ids_dict = self.get_row_cell_ids(key, value, 1)
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

    def get_referenced_cell_values(self, options):
        all_column_names: list = [
            (column.lower()).strip() for column in self.sheet.row_values(1)
        ]
        complete_values = dict()
        for column in options.get("columns"):
            if isinstance(column, str):
                unique_cells = get_cells(
                    self.sheet.col_values(all_column_names.index(column.lower()) + 1)
                )
                column_value = self.sheet.batch_get(unique_cells)
                expected_dict = get_cell_data(unique_cells, column_value)
                complete_values[column] = expected_dict
            else:
                unique_cells = get_cells(self.sheet.col_values(column))
                column_value = self.sheet.batch_get(unique_cells)
                expected_dict = get_cell_data(unique_cells, column_value)
                complete_values[column] = expected_dict

        return complete_values


def get_key_index(all_values, key):
    return all_values[0].index(key) + 1


def get_row_index(all_values, value, index=0):
    row_index = None
    found_item = [(i, j) for i, j in enumerate(all_values) if value in j]
    if found_item:
        row_index = found_item[0][0] + 1
    if row_index is not None:
        row_index = row_index
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
            try:
                item[j] = k[i]
            except IndexError as e:
                item[j] = ""
        results.append(item)
    return results


def paginate_response(response, page_size):
    avg = len(response) / float(page_size)
    split_array = []
    last = 0.0

    while last < len(response):
        split_array.append(response[int(last) : int(last + avg)])
        last += avg
    return split_array


# def get_row_range_from_sheet(result, instance):
#     first_key = (list(result[0].keys()))[0]
#     last_key = (list(result[0].keys()))[0]
#     first_question_id = result[0][first_key]
#     last_question_id = result[-1][last_key]
#     first = instance.find_cell(first_question_id).row
#     last = instance.find_cell(last_question_id).row
#     row_range = dict(first=first, last=last)
#     return row_range


def get_page(response, page_size, page):
    split_response = paginate_response(response, page_size)
    sub_array = split_response[page - 1]
    first = response.index(sub_array[0]) + 1
    last = response.index(sub_array[-1]) + 1
    result = {
        "first_row": first,
        "last_row": last,
        "total_row_count": len(response),
        "page": page,
        "page_size": page_size,
        "questions": sub_array,
    }

    return result


def get_cells(column_data):
    cleaned_data = ",".join(list(set(column_data)))
    pattern = re.compile(r'[A-Z]\d+"')
    cells = pattern.findall(cleaned_data)
    cells.sort()
    cells = [cell.replace('"', "") for cell in cells]
    return cells


def get_cell_data(unique_cells, cell_data):
    cell_dictionary = dict()
    for n in unique_cells:
        cell_dictionary[unique_cells[unique_cells.index(n)]] = cell_data[
            unique_cells.index(n)
        ][0][0]
        cell_dictionary[unique_cells[unique_cells.index(n)]] = cell_data[
            unique_cells.index(n)
        ][0][0]
    return cell_dictionary
