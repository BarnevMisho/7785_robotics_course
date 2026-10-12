from setuptools import find_packages, setup

package_name = 'team47_chase_object'

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
    maintainer_email='mihail.barnev@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'detect_object = team47_chase_object.detect_object:main',
            'get_object_range = team47_chase_object.get_object_range:main',
            'chase_object = team47_chase_object.chase_object:main'
        ],
    },
)
