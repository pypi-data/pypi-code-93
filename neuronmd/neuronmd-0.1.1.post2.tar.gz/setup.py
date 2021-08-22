from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='neuronmd',
    version='0.1.1.post2',
    description='Package for simulating spiking neuron models',
    long_description = long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/sowmyamanojna/neuronmd',
    project_urls={
        "Bug Tracker": "https://github.com/sowmyamanojna/neuronmd/issues",
    },
    author='N Sowmya Manojna',
    author_email='sowmyamanojna@gmail.com',
    license='MIT',
    packages=['neuronmd'],
    install_requires=["numpy","scipy", "tqdm", "matplotlib", "imageio"],
    zip_safe=False
    )
