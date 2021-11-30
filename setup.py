import setuptools
from graphgenerator.version import __version__

# https://www.freecodecamp.org/news/build-your-first-python-package/

exec(open("graphgenerator/version.py").read())

setuptools.setup(
    name="social-networks-graph-generator",
    description="CLI tool to generate a graph from a hashtag or expression",
    version=__version__,
    author="Ambanum",
    url="https://github.com/ambanum/social-networks-graph-generator",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["graphgenerator"],
    setup_requires=["setuptools_scm"],
    use_scm_version=False,
    include_package_data=True,
    install_requires=[
        "setuptools-scm==6.3.2",
        "networkx==2.6.3",
        "pandas==1.2.5",
        "click==8.0.1",
        "pytz==2021.3",
        "matplotlib==3.5.0",
        "python-louvain==0.15",
        "snscrape @ git+https://github.com/JustAnotherArchivist/snscrape.git@a6b6f3faaa26f541d9469651451340096b5abc92#egg=snscrape"

    ],
    dependency_links=["git+https://github.com/JustAnotherArchivist/snscrape.git"],
    python_requires="~=3.8",
    extras_require={
        "test": ["coverage"],
    },
    entry_points={
        "console_scripts": [
            "graphgenerator=graphgenerator.cli:main",
        ],
    },
)
