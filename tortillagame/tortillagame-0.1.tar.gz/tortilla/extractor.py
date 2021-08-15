import pygame


class ImageExtractor:
    def scale_image(self, image: pygame.Surface, scale_factor: float) -> pygame.Surface:
        """
        Scales and returns the given image

        :param image: the original pygame.Surface
        :param scale_factor: how much to scale the image by
        :return: the scaled image
        """
        if scale_factor == 1:
            return image
        width, height = image.get_rect().size[0], image.get_rect().size[1]
        return pygame.transform.scale(image, (int(width * scale_factor), int(height * scale_factor)))

    def extract_image(self, path: str, scale_factor=1) -> pygame.Surface:
        """
        Extracts image from file and returns it as a surface

        :param path:
        :param scale_factor:
        :return: the extracted image
        """
        image = pygame.image.load(path).convert_alpha()
        # image = pygame.image.load(path)
        image = self.scale_image(image, scale_factor)
        return image

    def extract_images(self, path: str, sprite_width: int, scale_factor=1) -> list:
        """
        Extracts images from a sprite sheet and returns them as a list

        :param scale_factor:
        :param path: relative path to sprite sheet
        :param sprite_width: width of a sprite in pixels
        :return: list of images of the sprite sheets
        """
        sheet = pygame.image.load(path).convert_alpha()
        width, h = sheet.get_size()
        sprites = int(width / sprite_width)
        images = []
        for x in range(sprites):
            images.append(self.scale_image(sheet.subsurface(x * sprite_width, 0, sprite_width, h), scale_factor))
        return images
