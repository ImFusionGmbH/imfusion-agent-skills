---
name: handle-coordinates
description: Work with pixel, image, and world coordinate transformations in ImFusion SDK. Use when converting between coordinate systems, handling image transformations, or working with tracking/registration matrices.
---

# Handle Image Coordinate Systems

Guide for working with coordinate transformations in medical imaging.

## Coordinate System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│ PIXEL COORDS          IMAGE COORDS           WORLD COORDS       │
│ (integer indices)     (millimeters)          (patient space)    │
│                                                                 │
│    ┌───┬───┬───┐          ▲ y                    ▲ Z (head)     │
│    │0,0│1,0│2,0│          │                      │              │
│    ├───┼───┼───┤      ◄───┼───► x            ◄───┼───► X        │
│    │0,1│1,1│2,1│          │                     /│              │
│    └───┴───┴───┘          ▼                    / ▼ Y            │
│                                                                 │
│  spacing[0] = 1mm    origin at center     patient-oriented      │
└─────────────────────────────────────────────────────────────────┘
```

## Three Coordinate Systems

### 1. Pixel Coordinates

- Integer indices into image array
- Origin: typically top-left corner (0, 0)
- Units: pixels/voxels
- Range: [0, width-1] × [0, height-1] × [0, depth-1]

### 2. Image Coordinates

- Physical position relative to image center
- Origin: center of image volume
- Units: millimeters
- Accounts for spacing

### 3. World Coordinates

- Global reference frame (patient space)
- Standard orientation:
  - X: patient right → left
  - Y: patient front → back  
  - Z: patient feet → head
- Units: millimeters

## Transformation Chain

```
Pixel → Image → World

P_world = Matrix_toWorld × P_image
P_image = P_pixel × spacing - (size × spacing) / 2
```

## C++ Coordinate Conversions

### Using SharedImage

```cpp
#include <ImFusion/Base/SharedImage.h>

SharedImage& img = ...;

// Pixel to World
vec3 pixelPos(100, 50, 0);
vec3 worldPos = img.pixelToWorld(pixelPos);

// World to Pixel
vec3 worldPt(10.0, 20.0, 5.0);
vec3 pixelPt = img.worldToPixel(worldPt);

// Get transformation matrix
mat4 toWorld = img.matrix();  // TOWORLD convention
```

### Using ImageDescriptor

```cpp
#include <ImFusion/Base/ImageDescriptor.h>

ImageDescriptor desc = img.descriptor();

// Spacing (mm per pixel)
vec3 spacing = desc.spacing();

// Dimensions
ivec3 size = desc.size();

// Physical size in mm
vec3 physicalSize = vec3(size) * spacing;
```

### Manual Conversion

```cpp
// Pixel to Image (local mm coordinates)
vec3 pixelToImage(const vec3& pixel, const ImageDescriptor& desc)
{
	vec3 spacing = desc.spacing();
	vec3 size(desc.size());
	return pixel * spacing - (size * spacing) * 0.5;
}

// Image to World
vec3 imageToWorld(const vec3& imagePos, const mat4& matrix)
{
	vec4 homogeneous(imagePos, 1.0);
	return vec3(matrix * homogeneous);
}
```

## Python Coordinate Conversions

```python
import imfusion
import numpy as np

img = ...  # SharedImage

# Get transformation matrix
matrix = img.matrix  # 4x4 numpy array

# Get spacing
spacing = img.spacing  # (sx, sy, sz)

# Pixel to world
def pixel_to_world(pixel: np.ndarray, img) -> np.ndarray:
    spacing = np.array(img.spacing)
    size = np.array(img.size)
    
    # Pixel to image coordinates
    image_pos = pixel * spacing - (size * spacing) / 2
    
    # Image to world
    homogeneous = np.append(image_pos, 1.0)
    world_pos = img.matrix @ homogeneous
    return world_pos[:3]
```

## Matrix Conventions

### TOWORLD vs FROMWORLD

ImFusion uses **TOWORLD** convention for images:
- Matrix transforms FROM image coordinates TO world coordinates
- `P_world = Matrix × P_image`

### Tracking Matrices

Tracking data also uses TOWORLD:
- `P_world = Registration × Tracking × Calibration × P_tool`

```cpp
// Complete transformation chain
mat4 toWorld = registration * tracking * calibration;
vec3 worldPos = vec3(toWorld * vec4(toolPos, 1.0));
```

## Working with Tracked Images

```cpp
#include <ImFusion/GL/TrackedSharedImageSet.h>

TrackedSharedImageSet& sweep = ...;

// Get tracking pose for frame
int frameIndex = 10;
mat4 pose = sweep.getTrackingPose(frameIndex);

// Full transformation: image pixel to world
vec3 pixelPos(100, 50, 0);
vec3 imagePos = sweep[frameIndex]->pixelToImage(pixelPos);
vec4 worldPos = pose * vec4(imagePos, 1.0);
```

## Common Patterns

### Resampling to Common Space

Use the `ImageResamplingAlgorithm` with a reference descriptor to resample an image with respect to another one.
Use the `StandardizeImageAxesOperation` to reorganize the memory buffer of a medical image to ensure anatomical consistency.
Use the `BakeTransformationOperation` or `BakeTransformationAlgorithm` to resample an image so that it does not have any rotation matrix.

### Applying Registration Result

```cpp
// After registration, get transformation
mat4 finalMatrix = registrationAlgorithm.outputMatrix();

// Apply to moving image
movingImage.setMatrix(finalMatrix * movingImage.matrix());
```

### Converting Mesh Vertices

```cpp
// Transform mesh to world coordinates
Mesh& mesh = ...;
mat4 meshToWorld = mesh.matrix();

for (auto& vertex : mesh.vertices())
{
	vec3 worldPos = vec3(meshToWorld * vec4(vertex.position(), 1.0));
	// Use worldPos...
}
```

## Troubleshooting

| Issue | Likely Cause | Solution |
|-------|--------------|----------|
| Flipped images | Wrong origin convention | Check if data uses top-left or center origin |
| Scale mismatch | Ignoring spacing | Always multiply by spacing for physical coords |
| Misaligned data | Matrix not applied | Verify TOWORLD matrix is used correctly |
| Tracking offset | Missing calibration | Apply calibration matrix in transform chain |

## Checklist

- [ ] Know which coordinate system your data is in
- [ ] Apply spacing when converting pixel to physical
- [ ] Use correct matrix convention (TOWORLD)
- [ ] Include all matrices in tracking chain
- [ ] Handle shift/scale for intensity values
- [ ] Verify origin convention (center vs corner)
