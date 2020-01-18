from setuptools import setup, find_packages

setup(
    name='irtools',
    version='1.0',
    description='Utilities for IR research',
    author='Binsheng Liu',
    author_email='liubinsheng@gmail.com',
    package_dir={"": "src"},
    scripts=["scripts/each_server.sh"],
    packages=find_packages("src"),
    include_package_data=True,
    install_requires=[
        'unidecode', 'tqdm', 'scipy', 'numpy', 'more_itertools', 'pandas'
    ],
)