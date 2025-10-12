import os
from glob import glob
from setuptools import setup

package_name = 'fleet_adapter_invisibot'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name,['config.yaml']),
        (os.path.join('share', package_name, 'launch'), glob(os.path.join('launch', '*launch.[pxy][yma]*'))),

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Gary Bey',
    maintainer_email='beyhy94@gmail.com',
    description='A RMF fleet adapter for invisibot, a virtual robot',
    license='Apache License 2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'fleet_adapter=fleet_adapter_invisibot.fleet_adapter:main'
        ],
    },
)
