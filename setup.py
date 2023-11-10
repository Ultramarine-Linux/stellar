from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name="umstellar",
    version="0.0.2",
    packages=find_packages(),
    entry_points={"console_scripts": []},
    install_requires=requirements,
    author="Cappy Ishihara",
    author_email="cappy@fyralabs.com",
    description="Ultramarine Quickstart Tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Ultramarine-Linux/umstellar",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GPLv3 License",
        "Operating System :: Linux :: Ultramarine",
    ],
)
