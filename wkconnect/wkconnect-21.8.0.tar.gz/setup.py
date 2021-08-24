# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['wkconnect',
 'wkconnect.backends',
 'wkconnect.backends.boss',
 'wkconnect.backends.neuroglancer',
 'wkconnect.backends.tiff',
 'wkconnect.backends.wkw',
 'wkconnect.routes',
 'wkconnect.routes.datasets',
 'wkconnect.utils',
 'wkconnect.webknossos']

package_data = \
{'': ['*']}

install_requires = \
['Pillow>=6.2,<7.0',
 'aiohttp>=3.7,<4.0',
 'async-lru>=1.0,<2.0',
 'blosc>=1.10,<2.0',
 'brotlipy>=0.7.0,<0.8.0',
 'compressed_segmentation>=1.0,<2.0',
 'gcloud-aio-auth>=3.0,<4.0',
 'jpeg4py>=0.1.4,<0.2.0',
 'numpy>=1.17,<2.0',
 'sanic==21.3.4',
 'sanic_cors>=1.0.0,<2.0.0',
 'tifffile>=2020.9.3,<2021.0.0',
 'wkcuber>=0.5,<0.6']

setup_kwargs = {
    'name': 'wkconnect',
    'version': '21.8.0',
    'description': '',
    'long_description': '# webknossos-connect\nA [webKnossos](https://github.com/scalableminds/webknossos) compatible data connector written in Python.\n\nwebKnossos-connect serves as an adapter between the webKnossos data store interface and other alternative data storage servers (e.g BossDB) or static files hosted on Cloud Storage (e.g. Neuroglancer Precomputed)\n\n[![Github Actions](https://github.com/scalableminds/webknossos-connect/actions/workflows/main.yml/badge.svg)](https://github.com/scalableminds/webknossos-connect/actions)\n\nAvailable Adapaters / Supported Data Formats:\n- [BossDB](https://bossdb.org/)\n- [Neuroglancer Precomputed](https://github.com/google/neuroglancer/tree/master/src/neuroglancer/datasource/precomputed)\n- [WKW](https://github.com/scalableminds/webknossos-wrap)\n- Tiled TIFF\n\n## Usage\n### 1. Installation / Docker\nInstall webKnossos-connect using Docker or use the instructions for native installation below.\n`docker-compose up --build webknossos-connect`\n\n### 2. Connecting to webKnossos\nRegister your webknossos-connect instance with your main webKnossos instance. Modify the webKnossos Postgres database:\n  ```\n  INSERT INTO "webknossos"."datastores"("name","url","publicurl","key","isscratch","isdeleted","isforeign","isconnector")\n  VALUES (E\'connect\', E\'http://localhost:8000\', E\'http://localhost:8000\', E\'secret-key\', FALSE, FALSE, FALSE, TRUE);\n  ```\n### 3. Adding Datasets\nAdd and configure datasets to webKnossos-connect to make them available for viewing in webKnossos\n\n#### 3.1 REST API\nYou can add new datasets to webKnossos-connect through the REST interface. POST a JSON configuration to:\n```\nhttp://<webKnossos-connect>/data/datasets?token\n```\nThe access `token` can be obained from your user profile in the webKnossos main instance. [Read more in the webKnosssos docs.](https://docs.webknossos.org/reference/rest_api#authentication)\n\nExample JSON body. More examples can be found [here](https://github.com/scalableminds/webknossos-connect/blob/master/data/datasets.json).\n```\n{\n    "boss": {\n        "Test Organisation": {\n            "ara": {\n                "domain": "https://api.boss.neurodata.io",\n                "collection": "ara_2016",\n                "experiment": "sagittal_50um",\n                "username": "<NEURODATA_IO_USER>",\n                "password": "<NEURODATA_IO_PW>"\n            },\n        }\n    },\n    "neuroglancer": {\n        "Test Organisation": {\n            "fafb_v14": {\n                "layers": {\n                    "image": {\n                        "source": "gs://neuroglancer-fafb-data/fafb_v14/fafb_v14_clahe",\n                        "type": "image"\n                    }\n                }\n            }\n        }\n    },\n    "tiff": {\n        "Test Organization": {\n            "my_2d_tiff_dataset": {\n                "scale": [2.1,2.1]\n            }\n        }\n    }\n}\n```\n\nNote that tiff datasets are hosted locally. Create compatible tifs with `vips tiffsave source.tif color.tif --tile --pyramid --bigtiff --compression none --tile-width 256 --tile-height 256` and save the generated `color.tif` file at `data/binary/sample_organization/my_2d_tiff_dataset`.\n\nCURL Example\n```\ncurl http:/<webKnossos-connect>/data/datasets -X POST -H "Content-Type: application/json" --data-binary "@datasets.json"\n```\n\n#### 3.2 webKnossos UI\nAlternatively, new datasets can be added directly through the webKnossos UI. Configure and import a new datasets from the webKnossos dashboard. (Dashboard -> Datasets -> Upload Dataset -> Add wk-connect Dataset)\n\n[Read more in the webKnossos docs.](https://docs.webknossos.org/guides/datasets#uploading-through-the-web-browser)\n\n#### 3.3 Default test datasets\n\nBy default, some public datasets are added to webKnossos-connect to get you started when using the Docker image.\n\n## Development\n### In Docker :whale:\n\n* Start it with `docker-compose up dev`\n* Run other commands `docker-compose run --rm dev pipenv run lint`\n* [Check below](#moar) for moar commands.\n* If you change the packages, rebuild the image with `docker-compose build dev`\n\n### Native\n#### Installation\n\nYou need Python 3.8 with `poetry` installed.\n\n```bash\npip install poetry\npoetry install\n```\n\n#### Run\n\n* Add webknossos-connect to the webKnossos database:\n  ```\n  INSERT INTO "webknossos"."datastores"("name","url","publicurl","key","isscratch","isdeleted","isforeign","isconnector")\n  VALUES (E\'connect\', E\'http://localhost:8000\', E\'http://localhost:8000\', E\'secret-key\', FALSE, FALSE, FALSE, TRUE);\n  ```\n* `python -m wkconnect`\n* ```\n  curl http://localhost:8000/api/neuroglancer/Demo_Lab/test \\\n    -X POST -H "Content-Type: application/json" \\\n    --data-binary "@datasets.json"\n  ```\n\n### Moar\n\nUseful commands:\n\n* Lint with `pylint` & `flake8`\n* Format with `black`, `isort` & `autoflake`\n* Type-check with `mypy`\n* Benchark with `timeit`\n* Trace with `py-spy`\n\nUse the commands:\n\n* `scripts/pretty.sh`\n* `scripts/pretty-check.sh`\n* `scripts/lint.sh`\n* `scripts/type-check.sh`\n* `benchmarks/run_all.sh`\n\nTrace the server on http://localhost:8000/trace.\n\n## License\nAGPLv3\nCopyright [scalable minds](https://scalableminds.com)\n',
    'author': 'scalable minds',
    'author_email': 'hello@scalableminds.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}
from build import *
build(setup_kwargs)

setup(**setup_kwargs)
