from setuptools import find_packages, setup

package_name = 'object_follower'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='mbarnev3',
    maintainer_email='mbarnev3@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'find_object_node = object_follower.find_object_node:main',
            'rotate_robot_node = object_follower.rotate_robot_node:main'
        ],
    },
)
