---
name: create-python-algorithm
description: Create Python algorithms that integrate into ImFusionSuite GUI. Use when the user wants to implement custom processing in Python, extend ImFusionSuite with Python code, or create Python-based image processing algorithms.
---

# Create Python Algorithm Extension

Guide for creating Python algorithms that appear in ImFusionSuite.

For generic Python style, type hints, docstring format, and exception conventions, apply `.cursor/rules/python-guidelines.mdc`.

## Prerequisites

- ImFusion Python SDK installed (`imfusion` package)
- Python plugin enabled in ImFusionSuite

## Basic Algorithm Structure

```python
import imfusion
from imfusion import SharedImageSet
from imfusion.algorithm import IncompatibleError

class MyAlgorithm(imfusion.Algorithm):
    """Brief description of the algorithm."""

    def __init__(self, image: SharedImageSet):
        super().__init__()
        self.image = image
        
        # Define parameters (automatically creates UI)
        self.add_param("threshold", 100.0, "min: 0, max: 1000")
        self.add_param("iterations", 10, "min: 1, max: 100")
        self.add_param("enabled", True)

    @classmethod
    def convert_input(cls, data: list) -> list:
        """Validate and convert input data.
        
        Parameters:
            data: List of Data objects from selection
            
        Returns:
            Converted input data for constructor
            
        Raises:
            IncompatibleError: If input data is incompatible
        """
        if len(data) != 1 or not isinstance(data[0], SharedImageSet):
            raise IncompatibleError("Requires exactly one image")
        return data

    def compute(self) -> list:
        """Execute the algorithm.
        
        Returns:
            List of output Data objects
        """
        # Access parameters
        threshold = self.threshold
        iterations = self.iterations
        
        # Process image
        output = self._process_image(self.image, threshold, iterations)
        
        return [output]

    def _process_image(self, image: SharedImageSet, threshold: float, iterations: int) -> SharedImageSet:
        """Internal processing logic."""
        import numpy as np
        
        result = SharedImageSet()
        for i in range(len(image)):
            img = image[i]
            arr = img.numpy()  # Get numpy array
            
            # Apply processing
            processed = np.where(arr > threshold, arr, 0)
            
            # Create output image
            out_img = img.clone()
            out_img.assign_array(processed)
            result.add(out_img)
        
        return result

# Register the algorithm
imfusion.register_algorithm(
    "MyAlgorithm",           # Internal ID
    "My Category;My Algorithm Name",  # Menu path
    MyAlgorithm
)
```

## Parameter Types

### Numeric Parameters

```python
self.add_param("threshold", 100.0, "min: 0, max: 1000, step: 0.1")
self.add_param("count", 10, "min: 1, max: 100")
```

### Boolean Parameters

```python
self.add_param("enabled", True)
```

### String/Choice Parameters

```python
self.add_param("mode", "fast", "enum: fast, accurate, balanced")
```

### Accessing Parameters

Parameters become instance attributes:

```python
def compute(self):
    value = self.threshold  # Access parameter value
    self.threshold = 200.0  # Set parameter value
```

## Adding Actions

```python
from imfusion.algorithm import Algorithm

class MyAlgorithm(Algorithm):
    def __init__(self, image):
        super().__init__()
        self.image = image

    @Algorithm.action
    def preview(self) -> None:
        """Preview action shown in controller."""
        # Preview logic
        pass

    @Algorithm.action
    def reset(self) -> None:
        """Reset to defaults."""
        self.threshold = 100.0
```

## Input Validation Patterns

### Single Image

```python
@classmethod
def convert_input(cls, data):
    if len(data) != 1 or not isinstance(data[0], SharedImageSet):
        raise IncompatibleError("Requires exactly one image")
    return data
```

### Two Images (e.g., registration)

```python
@classmethod
def convert_input(cls, data):
    images = [d for d in data if isinstance(d, SharedImageSet)]
    if len(images) != 2:
        raise IncompatibleError("Requires exactly two images")
    return images
```

### Image with Mesh

```python
@classmethod
def convert_input(cls, data):
    from imfusion import Mesh
    images = [d for d in data if isinstance(d, SharedImageSet)]
    meshes = [d for d in data if isinstance(d, Mesh)]
    if len(images) != 1 or len(meshes) != 1:
        raise IncompatibleError("Requires one image and one mesh")
    return [images[0], meshes[0]]
```

## Working with Images

### Reading Image Data

```python
import numpy as np

# Get numpy array (with shift/scale applied)
arr = shared_image.numpy()

# Get raw storage values
raw_arr = np.array(shared_image)

# Image properties
spacing = shared_image.spacing
matrix = shared_image.matrix
```

### Writing Image Data

```python
# Clone and modify
output = input_image.clone()
output.assign_array(processed_array)

# Create new image
from imfusion import SharedImage, SharedImageSet
new_img = SharedImage(array, spacing=(1.0, 1.0, 1.0))
result = SharedImageSet()
result.add(new_img)
```

## Configuration Persistence

```python
def configuration(self) -> dict:
    """Return current configuration for saving."""
    return {
        "threshold": self.threshold,
        "iterations": self.iterations
    }

def configure(self, config: dict) -> None:
    """Restore configuration from saved state."""
    if "threshold" in config:
        self.threshold = config["threshold"]
    if "iterations" in config:
        self.iterations = config["iterations"]
```

## Plugin File Structure

Create a Python plugin package:

```
my_plugin/
├── __init__.py
└── algorithms.py
```

`__init__.py`:

```python
from .algorithms import MyAlgorithm
```

`algorithms.py`:

```python
import imfusion
from imfusion.algorithm import IncompatibleError

class MyAlgorithm(imfusion.Algorithm):
    # ... implementation

imfusion.register_algorithm("MyAlgorithm", "Category;Name", MyAlgorithm)
```

## Loading Custom Plugins

Set environment variable or use entry points:

```python
# Entry point in setup.py / pyproject.toml
[project.entry-points."imfusion_sdk"]
my_plugin = "my_plugin"
```

## Checklist

- [ ] Class inherits from `imfusion.Algorithm`
- [ ] `convert_input()` validates and returns input data
- [ ] `compute()` returns list of output Data objects
- [ ] Parameters defined with `add_param()` in constructor
- [ ] Algorithm registered with `imfusion.register_algorithm()`
- [ ] Uses `IncompatibleError` for input validation

## Related Rules

- See `.cursor/rules/python-guidelines.mdc` for Python conventions
- See `create-imfusion-algorithm` skill for C++ equivalent
