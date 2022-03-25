from setuptools import find_packages, setup
setup(
    name='dkhelpers',
    packages=find_packages(include=['dkhelpers']),
    version='0.1.33',
    description='My first Python library',
    author='Me',
    license='MIT',
    install_requires=[],
    setup_requires=['pytest-runner'],
    tests_require=['pytest==4.4.1'],
    test_suite='tests',
)
