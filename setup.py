from setuptools import setup, find_packages
import os

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
def read_requirements():
    requirements = []
    try:
        with open("requirements.txt", "r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith("#") and not line.startswith('"""'):
                    # Basic validation for package name
                    if line and line[0].isalnum():
                        requirements.append(line)
    except FileNotFoundError:
        print("Warning: requirements.txt not found, using empty requirements")
        return []
    return requirements

requirements = read_requirements()

setup(
    name="nllpy",
    version="0.1.0",
    author="Jay Wellik",
    author_email="jwellik@usgs.gov",
    description="Python wrapper for generating NonLinLoc control files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jwellik/nllpy",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Physics",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": ["pytest>=6.0", "black", "flake8", "mypy"],
        "obspy": ["obspy>=1.3.0"],
    },
    entry_points={
        "console_scripts": [
            "nllpy=nllpy.cli.main:main",
            "nll-gtsrce=nllpy.cli.main:gtsrce_command",
        ],
    },
    include_package_data=True,
    package_data={
        "nllpy": ["templates/data/*.template"],
    },
)