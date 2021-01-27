from setuptools import setup

setup(

    name = 'Flight Software',
    version = '1.0',
    description = 'IMU data acquisition module',
    author = 'Manuel da Costa Lindo',
    author_email = 'manuelcostalindo@gmail.com',
    url = 'https://github.com/dacostalindo/Telemetry-Collection-App',
    packages = setuptools.find_packages(),
    python_requires='>=3.8',
    install_requires = [
        sock, subprocess, struct,
    ]
)