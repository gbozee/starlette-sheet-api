import os
import base64
import pytest
from media_service import settings, utils

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

image_file = os.path.join(BASE_DIR, "sample_img.png")


def create_cloudinary_image(file_name="media_test_image"):
    config = settings.IMAGE_SERVICES["cloudinary"]
    instance = utils.get_instance("cloudinary", **config)
    instance.save(image_file, public_id=file_name)
    return instance


def create_imagekit_image(file_name="media_test_image", folder="media"):
    config = settings.IMAGE_SERVICES["imagekit"]
    # create new file
    instance = utils.get_instance("imagekit", **config)
    with open(image_file, "rb") as ff:
        img = base64.b64encode(ff.read())
    instance.save(img, file_name=file_name, folder=folder)
    return instance


def test_create_cloudinary_image_file():
    # create new file
    config = settings.IMAGE_SERVICES["cloudinary"]
    instance = utils.get_instance("cloudinary", **config)
    assert not instance.uploaded
    instance.save(image_file, file_name="media_test_image")
    assert instance.uploaded
    assert instance.public_id == "media_test_image"
    # test build url
    url = instance.build_url(width=40, height=40, format="jpg", secure=True)
    assert (
        url
        == f"https://res.cloudinary.com/{config['cloud_name']}/image/upload/h_40,w_40/media_test_image.jpg"
    )
    # delete image
    instance.delete()
    assert not instance.uploaded


def test_create_cloudinary_image_b64_file():
    # create new file
    config = settings.IMAGE_SERVICES["cloudinary"]
    instance = utils.get_instance("cloudinary", **config)
    assert not instance.uploaded
    with open(image_file, "rb") as ff:
        img = base64.b64encode(ff.read())
    instance.save(b"data:image/png;base64," + img, file_name="media_test_image")
    assert instance.uploaded
    assert instance.public_id == "media_test_image"
    # test build url
    url = instance.build_url(width=40, height=40, format="jpg", secure=True)
    assert (
        url
        == f"https://res.cloudinary.com/{config['cloud_name']}/image/upload/h_40,w_40/media_test_image.jpg"
    )
    # delete image
    instance.delete()
    assert not instance.uploaded


def test_imagekit_image_file():
    config = settings.IMAGE_SERVICES["imagekit"]
    # create new file
    instance = utils.get_instance("imagekit", **config)
    assert not instance.uploaded
    assert not instance.public_id
    with open(image_file, "rb") as ff:
        img = base64.b64encode(ff.read())
    instance.save(img, file_name="media_test_image", folder="tests")
    assert instance.uploaded
    assert "tests/media_test_image" in instance.public_id

    # test build url
    url = instance.build_url(width=40, height=40, format="jpg")
    assert (
        url
        == f"https://ik.imagekit.io/{config['cloud_name']}/tr:f-jpg,h-40,w-40/{instance.public_id}"
    )
    # delete image
    instance.delete()
    assert not instance.uploaded
    assert not instance.public_id


def test_transfer_from_cloudinary_to_imagekit():
    cloud_id = create_cloudinary_image()
    public_id = cloud_id.public_id
    image_service = utils.MediaServiceAPI(settings.IMAGE_SERVICES, folder="media")
    # create image instance in imagekit
    imagekit_instance = image_service.switch_provider(
        cloud_id.public_id, from_="cloudinary", to="imagekit"
    )
    assert imagekit_instance.uploaded
    assert f"media/{public_id}" in imagekit_instance.public_id
    # delete imagekit
    imagekit_instance.delete()
    assert not imagekit_instance.uploaded
    assert not imagekit_instance.public_id


def test_transfer_from_image_kit_to_cloudinary():
    cld = create_imagekit_image()
    public_id = cld.public_id
    image_service = utils.MediaServiceAPI(settings.IMAGE_SERVICES, folder="media")
    # create image instance in imagekit
    cloudinary_instance = image_service.switch_provider(
        cld.public_id, from_="imagekit", to="cloudinary"
    )
    assert cloudinary_instance.uploaded
    assert cloudinary_instance.public_id in public_id
    # delete imagekit
    cloudinary_instance.delete()
    assert not cloudinary_instance.uploaded
    assert not cloudinary_instance.public_id

