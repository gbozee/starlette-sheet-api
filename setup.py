import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), "README.md")) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name="now_sheet_app",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    license="MIT License",  # example license
    description="Utility library that does a lot of things",
    long_description=README,
    url="https://www.example.com/",
    author="Bee sama",
    author_email="b33sama@gmail.com",
    install_requires=[
        # 'asgiref>=2.3.2',
        # 'starlette>=0.8.8',
        # 'uvicorn>=0.3.13',
        # "sentry-asgi>=0.1.5",
        # 'python-multipart>=0.0.5',
        # # 'graphene_utils @ https://github.com/gbozee/graphene-utils/archive/master.zip',
        # 'graphene_utils @ git+https://github.com/gbozee/graphene-utils@master',
        # 'django-paystack @ git+https://github.com/gbozee/django-paystack@master'
    ],
    dependency_links=[],
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: X.Y",  # replace "X.Y" as appropriate
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",  # example license
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        # Replace these appropriately if you are stuck on Python 2.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
