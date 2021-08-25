import subprocess
import pytest
def run_test_script(name):
    # os.chdir()
    p=subprocess.Popen(["python","tests/{}".format(name)])
    (stdout, stderr) = p.communicate()
    assert p.returncode ==0, stderr
    # print(stderr)

names=["demo.py",
"play_gym.py",
"play_gym_pend.py",
"play_gym_atari.py",
"play_gym_reach.py",]


@pytest.mark.parametrize("name", names)
def test_script(name):
    print(name)
    run_test_script(name)