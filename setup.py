from setuptools import setup, find_packages

with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='aws-delete-all',
    version='0.5.42',
    author='Sinan Artun',
    author_email='sinanartun@gmail.com',
    description='A script that concurrently deletes common AWS resources like S3 buckets, RDS instances, and EC2 instances across all AWS regions.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/sinanartun/aws_delete_all',
    packages=find_packages(),
    py_modules=['main'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.9',
    install_requires=[
        'boto3>=1.34.139',
        'loguru',
        'pip>=24.1.1'
    ],
    entry_points={
        'console_scripts': [
            'aws-delete-all=main:main', 
        ],
    },
)
