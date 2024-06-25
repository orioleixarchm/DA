from setuptools import setup, find_packages

setup(
    name='your_project_name',
    version='0.1',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    include_package_data=True,
    install_requires=[
        'altair==5.3.0',
        'asttokens==2.4.1',
        'attrs==23.2.0',
        'beautifulsoup4==4.12.3',
        'blinker==1.8.2',
        'branca==0.7.2',
        'cachetools==5.3.3',
        'cattrs==23.2.3',
        'certifi==2024.2.2',
        'charset-normalizer==3.3.2',
        'click==8.1.7',
        'colorama==0.4.6',
        'contourpy==1.2.1',
        'cycler==0.12.1',
        'decorator==5.1.1',
        'et-xmlfile==1.1.0',
        'executing==2.0.1',
        'filelock==3.15.0',
        'folium==0.17.0',
        'fonttools==4.53.0',
        'gdown==5.2.0',
        'geographiclib==2.0',
        'geopy==2.4.1',
        'gitdb==4.0.11',
        'GitPython==3.1.43',
        'idna==3.7',
        'ipython==8.25.0',
        'jedi==0.19.1',
        'Jinja2==3.1.4',
        'joblib==1.4.2',
        'jsonschema==4.22.0',
        'jsonschema-specifications==2023.12.1',
        'kiwisolver==1.4.5',
        'markdown-it-py==3.0.0',
        'MarkupSafe==2.1.5',
        'matplotlib==3.9.0',
        'matplotlib-inline==0.1.7',
        'mdurl==0.1.2',
        'numpy==1.26.4',
        'openpyxl==3.1.3',
        'packaging==24.0',
        'pandas==2.2.2',
        'parso==0.8.4',
        'patsy==0.5.6',
        'pillow==10.3.0',
        'pivottablejs==0.9.0',
        'platformdirs==4.2.2',
        'prompt_toolkit==3.0.47',
        'protobuf==5.27.1',
        'psutil==6.0.0',
        'pure-eval==0.2.2',
        'pyarrow==16.1.0',
        'pydeck==0.9.1',
        'Pygments==2.18.0',
        'pyparsing==3.1.2',
        'PySocks==1.7.1',
        'python-dateutil==2.9.0.post0',
        'pytz==2024.1',
        'ratelimiter==1.2.0.post0',
        'referencing==0.35.1',
        'requests==2.32.3',
        'requests-cache==1.2.1',
        'rich==13.7.1',
        'rpds-py==0.18.1',
        'scikit-learn==1.5.0',
        'scipy==1.13.1',
        'seaborn==0.13.2',
        'shapely==2.0.4',
        'six==1.16.0',
        'smmap==5.0.1',
        'soupsieve==2.5',
        'stack-data==0.6.3',
        'statsmodels==0.14.2',
        'streamlit==1.36.0',
        'tenacity==8.4.1',
        'threadpoolctl==3.5.0',
        'toml==0.10.2',
        'toolz==0.12.1',
        'tornado==6.4.1',
        'tqdm==4.66.4',
        'traitlets==5.14.3',
        'typing_extensions==4.12.2',
        'tzdata==2024.1',
        'url-normalize==1.4.3',
        'urllib3==2.2.1',
        'watchdog==4.0.1',
        'wcwidth==0.2.13',
        'xyzservices==2024.6.0'
    ],
    entry_points={
        'console_scripts': [
            'run-app=run_app:main',  # This creates a command 'run-app' that runs the 'main' function from 'run_app.py'
        ],
    },
    author='Your Name',
    author_email='your.email@example.com',
    description='A brief description of your project',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/orioleixarchm/DA',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
