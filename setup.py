from setuptools import setup

setup(
    version='0.1.0',
    name='chaino',
    description="chaino",
    packages=[
        'chaino',
    ],
    scripts=[
        'bin/blockchain.py'
    ],
    include_package_data=True,
    keywords='',
    author='0xidm',
    author_email='0xidm@protonmail.com',
    url='https://linktr.ee/0xidm',
    install_requires=[
        "web3==5.28.0",
        "multicall",
        "python-dotenv",
        "pandas",
        "click",
        "rich",
    ],
    extras_require={
        "dev": [
            "pytest",
            "pdbpp",
            "mypy",
            "pylint",
            "ipython",
        ],
        "docs": [
            "sphinx",
            "sphinx_rtd_theme",
        ]
    },
    license='MIT',
    zip_safe=True,
)
