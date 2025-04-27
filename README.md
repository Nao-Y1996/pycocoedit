# pycocoedit

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![ci](https://github.com/hachimada/pycocoedit/actions/workflows/ci.yml/badge.svg)](https://github.com/hachimada/pycocoedit/actions)
[![codecov](https://codecov.io/gh/hachimada/pycocoedit/branch/main/graph/badge.svg)](https://codecov.io/gh/hachimada/pycocoedit)

<html>
    <h2 align="center">
      <img src="https://github.com/hachimada/pycocoedit/blob/main/docs/assets/pycocoedit.png?raw=true" alt="pycocoedit Logo" width="256">
    </h2>
    <h3 align="center">
      An open-source lightweight Python package for editing and analyzing COCO datasets.
    </h3>
    <h3 align="center">
        Important Links: <a href="https://hachimada.github.io/pycocoedit/">Docs</a>
    </h3>

</html>

**pycocoedit** is a Python package for editing and analyzing [COCO datasets](https://cocodataset.org/#home).

It is particularly useful for specifying which images, annotations, categories, or licenses to include or exclude from your dataset.

With **pycocoedit**, you can apply custom filters to your dataset. These filters allow you to control inclusion or exclusion based on custom conditions for images, categories, annotations, and licenses.

For example, you can filter out specific images that have a certain number of annotations or exclude annotations with bounding boxes of a certain aspect ratio.


## Usage

Example of filtering images and categories.

```python
from pycocoedit.objectdetection.data import CocoData
from objectdetection.filter import FilterType, ImageFileNameFilter, CategoryNameFilter

annotation = "path/to/annotation.json"
new_annotation = "path/to/new_annotation.json"

# only include images with file name "image1.jpg" and "image2.jpg"
file_filter = ImageFileNameFilter(FilterType.INCLUSION, ["image1.jpg", "image2.jpg"])
# only include categories with category name "cat" and "dog"
category_filter = CategoryNameFilter(FilterType.INCLUSION, ["cat", "dog"])

coco_data = CocoData(annotation)
# apply filters and export new annotation
coco_data.add_filter(file_filter).add_filter(category_filter).apply_filter().save(new_annotation)
```

Example of custom filter for annotations:  
In this example, we create a custom filter that only includes annotations with bounding boxes of area less than 100.

```python
from pycocoedit.objectdetection.data import CocoData
from objectdetection.filter import BaseFilter, FilterType, TargetType


# only include annotations with area less than 100
class SmallBboxIncludeFilter(BaseFilter):
    def __init__(self):
        super().__init__(FilterType.INCLUSION, TargetType.ANNOTATION)

    def apply(self, data: dict) -> bool:
        return data["area"] < 100


annotation = "path/to/annotation.json"
new_annotation = "path/to/new_annotation.json"

coco_data = CocoData(annotation)
# apply custom filter and export new annotation
coco_data.add_filter(SmallBboxIncludeFilter()).apply_filter().save(new_annotation)
```

## Installation

### Install with pip

```bash
pip install pycocoedit
````

### Install with Poetry

Add following to your `pyproject.toml`:

```toml
[tool.poetry.dependencies]
pycocoedit = {git = "https://github.com/hachimada/pycocoedit", branch = "main" }
```

## Key Features

| Feature                          | What it gives you                                                                                     |
|----------------------------------|-------------------------------------------------------------------------------------------------------|
| **LEGO-style chainable filters** | One-liner `include` / `exclude` rules for images, annotations, categories, etc.                       |
| **Custom rules**                 | simply inherit `BaseFilter`, implement a short apply() method, and your custom logic is ready to use. |
| **Built-in data cleanup**        | `CocoData.correct()` - Built-in data cleanup that removes orphaned annotations & empty categories.    |
| **Pure Python ≥ 3.10**           | Zero external deps; runs anywhere CPython runs—no C build hassle.                                     |
| **Typed & unit-tested**          | IDE auto-completion and high confidence when refactoring.                                             |

## Task Support

| Task                  | Supported                            | version |
|-----------------------|--------------------------------------|---------|
| Object Detection      | ✅ (`pycocoedit.objectdetection`)     | 0.1.0   |
| Image Segmentation    | ✅ (use `pycocoedit.objectdetection`) | 0.1.0   |
| Keypoint Detection    | ❌ (future release)                   |         |
| Panoptic Segmentation | ❌ (future release)                   |         |
| Image Captioning      | ❌ (future release)                   |         |

## Roadmap

1. Image Captioning
2. key-point support
3. Panoptic Segmentation

Contributions and ideas are welcome—feel free to open an issue or pull request on GitHub!  

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](https://github.com/hachimada/pycocoedit/blob/main/LICENSE) file for details.


