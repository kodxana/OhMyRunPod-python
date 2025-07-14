from setuptools import setup, find_packages
import os

with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='OhMyRunPod',
    version='0.6.1',
    author='Madiator2011',
    author_email='admin@madiator.com',
    packages=find_packages(),
    include_package_data=True,
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=[
        'rich>=13.0.0',
    ],
    entry_points={
        'console_scripts': [
            'OhMyRunPod=OhMyRunPod.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: System :: Systems Administration',
        'Topic :: Utilities',
    ],
    python_requires='>=3.7',
)
