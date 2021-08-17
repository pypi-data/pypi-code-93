from setuptools import setup, find_packages
import subprocess

git_command_result: subprocess.CompletedProcess = subprocess.run(
    ["git", "describe", "--tags"], capture_output=True, encoding="utf-8"
)
actual_version: str = git_command_result.stdout.strip("\n")

setup(
    name="asteriskrealtimedata",
    version=actual_version,
    packages=find_packages(),
    author="Juares Vermelho Diaz (CL3k)",
    author_email="jvermelho@cl3k.com",
    description="API for manage realtime data about asterisk status",
    keywords="Asterisk realtime ",
    install_requires=["antidote==1.0.0", "fastrlock==0.5", "pymongo==3.12.0"],
)
