from pathlib import Path

from setuptools import find_packages, setup

# Resolve paths relative to this file so the build works regardless of the
# current working directory (e.g. when setuptools re-invokes setup.py from
# inside an unpacked sdist tarball).
HERE = Path(__file__).parent.resolve()


def _read_long_description() -> str:
    for name in ("README.md", "readme.md"):
        candidate = HERE / name
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")
    return ""


setup(
    name='aws-delete-all',
    version='0.5.53',
    author='Sinan Artun',
    author_email='sinanartun@gmail.com',
    description='A script that concurrently deletes common AWS resources like S3 buckets, RDS instances, and EC2 instances across all AWS regions.',
    long_description=_read_long_description(),
    long_description_content_type="text/markdown",
    url='https://github.com/sinanartun/aws_delete_all',
    packages=find_packages(),
    py_modules=['main'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    license="MIT",
    license_files=["LICENSE"],
    python_requires='>=3.9',
    install_requires=[
        'boto3>=1.42.0,<2.0.0',
        'botocore>=1.42.0,<2.0.0',
        'loguru>=0.7.2,<1.0.0',
    ],
    entry_points={
        'console_scripts': [
            'aws-delete-all=main:main',
        ],
    },
)
