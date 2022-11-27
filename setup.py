import os

import setuptools


files = [os.path.join("templates", "*.css"),
         os.path.join("templates", "*.html")]

setuptools.setup(
    name="pypline",
    version="0.1.0",
    author="Rafael DevOps",
    description="Utilities for pipelines",
    url="https://github.com/pypa/sampleproject",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir = {"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=["jinja2", "junit2html"],
    package_data={'build_mail': files},
    entry_points={
        'console_scripts': [
            'send-mail = build_mail.console:main',
        ]
    }
    
)