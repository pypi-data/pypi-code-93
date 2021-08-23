import logging
from random import randint
from typing import Literal

import numpy as np
import pytest
from astropy.io import fits
from dkist_header_validator import spec122_validator

from dkist_processing_common.models.constants import BudName
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.tasks.write_l1 import WriteL1Frame
from dkist_processing_common.tests.conftest import FakeGQLClient


class CompleteWriteL1Frame(WriteL1Frame):
    def add_dataset_headers(
        self, header: fits.Header, stokes: Literal["I", "Q", "U", "V"]
    ) -> fits.Header:
        header["DAAXES"] = 2
        header["DEAXES"] = 3
        header["DNAXIS"] = 5
        header["FRAMEWAV"] = 123.45
        header["LEVEL"] = 1
        header["WAVEMAX"] = 124
        header["WAVEMIN"] = 123
        header["WAVEREF"] = "Air"
        header["WAVEUNIT"] = -9
        header["DINDEX3"] = 3
        header["DINDEX4"] = 2
        header["DINDEX5"] = 1
        header["DNAXIS1"] = header["NAXIS1"]
        header["DNAXIS2"] = header["NAXIS2"]
        header["DNAXIS3"] = 10
        header["DNAXIS4"] = 1
        header["DNAXIS5"] = 4
        header["DPNAME1"] = ""
        header["DPNAME2"] = ""
        header["DPNAME3"] = ""
        header["DPNAME4"] = ""
        header["DPNAME5"] = ""
        header["DTYPE1"] = "SPATIAL"
        header["DTYPE2"] = "SPATIAL"
        header["DTYPE3"] = "TEMPORAL"
        header["DTYPE4"] = "SPECTRAL"
        header["DTYPE5"] = "STOKES"
        header["DUNIT1"] = ""
        header["DUNIT2"] = ""
        header["DUNIT3"] = ""
        header["DUNIT4"] = ""
        header["DUNIT5"] = ""
        header["DWNAME1"] = ""
        header["DWNAME2"] = ""
        header["DWNAME3"] = ""
        header["DWNAME4"] = ""
        header["DWNAME5"] = ""
        header["CALVERS"] = ""
        header["CAL_URL"] = ""
        header["HEADVERS"] = ""
        header["HEAD_URL"] = ""
        header["INFO_URL"] = ""

        return header


@pytest.fixture()
def calibrated_header():
    hdu = fits.PrimaryHDU(data=np.ones((1, 128, 128)))
    hdu.header["TELEVATN"] = 6.28
    hdu.header["TAZIMUTH"] = 3.14
    hdu.header["TTBLANGL"] = 1.23
    hdu.header["DATE-OBS"] = "2020-05-25T00:00:00.000"
    hdu.header["DKIST004"] = "observe"
    hdu.header["ID___004"] = "ip id"
    hdu.header["PAC__004"] = "Polarizer"
    hdu.header["PAC__005"] = 0
    hdu.header["PAC__006"] = "clear"
    hdu.header["PAC__007"] = 0
    hdu.header["PAC__008"] = "FieldStop (2.8arcmin)"
    hdu.header["INSTRUME"] = "VISP"
    hdu.header["LINEWAV"] = 1080.0
    hdu.header["DATE-BGN"] = "2020-03-13T00:00:00.000"
    hdu.header["DATE-END"] = "2021-08-15T00:00:00.000"
    hdu.header["ID___013"] = "PROPOSAL_ID1"
    hdu.header["ID___005"] = "id string"
    hdu.header["PAC__002"] = "clear"
    hdu.header["PAC__003"] = "on"
    hdu.header["TELSCAN"] = "Raster"
    hdu.header["DKIST008"] = 1
    hdu.header["DKIST009"] = 1
    hdu.header["BTYPE"] = ""
    hdu.header["BUNIT"] = ""
    hdu.header["CAMERA"] = ""
    hdu.header["CDELT1"] = 1
    hdu.header["CDELT2"] = 1
    hdu.header["CDELT3"] = 1
    hdu.header["CRPIX1"] = 0
    hdu.header["CRPIX2"] = 0
    hdu.header["CRPIX3"] = 0
    hdu.header["CRVAL1"] = 0
    hdu.header["CRVAL2"] = 0
    hdu.header["CRVAL3"] = 0
    hdu.header["CTYPE1"] = ""
    hdu.header["CTYPE2"] = ""
    hdu.header["CTYPE3"] = ""
    hdu.header["CUNIT1"] = ""
    hdu.header["CUNIT2"] = ""
    hdu.header["CUNIT3"] = ""
    hdu.header["DATE"] = "2021-08-20T00:00:00.000"
    hdu.header["DKIST003"] = "observe"
    hdu.header["DKISTVER"] = ""
    hdu.header["ID___012"] = ""
    hdu.header["CAM__002"] = ""
    hdu.header["CAM__004"] = 1
    hdu.header["CAM__005"] = 1
    hdu.header["CAM__014"] = 1
    hdu.header["FILE_ID"] = ""
    hdu.header["ID___001"] = ""
    hdu.header["ID___002"] = ""
    hdu.header["ID___008"] = ""
    hdu.header["NETWORK"] = "NSF-DKIST"
    hdu.header["OBJECT"] = "quietsun"
    hdu.header["OBSERVAT"] = "Haleakala High Altitude Observatory Site"
    hdu.header["OBSPR_ID"] = ""
    hdu.header["ORIGIN"] = "National Solar Observatory"
    hdu.header["TELESCOP"] = "Daniel K. Inouye Solar Telescope"
    hdu.header["WAVELNTH"] = 123.45
    hdu.header["WCSAXES"] = 3
    hdu.header["WCSNAME"] = ""
    hdu.header["PC1_1"] = 0
    hdu.header["PC1_2"] = 0
    hdu.header["PC1_3"] = 0
    hdu.header["PC2_1"] = 0
    hdu.header["PC2_2"] = 0
    hdu.header["PC2_3"] = 0
    hdu.header["PC3_1"] = 0
    hdu.header["PC3_2"] = 0
    hdu.header["PC3_3"] = 0
    hdu.header["CHECKSUM"] = ""
    hdu.header["DATASUM"] = ""
    hdu.header["NBIN"] = 1
    hdu.header["NBIN1"] = 1
    hdu.header["NBIN2"] = 1
    hdu.header["NBIN3"] = 1
    hdu.header["CAM__001"] = "cam string"
    hdu.header["CAM__003"] = 1
    hdu.header["CAM__006"] = 1
    hdu.header["CAM__007"] = 1
    hdu.header["CAM__008"] = 1
    hdu.header["CAM__009"] = 1
    hdu.header["CAM__010"] = 1
    hdu.header["CAM__011"] = 1
    hdu.header["CAM__012"] = 1
    hdu.header["CAM__013"] = 1
    hdu.header["CAM__015"] = 1
    hdu.header["CAM__016"] = 1
    hdu.header["CAM__017"] = 1
    hdu.header["CAM__018"] = 1
    hdu.header["CAM__019"] = 1
    hdu.header["CAM__020"] = 1
    hdu.header["CAM__033"] = 1
    hdu.header["CAM__034"] = 1
    hdu.header["CAM__035"] = 1
    hdu.header["CAM__036"] = 1
    hdu.header["CAM__037"] = 1
    hdu.header["DKIST001"] = "Auto"
    hdu.header["DKIST002"] = "Full"
    hdu.header["DKIST005"] = "id string"
    hdu.header["DKIST006"] = "Good"
    hdu.header["DKIST007"] = True
    hdu.header["DKIST010"] = 1
    hdu.header["ID___003"] = "id string"
    hdu.header["ID___006"] = "id string"
    hdu.header["ID___007"] = "id string"
    hdu.header["ID___009"] = "id string"
    hdu.header["ID___010"] = "id string"
    hdu.header["ID___011"] = "id string"
    hdu.header["ID___014"] = "id string"
    hdu.header["PAC__001"] = "open"
    hdu.header["PAC__009"] = "None"
    hdu.header["PAC__010"] = "closed"
    hdu.header["PAC__011"] = 0
    hdu.header["WS___001"] = "ws string"
    hdu.header["WS___002"] = 0
    hdu.header["WS___003"] = 0
    hdu.header["WS___004"] = 0
    hdu.header["WS___005"] = 0
    hdu.header["WS___006"] = 0
    hdu.header["WS___007"] = 0
    hdu.header["WS___008"] = 0

    return spec122_validator.validate_and_translate_to_214_l0(hdu.header, return_type=fits.HDUList)[
        0
    ].header


@pytest.fixture(scope="function", params=[1, 4])
def write_l1_task(calibrated_header, request):
    with CompleteWriteL1Frame(
        recipe_run_id=randint(0, 99999),
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        num_of_stokes_params = request.param
        stokes_params = ["I", "Q", "U", "V"]
        hdu = fits.PrimaryHDU(data=np.ones(shape=(128, 128)), header=calibrated_header)
        logging.info(f"{num_of_stokes_params=}")
        hdul = fits.HDUList([hdu])
        for i in range(num_of_stokes_params):
            task.fits_data_write(
                hdu_list=hdul,
                tags=[Tag.calibrated(), Tag.frame(), Tag.stokes(stokes_params[i])],
            )
        task.constants[BudName.average_cadence.value] = 10
        task.constants[BudName.minimum_cadence.value] = 10
        task.constants[BudName.maximum_cadence.value] = 10
        task.constants[BudName.variance_cadence.value] = 0
        yield task, num_of_stokes_params
        task.constants.purge()
        task.scratch.purge()


def test_write_l1_frame(write_l1_task, mocker):
    """
    :Given: a write L1 task
    :When: running the task
    :Then: no errors are raised
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    task, num_of_stokes_params = write_l1_task
    task()
    files = list(task.read(tags=[Tag.frame(), Tag.output()]))
    logging.info(f"{files=}")
    assert len(files) == num_of_stokes_params
    for file in files:
        logging.info(f"Checking file {file}")
        assert file.exists


def test_replace_header_values(write_l1_task, calibrated_header):
    """
    :Given: an input header
    :When: replacing specific header values
    :Then: the header values have changed
    """
    task, _ = write_l1_task
    original_file_id = calibrated_header["FILE_ID"]
    original_date = calibrated_header["DATE"]
    header = task._replace_header_values(header=calibrated_header)
    assert header["FILE_ID"] != original_file_id
    assert header["DATE"] != original_date


def test_l1_filename(write_l1_task, calibrated_header):
    """
    :Given: an input header
    :When: asking for the corresponding L1 filename
    :Then: the filename is formatted as expected
    """
    task, _ = write_l1_task
    assert (
        task.l1_filename(header=calibrated_header, stokes="Q")
        == "VISP_L1_01080000_2020_05_25T00_00_00_000_Q.fits"
    )


def test_calculate_date_avg(write_l1_task, calibrated_header):
    """
    :Given: an input header
    :When: finding the average date
    :Then: the correct datetime string is returned
    """
    task, _ = write_l1_task
    assert task._calculate_date_avg(header=calibrated_header) == "2021-01-03T12:00:00.000"


def test_calculate_telapse(write_l1_task, calibrated_header):
    """
    :Given: an input header
    :When: finding the time elapsed in an observation
    :Then: the correct time value is returned
    """
    task, _ = write_l1_task
    assert task._calculate_telapse(header=calibrated_header) == 38620800


def test_solarnet_keys(write_l1_task, mocker):
    """
    :Given: files with headers converted to SPEC 214 L1
    :When: checking the solarnet extra headers
    :Then: the correct values are found
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=FakeGQLClient
    )
    task, _ = write_l1_task
    task()
    files = list(task.read(tags=[Tag.frame(), Tag.output()]))
    logging.info(f"{files=}")
    for file in files:
        header = fits.open(file)[1].header
        assert header["DATEREF"] == header["DATE-BEG"]
        assert round(header["OBSGEO-X"]) == -5466045
        assert round(header["OBSGEO-Y"]) == -2404389
        assert round(header["OBSGEO-Z"]) == 2242134
        assert round(header["OBS_VR"]) == -144
        assert header["SPECSYS"] == "TOPOCENT"
        assert header["VELOSYS"] is False
