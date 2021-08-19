import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="btq",                                     
    version="0.0.1",                                       
    author="btq",                                       
    author_email="sakaiay_btq@163.com",                     
    description="extract feature",                            
    # long_description=long_description,                     
    # long_description_content_type="text/markdown",          
    url="http://pdc.yfish.x/",                              
    packages=setuptools.find_packages(),                    
    classifiers=[                                       
        "Programming Language :: Python :: 3",             
        "License :: OSI Approved :: MIT License",           
        "Operating System :: OS Independent",           
    ],
    install_requires=[], 
    python_requires='>=3'
)