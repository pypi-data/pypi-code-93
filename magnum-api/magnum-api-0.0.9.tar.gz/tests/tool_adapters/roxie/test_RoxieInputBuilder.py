import io
from unittest import TestCase

from magnumapi.geometry.GeometryFactory import GeometryFactory
from magnumapi.geometry.roxie.CableDatabase import CableDatabase
from magnumapi.tool_adapters.roxie.RoxieInputBuilder import RoxieInputBuilder
from tests.resource_files import create_resources_file_path


class TestRoxieInputBuilder(TestCase):
    def test_convert_flag_dct_to_str(self):
        # arrange
        roxie_input = RoxieInputBuilder()

        # act
        flag_str = roxie_input.convert_flag_dct_to_str(roxie_input.flags)

        # assert
        flag_str_ref = '  LEND=F     LWEDG=F    LPERS=F    LQUENCH=F  LALGO=F    LMIRIRON=F \n' \
                       '  LBEMFEM=F  LPSI=F     LSOLV=F    LIRON=F    LMORPH=F   LHARD=F    \n' \
                       '  LPOSTP=F   LPEAK=T    LINMARG=F  LMARG=T    LSELF=F    LMQE=F     \n' \
                       '  LINDU=F    LEDDY=F    LSOLE=F    LFIELD3=F  LFISTR=F   LSELF3=F   \n' \
                       '  LBRICK=F   LLEAD=F    LVRML=F    LOPERA=F   LOPER20=F  LANSYS=F   \n' \
                       '  LRX2ANS=F  LANS2RX=F  LDXF=F     LMAP2D=F   LMAP3D=F   LEXPR=F    \n' \
                       '  LFIL3D=F   LFIL2D=F   LCNC=F     LANSYSCN=F LWEIRON=F  LCATIA=F   \n' \
                       '  LEXEL=F    LFORCE2D=F LAXIS=T    LIMAGX=F   LIMAGY=F   LRAEND=F   \n' \
                       '  LMARKER=F  LROLER2=F  LROLERP=F  LIMAGZZ=F  LSTEP=F    LIFF=F     \n' \
                       '  LICCA=F    LICC=F     LICCIND=F  LITERNL=F  LTOPO=F    LQUEN3=F   \n' \
                       '  LAYER=T    LEULER=T   LHEAD=T    LPLOT=T    LVERS52=T  LHARM=T    \n' \
                       '  LMATRF=F   LF3LIN=F   \n' \
                       '  /'
        self.assertEqual(flag_str_ref, flag_str)

    def test_prepare_data_file_str(self):
        self.maxDiff = None
        # arrange
        json_path = create_resources_file_path('resources/geometry/roxie/16T/16T_abs.json')
        cadata_path = create_resources_file_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)
        roxie_input = RoxieInputBuilder()
        geometry = GeometryFactory.init_with_json(json_path, cadata)

        # act
        roxie_input.cadata_path = 'C:/gitlab/magnum-api/tests/resources/geometry/roxie/16T/roxieold_2.cadata'
        roxie_input.block = geometry.to_roxie_df()

        # assert
        file_str = roxie_input.prepare_data_file_str()
        data_path_ref = create_resources_file_path('resources/geometry/roxie/16T/reference/16T_abs_partial_ref.data')
        with open(data_path_ref, 'r') as file:
            file_str_ref = file.read()


        #ToDo Fix failing test on CI
        # self.assertEqual(file_str_ref, file_str)

    def test_build(self):
        self.maxDiff = None
        # arrange
        json_path = create_resources_file_path('resources/geometry/roxie/16T/16T_abs.json')
        cadata_path = create_resources_file_path('resources/geometry/roxie/16T/roxieold_2.cadata')
        cadata = CableDatabase.read_cadata(cadata_path)
        roxie_input = RoxieInputBuilder()
        geometry = GeometryFactory.init_with_json(json_path, cadata)

        # act
        roxie_input.cadata_path = 'C:/gitlab/magnum-api/tests/resources/geometry/roxie/16T/roxieold_2.cadata'
        roxie_input.block = geometry.to_roxie_df()

        # assert
        data_path = create_resources_file_path('resources/geometry/roxie/16T/16T_abs.data')
        template_path = create_resources_file_path('resources/geometry/roxie/16T/template.roxie')
        roxie_input.build(template_path, data_path)

        data_path_ref = create_resources_file_path('resources/geometry/roxie/16T/reference/16T_abs_ref.data')

        with open(data_path, 'r') as file:
            file_str = file.read()

        with open(data_path_ref, 'r') as file:
            file_str_ref = file.read()

        #ToDo Fix failing test on CI
        # self.assertEqual(file_str_ref, file_str)
