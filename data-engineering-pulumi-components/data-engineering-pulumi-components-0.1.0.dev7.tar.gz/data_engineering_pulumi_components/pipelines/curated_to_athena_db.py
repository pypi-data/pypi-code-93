from typing import Optional

from data_engineering_pulumi_components.aws import (
    CuratedBucket,
    GlueDataCrawler,
)
from data_engineering_pulumi_components.utils import Tagger
from pulumi import ComponentResource, ResourceOptions
from pulumi_aws import Provider


class CuratedToAthenaDatabasePipeline(ComponentResource):
    def __init__(
        self,
        name: str,
        curated_bucket: CuratedBucket,
        tagger: Tagger,
        provider: Optional[Provider] = None,
        opts: Optional[ResourceOptions] = None,
    ) -> None:
        super().__init__(
            t=(
                "data-engineering-pulumi-components:pipelines:"
                "CuratedToAthenaDatabasePipeline"
            ),
            name=name,
            props=None,
            opts=opts,
        )

        self._glueDataCrawler = GlueDataCrawler(
            source_bucket=curated_bucket,
            name=name,
            tagger=tagger,
            opts=ResourceOptions(parent=self, provider=provider),
        )
