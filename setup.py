from os.path import join, dirname, abspath
from setuptools import setup, Extension
from Cython.Build import cythonize


directory_path = dirname(abspath(__file__))


ext_data = {
    'aktarai.*': {
        'sources': [join(directory_path, 'aktarai', '*.py')]},

    'aktarai.detection.*': {
        'sources': [join(directory_path, 'aktarai', 'detection', '*.py')]},
    'aktarai.detection.utils.*': {
        'sources': [join(directory_path, 'aktarai', 'detection', 'utils', '*.py')]},

    'aktarai.recognition.*': {
        'sources': [join(directory_path, 'aktarai', 'recognition', '*.py')]},
    'aktarai.recognition.utils.*': {
        'sources': [join(directory_path, 'aktarai', 'recognition', 'utils', '*.py')]},

    'aktarai.mapping.*': {
        'sources': [join(directory_path, 'aktarai', 'mapping', '*.py')]},

    'aktarai.streaming.*': {
        'sources': [join(directory_path, 'aktarai', 'streaming', '*.py')]},

    'aktarai.tracking.*': {
        'sources': [join(directory_path, 'aktarai', 'tracking', '*.py')]},
    'aktarai.tracking.utils.*': {
        'sources': [join(directory_path, 'aktarai', 'tracking', 'utils', '*.py')]},
        }


extensions = []

for name, data in ext_data.items():

    sources = data['sources']
    include = data.get('include', [])

    obj = Extension(
        name,
        sources=sources,
        include_dirs=include
    )

    extensions.append(obj)


# Use cythonize on the extension object.
setup(
    name='aktarai',
    version='0.2.0',
    author='Mostafa Moradipour',
    ext_modules=cythonize(extensions))
