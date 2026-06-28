from setuptools import setup, find_packages

package_name = 'settings_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='your_email',
    description='Settings package',
    license='Apache License 2.0',
    entry_points={
        'console_scripts': [
            'settings_node = settings_pkg.setting_node:main',
             'permission_monitor_node = settings_pkg.permission_monitor_node:main',
        ],
    },
)

