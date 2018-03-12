from setuptools import setup, find_packages

setup(
    name="beampy",
    version="0.4.6",
    long_description=__doc__,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "beautifulsoup4",
        "pillow",
        "six",
        "lxml",
    ]
)
