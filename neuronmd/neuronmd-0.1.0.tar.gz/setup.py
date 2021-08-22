from setuptools import setup

setup(
    name='neuronmd',
    version='0.1.0',
    description='Package for simulating spiking neuron models',
    url='https://github.com/sowmyamanojna/neuronmd',
    author='N Sowmya Manojna',
    author_email='sowmyamanojna@gmail.com',
    license='MIT',
    packages=['neuronmd'],
    install_requires=["numpy","scipy", "tqdm", "matplotlib", "imageio"],
    zip_safe=False
    )
