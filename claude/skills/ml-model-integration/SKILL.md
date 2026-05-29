---
name: ml-model-integration
description: Integrate external medical imaging models (traced from Pytorch or saved as onnx) into ImFusion inference YAMLs, including preprocessing, postprocessing, orientation fixes, sampling setup, and validation. Use when working with MONAI, TotalSegmentator, nnUNet, traced PyTorch models, or custom Machine Learning model YAML integration in ImFusion.
---

# ML Model Integration

Use this skill when integrating an externally trained model into ImFusion via a model YAML or the `MachineLearningModel` API.

Refer to the `ExampleMachineLearningInference` demo in the local `public-demos` checkout and adapt its YAML before changing C++.

## Workflow

1. Identify the training/inference I/O stack used to generate the reference outputs:
   - `nibabel` usually means RAS+ conventions.
   - `SimpleITK` / ITK usually means LPS conventions in memory.
2. Reproduce the external preprocessing exactly in the YAML:
   - intensity mapping
   - orientation changes
   - resampling
   - any nonlinear activation used before inference
3. Make postprocessing the inverse of the orientation-related preprocessing, then finish with `ResampleToInput: {}`.
4. Validate against the traced model using the same Python loading/saving stack used during training.

When using `AdjustShiftScale`, remember that ImFusion computes `output = (input + shift) / scale`.
For example, MONAI `ScaleIntensityRanged(a_min=-57, a_max=164, b_min=0, b_max=1, clip=True)` should map to:

```yaml
- Clip:
    min: -57.0
    max: 164.0
- AdjustShiftScale:
    shift: 57.0
    scale: 221.0
```

## Default Rules

- Prefer traced-model validation before integrating a full tiled inference pipeline.
- Add `BakeTransformation: {}` before tensor inference whenever the engine should consume voxel data in baked image space.
- Keep preprocessing and postprocessing explicitly symmetric for orientation fixes.
- Reuse working patterns from `ExampleMachineLearningInference/demo_model.yaml`.

## Framework Recipes

### MONAI traced model using `nibabel`

Use the following orientation fixup:

```yaml
PreProcessing:
  - BakeTransformation: {}
  - AxisRotation:
      axes: ["y"]
      angles: [90]
  - AxisFlip:
      axes: ["x", "y", "z"]
PostProcessing:
  - AxisFlip:
      axes: ["z", "y", "x"]
  - AxisRotation:
      axes: ["y"]
      angles: [-90]
  - ResampleToInput: {}
```

For MONAI `segResNet` with `normalize_mode: range`, map the training intensity bounds to `[-1, 1]` with `LinearIntensityMapping`, then apply `Sigmoid`.

### TotalSegmentator / nnUNet v2 using `SimpleITK`

Use the following orientation fixup:

```yaml
PreProcessing:
  - BakeTransformation: {}
  - AxisRotation:
      angles: 180
      axes: z
PostProcessing:
  - AxisRotation:
      angles: -180
      axes: z
  - ResampleToInput: {}
```

Intensity transforms come from the model plans. Do not guess them; extract them from the training/export pipeline.

### Checklist

* For 3D ONNX exports, check both input and output tensor layouts: input should be N,C,D,H,W as consumed by ImFusion, while output channels remain axis 1.
