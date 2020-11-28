from setuptools import setup, find_packages

test_deps = ["brunette", "coverage", "flake8", "httmock", "tox"]

setup(
    name="mysocketctl",
    packages=find_packages(),
    # include_package_data=True,
    license="Apache Software License",
    version="0.7",
    description="CLI tool for mysocket.io",
    long_description=open("README.rst").read(),
    url="https://github.com/mysocketio/mysocketctl",
    author="Andree Toonk",
    author_email="andree@mysocket.io",
    install_requires=["Click", "requests", "pyjwt", "prettytable", "paramiko"],
    python_requires=">=3.6",
    extras_requires={
        "test": test_deps,
    },
    test_requires=test_deps,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    entry_points={"console_scripts": ["mysocketctl = mysocketctl.mysocketcli:cli"]},
)
