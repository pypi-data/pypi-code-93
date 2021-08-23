from distutils.core import setup
setup(
    name = 'print_logger',
    packages = ['print_logger'],
    version = '1.0.0',
    license='MIT',
    description = 'Python print with strict structure',
    author = 'Huan Nguyen',
    author_email = 'nguyenxuanhuan.95@gmail.com',
    url = 'https://github.com/xuanhuan95/print_log',
    # download_url = 'https://github.com/xuanhuan95/dist/print_log-00',
    keywords = ['PYTHON', 'PRINT', 'LOGGING'],   # Keywords that define your package best
    install_requires=[],
    classifiers=[
        'Development Status :: 5 - Production/Stable',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.8', #Specify which python versions that you want to support
    ],
)