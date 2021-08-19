from marshmallow import ValidationError

from serifan import exceptions, comic


class ComicsList:
    def __init__(self, response):
        self.comics = []

        schema = comic.ComicSchema()
        for issue_dict in response["comics"]:
            try:
                result = schema.load(issue_dict)
            except ValidationError as error:
                raise exceptions.ApiError(error)

            self.comics.append(result)

    def __iter__(self):
        return iter(self.comics)

    def __len__(self):
        return len(self.comics)

    def __getitem__(self, index: int):
        return self.comics[index]
