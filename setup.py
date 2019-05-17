from setuptools import setup, find_packages

from beampy import __version__ as beampy_version

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
    name="beampy-slideshow",
    version=beampy_version,
    author="Hugo Chauvet",
    author_email="hugo.chauvet@protonmail.com",
    long_description=long_description,
    description="A python tool to create simple HTML5 presentation slideshow",
    long_description_content_type="text/markdown",
    url="https://github.com/hchauvet/beampy",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "beautifulsoup4",
        "pillow",
        "six",
        "lxml",
    ],
    classifiers=[
        'Programming Language :: Python :: 2 ',
        'Programming Language :: Python :: 3 ',
        'Topic :: Multimedia :: Graphics :: Presentation',
        'Topic :: Multimedia :: Graphics :: Editors :: Vector-Based ',
        'Topic :: Text Processing :: Markup :: LaTeX',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Text Processing',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
    ]
)
