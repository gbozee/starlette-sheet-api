from starlette.config import Config
from starlette.datastructures import Secret, URL

config = Config(".env")
DEBUG = config("DEBUG", cast=bool, default=True)
GOOGLE_PROJECT_ID = config("GOOGLE_PROJECT_ID")
GOOGLE_PRIVATE_KEY = config("GOOGLE_PRIVATE_KEY")
GOOGLE_PRIVATE_KEY_ID = config("GOOGLE_PRIVATE_KEY_ID")
GOOGLE_CLIENT_EMAIL = config("GOOGLE_CLIENT_EMAIL")
GOOGLE_CLIENT_ID = config("GOOGLE_CLIENT_ID")
OAUTH_SPREADSHEET = config("OAUTH_SPREADSHEET")
HOST_PROVIDER = config("HOST_PROVIDER")
OAUTH_SHEET_NAME = config("OAUTH_SHEET_NAME")
MEDIA_SHEET_NAME = config("MEDIA_SHEET_NAME")
MEDIA_SPREADSHEET = config("MEDIA_SPREADSHEET")
# IMAGE_SERVICES = {
#     "cloudinary": {
#         "cloud_name": config("CLOUDINARY_CLOUD_NAME"),
#         "api_key": config("CLOUDINARY_API_KEY"),
#         "api_secret": config("CLOUDINARY_API_SECRET"),
#     },
#     "imagekit": {
#         "cloud_name": config("IMAGEKIT_CLOUD_NAME"),
#         "api_key": config("IMAGEKIT_API_KEY"),
#         "api_secret": config("IMAGEKIT_API_SECRET"),
#     },
# }
