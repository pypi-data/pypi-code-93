#  Copyright (c) European Space Agency, 2017, 2018, 2019, 2020.
#
#  This file is subject to the terms and conditions defined in file 'LICENCE.txt', which
#  is part of this Pyxel package. No part of the package, including
#  this file, may be copied, modified, propagated, or distributed except according to
#  the terms contained in the file ‘LICENCE.txt’.

"""TBW."""
from pyxel.detectors import Geometry


class CMOSGeometry(Geometry):
    """Geometrical attributes of a CMOS-based detector."""

    def __init__(
        self,
        # Parameters for Geometry
        row: int = 0,
        col: int = 0,
        total_thickness: float = 0.0,
        pixel_vert_size: float = 0.0,
        pixel_horz_size: float = 0.0,
        # Parameters for CMOS Geometry
        n_output: int = 1,
        n_row_overhead: int = 0,
        n_frame_overhead: int = 0,
        reverse_scan_direction: bool = False,
        reference_pixel_border_width: int = 4,
    ):
        """Create a new instance of `CMOSGeometry`.

        Parameters
        ----------
        n_output: int
            Number of detector outputs.
        n_row_overhead: int
            New row overhead in pixel.
            This allows for a short wait at the end of a row before starting the next row.
        n_frame_overhead: int
            New frame overhead in rows.
            This allows for a short wait at the end of a frame before starting the next frame.
        reverse_scan_direction: bool
            Set this True to reverse the fast scanner readout directions.
            This capability was added to support Teledyne’s programmable fast scan readout directions.
            The default setting (False) corresponds to what HxRG detectors default to upon power up.
        reference_pixel_border_width: int
            Width of reference pixel border around image area.
        """
        if n_output not in range(33):
            raise ValueError("'n_output' must be between 0 and 32.")

        if n_row_overhead not in range(101):
            raise ValueError("'n_row_overhead' must be between 0 and 100.")

        if n_frame_overhead not in range(101):
            raise ValueError("'n_frame_overhead' must be between 0 and 100.")

        if reference_pixel_border_width not in range(33):
            raise ValueError("'reference_pixel_border_width' must be between 0 and 32.")

        super().__init__(
            row=row,
            col=col,
            total_thickness=total_thickness,
            pixel_vert_size=pixel_vert_size,
            pixel_horz_size=pixel_horz_size,
        )

        self._n_output = n_output
        self._n_row_overhead = n_row_overhead
        self._n_frame_overhead = n_frame_overhead
        self._reverse_scan_direction = reverse_scan_direction
        self._reference_pixel_border_width = reference_pixel_border_width

    @property
    def n_output(self) -> int:
        """Get Number of detector outputs."""
        return self._n_output

    @n_output.setter
    def n_output(self, value: int) -> None:
        """Set Number of detector outputs."""
        if value not in range(33):
            raise ValueError("'n_output' must be between 0 and 32.")

        self._n_output = value

    @property
    def n_row_overhead(self) -> int:
        """Get Number of detector outputs."""
        return self._n_row_overhead

    @n_row_overhead.setter
    def n_row_overhead(self, value: int) -> None:
        """Set Number of detector outputs."""
        if value not in range(101):
            raise ValueError("'n_row_overhead' must be between 0 and 100.")

        self._n_row_overhead = value

    @property
    def n_frame_overhead(self) -> int:
        """Get New frame overhead in rows."""
        return self._n_frame_overhead

    @n_frame_overhead.setter
    def n_frame_overhead(self, value: int) -> None:
        """Set New frame overhead in rows."""
        if value not in range(101):
            raise ValueError("'n_frame_overhead' must be between 0 and 100.")

        self._n_frame_overhead = value

    @property
    def reverse_scan_direction(self) -> bool:
        """Get reverse scan direction."""
        return self._reverse_scan_direction

    @reverse_scan_direction.setter
    def reverse_scan_direction(self, value: bool) -> None:
        """Set reverse scan direction."""
        self._reverse_scan_direction = value

    @property
    def reference_pixel_border_width(self) -> int:
        """Get Number of detector outputs."""
        return self._reference_pixel_border_width

    @reference_pixel_border_width.setter
    def reference_pixel_border_width(self, value: int) -> None:
        """Set Number of detector outputs."""
        if value not in range(33):
            raise ValueError("'reference_pixel_border_width' must be between 0 and 32.")

        self._reference_pixel_border_width = value
