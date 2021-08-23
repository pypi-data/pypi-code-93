from pollination_dsl.dag import Inputs, DAG, task, Outputs
from dataclasses import dataclass
from pollination.honeybee_radiance.sky import GenSky, AdjustSkyForMetric
from pollination.honeybee_radiance.octree import CreateOctreeWithSky
from pollination.honeybee_radiance.translate import CreateRadianceFolderView

# input/output alias
from pollination.alias.inputs.model import hbjson_model_view_input
from pollination.alias.inputs.pit import point_in_time_view_metric_input
from pollination.alias.inputs.radiancepar import rad_par_view_input
from pollination.alias.inputs.bool_options import skip_overture_input
from pollination.alias.outputs.daylight import point_in_time_view_results

from ._raytracing import PointInTimeViewRayTracing


@dataclass
class PointInTimeViewEntryPoint(DAG):
    """Point-in-time View-based entry point."""

    # inputs
    model = Inputs.file(
        description='A Honeybee model in HBJSON file format.',
        extensions=['json', 'hbjson', 'pkl', 'hbplk'],
        alias=hbjson_model_view_input
    )

    sky = Inputs.str(
        description='Sky string for any type of sky (cie, climate-based, irradiance, '
        'illuminance). This can be a minimal representation of the sky through '
        'altitude and azimuth (eg. "cie -alt 71.6 -az 185.2 -type 0"). Or it can be '
        'a detailed specification of time and location (eg. "climate-based 21 Jun 12:00 '
        '-lat 41.78 -lon -87.75 -tz 5 -dni 800 -dhi 120"). Both the altitude and '
        'azimuth must be specified for the minimal representation to be used. See the '
        'honeybee-radiance sky CLI group for a full list of options '
        '(https://www.ladybug.tools/honeybee-radiance/docs/cli/sky.html).'
    )

    metric = Inputs.str(
        description='Text for the type of metric to be output from the calculation. '
        'Choose from: illuminance, irradiance, luminance, radiance.',
        default='luminance', alias=point_in_time_view_metric_input,
        spec={'type': 'string',
              'enum': ['illuminance', 'irradiance', 'luminance', 'radiance']},
    )

    resolution = Inputs.int(
        description='An integer for the maximum dimension of each image in pixels '
        '(either width or height depending on the input view angle and type).',
        spec={'type': 'integer', 'minimum': 1}, default=800
    )

    view_filter = Inputs.str(
        description='Text for a view identifer or a pattern to filter the views '
        'of the model that are simulated. For instance, first_floor_* will simulate '
        'only the views that have an identifier that starts with first_floor_. By '
        'default, all views in the model will be simulated.',
        default='*'
    )

    skip_overture = Inputs.str(
        description='A switch to note whether an ambient file (.amb) should be '
        'generated for an overture calculation before the view is split into smaller '
        'views. With an overture calculation, the ambient file (aka ambient cache) is '
        'first populated with values. Thereby ensuring that - when reused to create '
        'an image - Radiance uses interpolation between already calculated values '
        'rather than less reliable extrapolation. The overture calculation has '
        'comparatively small computation time to full rendering but is single-core '
        'can become time consuming in situations with very high numbers of '
        'rendering multiprocessors.', default='overture', alias=skip_overture_input,
        spec={'type': 'string', 'enum': ['overture', 'skip-overture']}
    )

    view_count = Inputs.int(
        description='Number of views into which each Model view will be subdivided '
        'for parallelized calculation.', default=2,
        spec={'type': 'integer', 'minimum': 1}
    )

    radiance_parameters = Inputs.str(
        description='The radiance parameters for ray tracing',
        default='-ab 2 -aa 0.25 -ad 512 -ar 16',
        alias=rad_par_view_input
    )

    @task(template=GenSky)
    def generate_sky(self, sky_string=sky):
        return [
            {
                'from': GenSky()._outputs.sky,
                'to': 'resources/weather.sky'
            }
        ]

    @task(
        template=AdjustSkyForMetric,
        needs=[generate_sky]
    )
    def adjust_sky(self, sky=generate_sky._outputs.sky, metric=metric):
        return [
            {
                'from': AdjustSkyForMetric()._outputs.adjusted_sky,
                'to': 'resources/weather.sky'
            }
        ]

    @task(template=CreateRadianceFolderView)
    def create_rad_folder(
        self, input_model=model, view_filter=view_filter
            ):
        """Translate the input model to a radiance folder."""
        return [
            {
                'from': CreateRadianceFolderView()._outputs.model_folder,
                'to': 'model'
            },
            {
                'from': CreateRadianceFolderView()._outputs.bsdf_folder,
                'to': 'model/bsdf'
            },
            {
                'from': CreateRadianceFolderView()._outputs.views_file,
                'to': 'results/views_info.json'
            },
            {
                'from': CreateRadianceFolderView()._outputs.views,
                'description': 'View information.'
            }
        ]

    @task(
        template=CreateOctreeWithSky, needs=[adjust_sky, create_rad_folder]
    )
    def create_octree(
        self, model=create_rad_folder._outputs.model_folder,
        sky=adjust_sky._outputs.adjusted_sky
    ):
        """Create octree from radiance folder and sky."""
        return [
            {
                'from': CreateOctreeWithSky()._outputs.scene_file,
                'to': 'resources/scene.oct'
            }
        ]

    @task(
        template=PointInTimeViewRayTracing,
        needs=[create_rad_folder, create_octree],
        loop=create_rad_folder._outputs.views,
        sub_folder='initial_results/{{item.name}}',  # create a subfolder for each view
        sub_paths={'view': 'view/{{item.full_id}}.vf'}  # subpath for view
    )
    def point_in_time_view_ray_tracing(
        self, metric=metric, resolution=resolution, skip_overture=skip_overture,
        radiance_parameters=radiance_parameters, view_count=view_count,
        octree_file=create_octree._outputs.scene_file,
        view_name='{{item.full_id}}',
        view=create_rad_folder._outputs.model_folder,
        bsdfs=create_rad_folder._outputs.bsdf_folder
    ):
        # this task doesn't return a file for each loop.
        # instead we access the results folder directly as an output
        pass

    results = Outputs.folder(
        source='results', description='Folder with raw image files (.HDR) that contain '
        'images for each view.', alias=point_in_time_view_results
    )
