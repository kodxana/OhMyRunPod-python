from setuptools import setup, find_packages
import os

with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='OhMyRunPod',
    version='0.2.4',
    author='Madiator2011',
    author_email='admin@madiator.com',
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_data={
        'OhMyRunPod': [
            'modules/ssh_setup/*.sh',
            'modules/tailscale_setup/*.sh'
        ],
    },
    entry_points={
        'console_scripts': [
            'OhMyRunPod=OhMyRunPod.main:main',
        ],
    },
)
