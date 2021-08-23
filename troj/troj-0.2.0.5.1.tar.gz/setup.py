from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="troj",
    version="0.2.0.5.1",
    packages=find_packages(),
    author="TrojAI",
    author_email="stan.petley@troj.ai",
    description="TrojAI provides the troj Python convenience package to allow users to integrate TrojAI adversarial protections and robustness metrics seamlessly into their AI development pipelines.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://troj.ai",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "torch>=1.6.0",
        "tensorflow>=2.0.0",
        "requests",
        "urllib3",
        "adversarial-robustness-toolbox==1.7.0",
        "opencv-python",
        "torchvision",
    ],
    python_requires=">=3.6",
    extras_require={
        "dev": [
            "pytest>=6.2",
        ],
    },

)
