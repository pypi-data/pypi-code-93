from setuptools import setup, find_packages

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
    'Programming Language :: Python :: 3.8',
    'Programming Language :: Python :: 3.9',
    'Programming Language :: Python :: 3.10'
]

setup(
    name='HandDetectorModule',
    version='0.0.1',
    description='This is a simplified version of mediapipe to do hand Detection',
    long_description=open('README.txt').read() + '\n\n' + open('CHANGELOG.txt').read(),
    url='',
    author='Saurabh Lanje',
    author_email='saurabhlanje33@gmail.com',
    license='MIT',
    classifiers=classifiers,
    keywords='hand, Computervision, HandTracking, HandDetection, Hand-Detection',
    packages=find_packages(),
    install_requires=['']
)
