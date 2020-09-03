import setuptools

setuptools.setup(
    name="WSV_test-bruxy70",
    version="0.0.1",
    author="bruxy70",
    author_email="vaclav.chaloupka@gmail.com",
    description="Selenium test script for WSV",
    long_description="Selenium test script for WSV",
    url="https://github.com/bruxy70/WSV_test",
    packages=setuptools.find_packages(),
    install_requires=[
        'unittest',
        'parameterized',
        'selenium',
        'pyvirtualdisplay',
        'pymsteams',
        'yaml'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)