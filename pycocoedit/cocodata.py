import copy
import json
from typing import Any

from pycocoedit.filter import (
    BaseExclusionFilter,
    BaseFilter,
    BaseInclusionFilter,
    CategoryExcludeFilter,
    CategoryIncludeFilter,
    Filters,
    ImageNameExcludeFilter,
    ImageNameIncludeFilter,
)


def validate_keys(data: list[dict], required_keys: list[str], target: str) -> None:
    for d in data:
        missing_keys = [key for key in required_keys if key not in d]
        if missing_keys:
            raise KeyError(
                f"Missing keys {missing_keys} in {target} with ID: {d.get('id', 'Unknown')}"
            )


def validate_images(images: list[dict]) -> None:
    required_keys = ["id", "file_name", "width", "height"]
    validate_keys(images, required_keys, "image")


def validate_categories(categories: list[dict]) -> None:
    required_keys = ["id", "name", "supercategory"]
    validate_keys(categories, required_keys, "category")


def validate_annotations(annotations: list[dict]) -> None:
    required_keys = ["id", "image_id", "category_id", "bbox", "area", "segmentation"]
    validate_keys(annotations, required_keys, "annotation")


class CocoEditor:
    """
    Coco format dataset editor.
    """

    def __init__(self, annotation: str | dict[str, Any]):

        if isinstance(annotation, dict):
            dataset = copy.deepcopy(annotation)
        else:
            with open(annotation) as f:
                dataset = json.load(f)
        self.images: list[dict] = dataset["images"]
        self.annotations: list[dict] = dataset["annotations"]
        self.categories: list[dict] = dataset["categories"]
        self.licenses: list[dict] = dataset.get("licenses", [])
        self.info: dict = dataset.get("info", {})

        validate_images(self.images)
        validate_categories(self.categories)
        validate_annotations(self.annotations)

        self.image_filters: Filters = Filters()
        self.category_filters: Filters = Filters()
        self.annotation_filters: Filters = Filters()
        self.licenses_filters: Filters = Filters()

        self.filter_applied = False

    def __add_filter(self, filter: BaseFilter, target_type: str):
        """
        Add a filter to the dataset.
        """

        if target_type not in ["image", "category", "annotation", "license"]:
            raise ValueError(
                "target_type should be one of [image, category, annotation, license]"
            )

        if target_type == "image":
            self.image_filters.add(filter)
        if target_type == "category":
            self.category_filters.add(filter)
        if target_type == "annotation":
            self.annotation_filters.add(filter)
        if target_type == "license":
            self.licenses_filters.add(filter)

    def add_file_name_filter(
        self,
        include_files: list[str] | None = None,
        exclude_files: list[str] | None = None,
    ) -> "CocoEditor":
        """
        Add a file name filter.

        Parameters
        ----------
        include_files : list[str] | None
            File names to be included.
        exclude_files : list[str] | None
            File names to be excluded.
        """
        if include_files is not None:
            self.__add_filter(
                ImageNameIncludeFilter(file_names=include_files), target_type="image"
            )
        if exclude_files is not None:
            self.__add_filter(
                ImageNameExcludeFilter(file_names=exclude_files), target_type="image"
            )
        return self

    def add_category_filter(
        self,
        include_names: list[str] | None = None,
        exclude_names: list[str] | None = None,
    ) -> "CocoEditor":
        """
        Add a category filter.

        Parameters
        ----------
        include_names : list[str] | None
            Category names to be included.
        exclude_names : list[str] | None
            Category names to be excluded.
        """
        if include_names is not None:
            self.__add_filter(
                CategoryIncludeFilter(category_names=include_names),
                target_type="category",
            )
        if exclude_names is not None:
            self.__add_filter(
                CategoryExcludeFilter(category_names=exclude_names),
                target_type="category",
            )
        return self

    def add_custom_filter(
        self, custom_filter: BaseInclusionFilter | BaseExclusionFilter, target_type: str
    ) -> "CocoEditor":
        """
        Add a custom filter.

        Parameters
        ----------
        custom_filter : BaseInclusionFilter | BaseExclusionFilter
            Custom filter to be added.
        target_type : str
            Type of the target data. One of ["image", "category", "annotation", "license"].
        """
        if target_type is None:
            raise ValueError(
                "target_type should be one of [image, category, annotation, license]"
            )
        self.__add_filter(custom_filter, target_type=target_type)
        return self

    def apply_filter(self) -> "CocoEditor":
        """
        Apply filters to the dataset.
        """
        targets: list[list[dict]] = [
            self.images,
            self.categories,
            self.annotations,
            self.licenses,
        ]
        all_filters: list[Filters] = [
            self.image_filters,
            self.category_filters,
            self.annotation_filters,
            self.licenses_filters,
        ]

        def update(index: int, new_data: list[dict]):
            if index == 0:
                self.images = new_data
            if index == 1:
                self.categories = new_data
            if index == 2:
                self.annotations = new_data
            if index == 3:
                self.licenses = new_data

        for i in range(len(targets)):
            filters: Filters = all_filters[i]
            include_filters: list[BaseInclusionFilter] = filters.include_filters
            exclude_filters: list[BaseExclusionFilter] = filters.exclude_filters
            if len(include_filters) != 0:
                new_dicts = []
                for d in targets[i]:
                    for include_filter in include_filters:
                        if include_filter.apply(d):
                            new_dicts.append(d)
                            break
                update(i, new_dicts)
            if len(exclude_filters) != 0:
                new_dicts = []
                for d in targets[i]:
                    for exclude_filter in exclude_filters:
                        if not exclude_filter.apply(d):
                            new_dicts.append(d)
                            break
                update(i, new_dicts)

        self.filter_applied = True
        return self

    def reset(self, annotation: str | dict[str, Any]) -> "CocoEditor":
        """
        Reset the dataset to the original state.
        """

        # TODO refactor this part. This process is equivalent to __init__ method. But, basically call __init__ method
        #  is not recommended and mypy raises an error when calling __init__ method. error: Accessing "__init__" on
        #  an instance is unsound, since instance.__init__ could be from an incompatible subclass
        if isinstance(annotation, dict):
            dataset = copy.deepcopy(annotation)
        else:
            with open(annotation) as f:
                dataset = json.load(f)
        self.images = dataset["images"]
        self.annotations = dataset["annotations"]
        self.categories = dataset["categories"]
        self.licenses = dataset.get("licenses", [])
        self.info = dataset.get("info", {})

        validate_images(self.images)
        validate_categories(self.categories)
        validate_annotations(self.annotations)

        self.image_filters = Filters()
        self.category_filters = Filters()
        self.annotation_filters = Filters()
        self.licenses_filters = Filters()

        self.filter_applied = False
        return self

    def correct(
        self, correct_image: bool = True, correct_category: bool = False
    ) -> dict:
        """
        Correct data inconsistencies after applying filters.

        Parameters
        ----------
        correct_image : bool
            whether to remove images with no annotations.
            default is True.
        correct_category : bool
            whether to remove categories with no annotations.
            default is False.

        Returns
        -------
        dict
            Corrected dataset including info, licenses, images, categories and annotations.
        """
        if not self.filter_applied:
            self.apply_filter()

        # Remove annotations with category_id not in categories
        cat_ids = [cat["id"] for cat in self.categories]
        _annotations = []
        for i in range(len(self.annotations)):
            ann = self.annotations[i]
            _cat_id = ann["category_id"]
            if ann["category_id"] in cat_ids:
                _annotations.append(ann)
        self.annotations = _annotations

        # Remove annotations with no images
        img_ids = [img["id"] for img in self.images]
        _annotations = []
        for i in range(len(self.annotations)):
            ann = self.annotations[i]
            _img_id = ann["image_id"]
            if ann["image_id"] in img_ids:
                _annotations.append(ann)
        self.annotations = _annotations

        if correct_image:
            # Remove images with no annotations
            img_ids = [ann["image_id"] for ann in self.annotations]
            _images = []
            for img in self.images:
                if img["id"] in img_ids:
                    _images.append(img)
            self.images = _images

        if correct_category:
            # Remove categories with no annotations
            cat_ids = [ann["category_id"] for ann in self.annotations]
            _categories = []
            for cat in self.categories:
                if cat["id"] in cat_ids:
                    _categories.append(cat)
            self.categories = _categories

        # TODO Correct licenses
        return {
            "info": self.info,
            "licenses": self.licenses,
            "images": self.images,
            "categories": self.categories,
            "annotations": self.annotations,
        }

    def export(
        self, file_path: str, correct_image: bool = True, correct_category: bool = False
    ) -> None:
        """
        Export the dataset to a json file.
        """
        dataset = self.correct(
            correct_image=correct_image, correct_category=correct_category
        )
        with open(file_path, "w") as f:
            json.dump(dataset, f)
