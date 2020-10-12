import io

from setuptools import setup


def read_files(files):
    data = []
    for file in files:
        with io.open(file, encoding='utf-8') as f:
            data.append(f.read())
    return "\n".join(data)


long_description = read_files(['README.md', 'CHANGELOG.md'])

meta = {}

with io.open('./Butter/version.py', encoding='utf-8') as f:
    exec(f.read(), meta)

setup(
    name="Butter",
    description="Common library collection",
    long_description=long_description,
    long_description_content_type='text/markdown',
    version=meta['version'],
    author="ITJoker233",
    author_email="i@itjoker.cn",
    url="https://github.com/ITJoker233/butter",
    license='MIT',
    keywords=['butter'],
    packages=['butter','easy','quick','bot'],
    install_requires=[
        'requests >= 2.23.0',
        'opencv-python',
    ],
    entry_points='''
    ''',
    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GPL License 3.0',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
