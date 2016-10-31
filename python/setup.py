from setuptools import setup

setup(
    name='pack64',
    version = '2.0.0',
    maintainer='Luminoso Technologies, Inc.',
    maintainer_email='info@luminoso.com',
    url = 'http://github.com/LuminosoInsight/pack64',
    license = 'MIT',
    platforms = ['any'],
    description = 'A library for representing floating point vectors in a compact, base64-like format',
    py_modules=['pack64'],
    install_requires=['numpy >= 1.9.0'],
)
