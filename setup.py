
from setuptools import setup, find_packages

setup(
    name='umstellar',
    version='0.1',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'ultramarine-stellar-setup=umstellar.__main__:main'
        ]
    },
    install_requires=[
        # 'PyGObject',
        'requests'# add any required dependencies here
    ],
    author='Cappy Ishihara',
    author_email='your.email@example.com',
    description='A short description of your package',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/yourusername/umstellar',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GPLv3 License',
        'Operating System :: OS Independent',
    ],
)
