import pytest
import pyscores2.test
from pyscores2.runScores2 import Calculation

from pyscores2.indata import Indata


@pytest.fixture
def indata():
    the_indata = Indata()
    the_indata.open(pyscores2.test.indata_path)
    yield the_indata


@pytest.fixture
def calculation(tmpdir):
    outdata_directory = str(tmpdir)
    calculation = Calculation(outDataDirectory=outdata_directory)
    yield calculation


def test_run_from_file(calculation):
    calculation.run(indata_file_path=pyscores2.test.indata_path)


def test_run_from_indata(calculation, indata):
    calculation.run(indata=indata)

def test_run_from_indata2(calculation, indata):

    indata.waveDirectionIncrement = 12
    indata.waveDirectionMin = 2
    indata.waveDirectionMax = 24

    calculation.run(indata=indata)

def test_get_result_no_run(calculation):
    with pytest.raises(ValueError):
        calculation.getResult()

@pytest.mark.skip('This one does not work under python3.7')
def test_get_result(calculation):
    calculation.run(indata_file_path=pyscores2.test.indata_path)
    added_resistance_RAOs = calculation.getResult()
    errorCode, errorDescription = calculation.parse_error()
    a = 1

def test_output_file(calculation):
    calculation.run(indata_file_path=pyscores2.test.indata_path)

    from pyscores2.output import OutputFile
    output_file = OutputFile(filePath=calculation.outDataPath)
    speed = 10.0
    result_speed = output_file.results[speed]
    result_180 = result_speed[180]
    vertical_plane_responses= result_180.verticalPlaneResponses
    assert vertical_plane_responses.frequencies.size != 0
