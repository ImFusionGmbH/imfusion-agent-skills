<!-- Auto-generated from cursor/rules/public-demos-reference.mdc — do not edit directly -->

# Public Demos Reference

When building plugins, algorithms, standalone apps, or integrations with the ImFusion SDK, consult the public demo projects for working examples and established patterns.

## Where to Find Them

- **GitHub repository**: https://github.com/ImFusionGmbH/public-demos
- If the repository is cloned locally in the workspace or a sibling directory, prefer reading from the local copy.

## Version Matching

Always use the tag matching the ImFusion SDK version in use. Tags follow the pattern `imfusion-sdk-vX.Y` (e.g. `imfusion-sdk-v4.4`).

1. Determine the SDK version from the project (e.g. from `CMakeLists.txt`, `find_package(ImFusionLib X.Y)`, or by asking the user).
2. Use that version to construct the tag: `imfusion-sdk-vX.Y`.
3. When fetching files from GitHub, use that tag as the ref (e.g. `?ref=imfusion-sdk-v4.4`). Fall back to the `release` branch only if no matching tag exists.

## Available Demos

| Demo | What it shows |
|------|---------------|
| `ExamplePlugin` | Plugin template — start here for new plugins |
| `ExampleStandaloneApplication` | Standalone app using the SDK |
| `ExampleMainWindowBaseApplication` | MainWindowBase app for DICOM display |
| `ExampleMachineLearningInference` | Deep learning model integration |
| `ExampleAnatomyPlugin` | AnatomicalStructure / AnatomicalStructureCollection |
| `TotalSegmentatorAnatomyPlugin` | Custom anatomy plugin (TotalMeshSegmentator) |
| `Example2D3DRegistration` | 2D/3D registration customization |
| `ExampleDicomBrowser` | DICOM browser using ImFusionDicom |
| `ExampleDicomExtension` | Custom DICOM tag read/write |
| `ExampleITK` | ITK interop |
| `ExampleOpenCV` | OpenCV interop |
| `ExampleOpenGL` | OpenGL rendering / image processing |
| `ExampleImageMath` | ImageMath plugin usage |
| `ExampleRGBDReconstruction` | RGBD 3D reconstruction |
| `BrushStandaloneApplication` | Interactive Brush tool for labeling |
| `AnnotationHandle` | Interactive handles on GlPointBasedAnnotation |
| `QMLRendererDemo` | ImFusionLib rendering in QML |
| `SlicerExtension` | 3D Slicer integration |
| `StreamExamples` | Creating and working with Streams |
| `TractographyPlugin` | Custom data type + GlObject + DataDisplayHandler |

## When to Consult

- Creating a new plugin or algorithm: look at `ExamplePlugin`, `ExampleAnatomyPlugin`
- Building a standalone application: look at `ExampleStandaloneApplication`, `ExampleMainWindowBaseApplication`
- ML inference integration: look at `ExampleMachineLearningInference`
- Custom visualization / GlObject: look at `TractographyPlugin`, `AnnotationHandle`
- CMake setup: any demo's `CMakeLists.txt` is a good reference