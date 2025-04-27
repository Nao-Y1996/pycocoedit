"""
Filter module for COCO dataset.

This module provides filter implementations for COCO dataset manipulation.
Filters can be used to include or exclude specific elements from the dataset
based on various criteria.
"""

from abc import ABC, abstractmethod
from enum import Enum


class FilterType(Enum):
    """
    Enumeration for filter types.

    Attributes
    ----------
    INCLUSION : int
        Filter to include matching elements (value=1).
    EXCLUSION : int
        Filter to exclude matching elements (value=2).
    """

    INCLUSION = 1
    EXCLUSION = 2


class TargetType(Enum):
    """
    Enumeration for target types that can be filtered.

    Attributes
    ----------
    IMAGE : str
        Target type for image filters.
    ANNOTATION : str
        Target type for annotation filters.
    CATEGORY : str
        Target type for category filters.
    LICENSE : str
        Target type for license filters.
    """

    IMAGE = "image"
    ANNOTATION = "annotation"
    CATEGORY = "category"
    LICENSE = "license"


class BaseFilter(ABC):
    """
    Abstract base class for all filter implementations.

    This class defines the common interface and basic functionality
    for all filter types used in COCO dataset manipulation.

    Parameters
    ----------
    filter_type : FilterType
        The type of filter (inclusion or exclusion).
    target_type : TargetType
        The target data type this filter will be applied to.

    Raises
    ------
    ValueError
        If filter_type or target_type is None or not of the correct type.
    """

    def __init__(self, filter_type: FilterType, target_type: TargetType):
        if not isinstance(filter_type, FilterType) or filter_type is None:
            raise ValueError("filter_type must be a FilterType and not None.")
        if not isinstance(target_type, TargetType) or target_type is None:
            raise ValueError("target_type must be a TargetType and not None.")
        self.filter_type: FilterType = filter_type
        self.target_type: TargetType = target_type

    @abstractmethod
    def apply(self, data: dict) -> bool:
        """Apply the filter to the data.

        Implement logic within this function to determine what data to include or exclude to your dataset.

        -  when ``self.filter_type`` is ``INCLUSION`` and this function return True, the data is included
        -  when ``self.filter_type`` is ``INCLUSION`` and this function return False, the data is excluded
        -  when ``self.filter_type`` is ``EXCLUSION`` and this function return True, the data is excluded
        -  when ``self.filter_type`` is ``EXCLUSION`` and this function return False, the data is included

        Parameters
        ----------
        data : dict
            The data to filter.
            data is expected to be as follows
            - element of the images in the COCO format
            - element of the annotations in the COCO format
            - element of the categories in the COCO format
            - element of the licenses in the COCO format
            - info in the COCO format
            - other dict elements
        """
        raise NotImplementedError


class Filters:
    """
    Container for managing multiple filters.

    This class collects and manages both inclusion and exclusion filters
    to be applied to a dataset.
    """

    def __init__(self):
        """Initialize an empty filters container."""
        self.include_filters: list[BaseFilter] = []
        self.exclude_filters: list[BaseFilter] = []

    def add(self, filter: BaseFilter) -> None:
        """
        Add a filter to the appropriate collection based on its type.

        Parameters
        ----------
        filter : BaseFilter
            The filter to add, either inclusion or exclusion type.
        """
        if filter.filter_type == FilterType.INCLUSION and isinstance(filter, BaseFilter):
            self.include_filters.append(filter)
        if filter.filter_type == FilterType.EXCLUSION and isinstance(filter, BaseFilter):
            self.exclude_filters.append(filter)


class ImageFileNameFilter(BaseFilter):
    """
    Filter images based on their file names.

    Parameters
    ----------
    filter_type : FilterType
        The type of the ``filter.FilterType.INCLUSION`` or ``FilterType.EXCLUSION``.
        If ``FilterType.INCLUSION``, the images with the file names in the ``file_names`` are included.
        If ``FilterType.EXCLUSION``, the images with the file names in the ``file_names`` are excluded.
    file_names : list[str]
        List of file names to filter by.
    """

    def __init__(self, filter_type: FilterType, file_names: list[str]):
        super().__init__(filter_type, TargetType.IMAGE)
        self.file_names = file_names

    def apply(self, data: dict) -> bool:  # noqa: D102
        return data["file_name"] in self.file_names


class CategoryNameFilter(BaseFilter):
    """
    Filter categories based on their names.

    Parameters
    ----------
    filter_type : FilterType
        The type of the ``filter.FilterType.INCLUSION`` or ``FilterType.EXCLUSION``.
        If ``FilterType.INCLUSION``, the categories with the names in the `category_names` are included.
        If ``FilterType.EXCLUSION``, the categories with the names in the `category_names` are excluded.
    """

    def __init__(self, filter_type: FilterType, category_names: list[str]):
        super().__init__(filter_type, TargetType.CATEGORY)
        self.category_names = category_names

    def apply(self, data: dict) -> bool:  # noqa: D102
        return data["name"] in self.category_names


class BoxAreaFilter(BaseFilter):
    """
    Filter annotations based on bounding box area.

    Parameters
    ----------
    filter_type : FilterType
        The type of the ``filter.FilterType.INCLUSION`` or ``FilterType.EXCLUSION``.
        If ``FilterType.INCLUSION``, the data with the area of bbox in the range of ``min_area`` and ``max_area`` are included.
        If ``FilterType.EXCLUSION``, the data with the area of bbox in the range of ``min_area`` and ``max_area`` are excluded.
    min_area : int or None, optional
        Minimum area threshold for the filter, default is None.
    max_area : int or None, optional
        Maximum area threshold for the filter, default is None.

    Notes
    -----
    If both min_area and max_area are None, the filter accepts all areas.
    """

    def __init__(
        self,
        filter_type: FilterType,
        min_area: int | None = None,
        max_area: int | None = None,
    ):
        super().__init__(filter_type, TargetType.ANNOTATION)
        self.min_area = min_area
        self.max_area = max_area

    def apply(self, data: dict) -> bool:  # noqa: D102
        if self.min_area and self.max_area:
            return self.min_area <= data["area"] <= self.max_area
        elif self.min_area:
            return self.min_area <= data["area"]
        elif self.max_area:
            return data["area"] <= self.max_area
        return True
