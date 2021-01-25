import re
import typing
import cloudinary
from cloudinary import uploader as cloudinary_uploader


class ResourceInstance:
    def build_url(self, **kwargs):
        raise NotImplementedError

    def save(self, **kwargs):
        raise NotImplementedError

    def delete(self, **kwargs):
        raise NotImplementedError


class CloudinaryInstance(ResourceInstance):
    kind = "cloudinary"

    def __init__(
        self,
        image: str = None,
        cloud_name=None,
        api_key=None,
        api_secret=None,
        upload=False,
        resource_type="image",
        **kwargs,
    ):
        self.auth = {
            "cloud_name": cloud_name,
            "api_key": api_key,
            "api_secret": api_secret,
        }
        cloudinary.config(**self.auth)
        self.uploaded = bool(image)
        self.image = image
        self.resource_type = resource_type
        if self.uploaded:
            self.instance = self.resource_options[resource_type](image)

    @property
    def resource_options(self):
        return {
            "image": cloudinary.CloudinaryImage,
            "video": cloudinary.CloudinaryVideo,
            "raw": cloudinary.CloudinaryResource,
        }

    @property
    def public_id(self):
        if self.instance:
            return self.instance.public_id

    def build_url(self, secure=True, **kwargs):
        if self.uploaded:
            return self.instance.build_url(
                secure=secure, resource_type=self.resource_type, **kwargs
            )

    def html(self, secure=True, **kwargs):
        if self.uploaded:
            return self.instance.video(secure=secure, **kwargs)

    def delete(self):
        if self.uploaded:
            cloudinary_uploader.destroy(
                self.public_id, invalidate=True, resource_type=self.resource_type
            )
            self.instance = None
            self.uploaded = False

    def save(
        self,
        file: bytes = None,
        url=None,
        file_name=None,
        folder=None,
        kind=None,
        resource_type="image",
        **kwargs,
    ):
        # func = cloudinary.uploader.upload_image
        new_file = file or url
        func = cloudinary_uploader.upload
        r_type = resource_type
        if self.resource_type:
            r_type = self.resource_type
        if not self.uploaded:
            result = func(
                new_file, public_id=file_name, folder=folder, resource_type=r_type
            )
            self.uploaded = True
            self.instance = self.resource_options[resource_type](result["public_id"])


def get_instance(key: str, **kwargs):
    options = {
        "cloudinary": CloudinaryInstance,
        # "imagekit": ImageKitInstance,
        # "url": YoutubeInstance,
    }
    return options[key](**kwargs)


SUPPORTED_TYPES = CloudinaryInstance
# SUPPORTED_TYPES = typing.Union[CloudinaryInstance, ImageKitInstance]


class VideoAudioServiceAPI:
    pass


class MediaServiceAPI:
    def __init__(self, config, folder="", resource_type="image"):
        self.config = config
        self.folder = folder
        self.resource_type = resource_type

    def switch_provider(self, public_id, from_=None, to=None):
        from_instance = get_instance(from_, image=public_id, **self.config[from_])
        to_instance = get_instance(to, **self.config[to])
        to_instance.save(
            url=from_instance.build_url(),
            file_name=from_instance.public_id.replace(f"/{self.folder}/", ""),
            folder=self.folder,
            kind="url",
        )
        from_instance.delete()
        return to_instance

    @classmethod
    def create_resource(
        cls, image, service=None, media_instance: SUPPORTED_TYPES = None, **kwargs
    ):
        config = kwargs.get("config")
        # config = settings.IMAGE_SERVICES[service]
        if media_instance:
            instance = media_instance
            service = instance.kind
        else:
            new_service = service
            if not new_service:
                new_service = config.get("client")
            instance: SUPPORTED_TYPES = get_instance(
                new_service, resource_type=kwargs.get("resource_type"), **config
            )
            instance.save(image, **kwargs)
        return dict(
            service=service,
            resource_id=instance.public_id,
            kind=kwargs.get("resource_type"),
        )

    @classmethod
    def get_instance(cls, service=None, resource_id=None, kind="image", config=None):
        new_service = service
        if not new_service:
            new_service = config.get("client")
        instance = get_instance(
            new_service, image=resource_id, resource_type=kind, **config
        )
        return instance

    @classmethod
    async def update_resource(
        cls,
        image,
        media_instance=None,
        service=None,
        old_service=None,
        resource_id=None,
        **kwargs,
    ):
        config = settings.IMAGE_SERVICES[old_service]
        instance = get_instance(old_service, image=resource_id, **config)
        if image:
            instance.delete()
            config = settings.IMAGE_SERVICES[service]
            instance = get_instance(
                service, resource_type=kwargs.get("resource_type"), **config
            )
            instance.save(image, **kwargs)
        else:
            instance = media_instance
        return {"service": instance.kind, "resource_id": instance.public_id}

    @classmethod
    async def delete_resource(cls, service=None, resource_id=None, **kwargs):
        config = kwargs.get("config")
        new_service = service
        if not new_service:
            new_service = config.get("client")
        # config = settings.IMAGE_SERVICES[service]
        instance = get_instance(new_service, image=resource_id, **config, **kwargs)
        instance.delete()
