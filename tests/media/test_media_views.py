import pytest
import httpx
from gsheet_service.views import app


@pytest.fixture
def client():
    return httpx.Client(app=app, base_url="http://test-server")


@pytest.mark.asyncio
async def test_get_cloudinary_image_when_not_exist(client: httpx.Client):
    response = await client.get(
        "/media/images",
        params={
            "url": "https://www.dropbox.com/s/l0yygsrxbxffxsl/Q1.jpg?raw=1",
            "provider": "cloudinary",
        },
    )
    assert response.status_code == 200 
    assert response.json == {
        'status':True,
        'data':
    }

