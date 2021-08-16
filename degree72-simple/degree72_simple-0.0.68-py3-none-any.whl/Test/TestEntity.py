from Core.EntityBase import EntityBase
import PySQL


@PySQL.table(table_name="youtube_video_info")
class TestEntity(EntityBase):
    id = None
    type = None
    count = None
    pass