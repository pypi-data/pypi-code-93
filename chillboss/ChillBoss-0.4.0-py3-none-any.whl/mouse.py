"""Interact with Pointer."""

import logging
from random import randrange
from time import sleep
from typing import Optional, Tuple

import pyautogui

logger: logging.Logger = logging.getLogger("chillboss")


class Pointer:
    """Driver for mouse pointer movement."""

    def __init__(
        self,
        movement: str = "random",
        length: Optional[int] = None,
        sleep_time: int = 30,
        motion_time: int = 0,
    ):
        """Create the object for Pointer class.

        Args:
            movement (str): Type of movement, `square` and `random` are allowed. Default to `random`.
            length (Optional[int]): Applicable for square movement, length of edge of square in pixels.
            sleep_time (int): Time to sleep in between consecutive movements of pointer.
            motion_time (int): Time to be taken to move consecutive coordinates of pointer.
        """
        self._movement: str = movement
        self._sleep_time: int = sleep_time
        self._motion_time: int = motion_time
        self._x_pixels: int
        self._y_pixels: int
        self._x_pixels, self._y_pixels = pyautogui.size()
        smaller_dimension: int = min(self._x_pixels, self._y_pixels)
        self._length: int = length if length is not None else smaller_dimension // 10
        if self._length > smaller_dimension and movement == "square":
            logger.error(
                f"Given length {self._length} is greater than the display resolution {smaller_dimension}. "
                f"Please enter a smaller value."
            )
            raise ValueError(
                f"Given length {self._length} is greater than the display resolution {smaller_dimension}. "
                f"Please enter a smaller value."
            )
        logger.debug(f"Pointer class object created with attributes: {self.__dict__}.")

    def _get_random_coordinates(self) -> Tuple[int, int]:
        """Random coordinate within bounds of display.

        Returns:
            Tuple[int, int]: Random x,y pixels coordinate within the display bounds.

        """
        random_x_pixel: int = randrange(start=0, stop=self._x_pixels)
        random_y_pixel: int = randrange(start=0, stop=self._y_pixels)
        logger.info(
            f"Random coordinates generated are: ({random_x_pixel}, {random_y_pixel})."
        )
        return random_x_pixel, random_y_pixel

    def _get_square_coordinates(
        self,
    ) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
        """Calculate square coordinates.

        Returns:
            Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]] : Tuple consisting of tuples
            with square coordinates.
        """
        half_length: int = self._length // 2
        x_center: int = self._x_pixels // 2
        y_center: int = self._y_pixels // 2
        if (
            x_center + half_length >= self._x_pixels
            or y_center + half_length >= self._y_pixels
        ):
            raise ValueError("Pixels out of bound of the screen")
        return (
            (x_center - half_length, y_center - half_length),
            (x_center + half_length, y_center - half_length),
            (x_center + half_length, y_center + half_length),
            (x_center - half_length, y_center + half_length),
        )

    def _random_movement(self) -> None:
        """Move the pointer in random direction until KeyBoardInterrupt."""
        while True:
            try:
                x_move_to: int
                y_move_to: int
                x_move_to, y_move_to = self._get_random_coordinates()
                pyautogui.moveTo(x=x_move_to, y=y_move_to, duration=self._motion_time)
                logger.info(f"Pointer moved to ({x_move_to}, {y_move_to}).")
                sleep(self._sleep_time)
            except KeyboardInterrupt:
                logger.debug("Caught KeyBoardInterrupt.")
                break

    def _squared_movement(self) -> None:
        """Move the pointer in squared direction until KeyBoardInterrupt."""
        corners = self._get_square_coordinates()
        while True:
            try:
                for corner in corners:
                    x_move_to: int
                    y_move_to: int
                    x_move_to, y_move_to = corner
                    pyautogui.moveTo(
                        x=x_move_to, y=y_move_to, duration=self._motion_time
                    )
                    logger.info(f"Pointer moved to ({x_move_to}, {y_move_to}).")
                    sleep(self._sleep_time)
            except KeyboardInterrupt:
                logger.debug("Caught KeyBoardInterrupt.")
                break

    def move_the_mouse_pointer(self) -> None:
        """Adapter to call movement method accordingly."""
        try:
            {
                "random": self._random_movement,
                "square": self._squared_movement,
            }[self._movement]()
        except KeyError:
            logger.error(f"Caught KeyError for unknown movement input {self._movement}")
            raise
