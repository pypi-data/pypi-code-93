from marshmallow import INCLUDE, Schema, fields, post_load


class Comic:
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class ComicSchema(Schema):
    """ Schema for Comic api """

    publisher = fields.Str()
    description = fields.Str()
    title = fields.Str()
    price = fields.Str()
    creators = fields.Str()
    release_date = fields.Date(format="%Y-%m-%d")
    diamond_id = fields.Str()

    class Meta:
        unknown = INCLUDE

    @post_load
    def make_object(self, data, **kwargs):
        """
        Make the comic object.
        :param data: Data from Shortboxed response.
        :returns: :class:`Comic` object
        :rtype: Comic
        """
        return Comic(**data)
