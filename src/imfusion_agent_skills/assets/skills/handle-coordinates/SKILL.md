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

Never include any spacing in the world matrix of an image.
In most applications, the world matrix is expected to be an isometry (but exceptions like non-rigid registration exist).

## World Matrices

### TOWORLD vs FROMWORLD

Depending on the type of Data, world matrices may either map to or from the world coordinate system:
Use methods `Data::matrix` and `Data::setMatrix` if they only deal with a known data type for performance reasons. 
In cases where multiple or a priori unknown data types are used and inference of the internally used transformation convention is cumbersome, the convenience methods `Data::matrixToWorld` and `Data::matrixFromWorld` shall be used.

### Tracking Matrices

Tracking matrices are a special case of world matrices, and are used to represent coordinate systems of an image or an instrument tracked by a camera, an EM system, etc.
Tracking data also uses TOWORLD and are composed of several 4x4 matrices:
`P_world = Registration × Tracking × Calibration × P_tool`

### Other data types

Data like `Mesh` and `PointCloud` may also have a world matrix, even if they don't have pixel/image coordinates.
Use these matrices when accessing the coordinates of the vertices or the points.


## Common Patterns

### Resampling to Common Space

Use the `ImageResamplingAlgorithm` with a reference descriptor to resample an image with respect to another one.
Use the `StandardizeImageAxesOperation` to reorganize the memory buffer of a medical image to ensure anatomical consistency.
Use the `BakeTransformationOperation` or `BakeTransformationAlgorithm` to resample an image so that it does not have any rotation matrix.


## Checklist

- [ ] Know which coordinate system your data is in
- [ ] Apply spacing when converting pixel to physical
- [ ] Use correct matrix convention (TOWORLD)
- [ ] Include all matrices in tracking chain
- [ ] Verify origin convention (center vs corner)
