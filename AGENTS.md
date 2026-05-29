<!-- Auto-generated from cursor/rules/*.mdc — do not edit directly -->

# Algorithm Pattern

For a full implementation guide and templates, see the `create-imfusion-algorithm` skill.

When implementing `Algorithm` classes:
- Set `m_status` correctly in `compute()` (Success or documented error enum)
- Avoid exceptions for regular failures; use return codes and enums
- Document preconditions/postconditions and any `\throws`
- Functions like `takeOutput` that just implement the `Algorithm` interface do not need docstrings, but new functions do

---

# CMake Guidelines

For full templates and setup guide, see the `setup-sdk-cmake` skill.

- Use modern target-based CMake; prefer `function()` over `macro()`.
- List files explicitly; do not use `file(GLOB ...)`.
- Options naming:
  - Framework: `IMFUSION_*` (e.g., `IMFUSION_ENABLE_PRECOMPILED_HEADERS`)
  - Project/Target: `IMFUSION_<TargetName>_*` (e.g., `IMFUSION_ML_USE_CUDA`)
  - Actions: BUILD/ENABLE/USE/INSTALL verbs
- Formatting: functions in `snake_case` with `imfusion_` prefix; local variables `PascalCase`; cache/global vars `ALL_CAPS`.

---

# Code Review Checklist

- [ ] Naming: classes/methods/members follow conventions; units in names where relevant
- [ ] Doxygen for public/protected API; ownership, units, exceptions documented
- [ ] Constructors `explicit` (single arg); no virtual calls in ctors
- [ ] Const-correctness; `override` used for overrides
- [ ] Error handling: return codes (0=success); enums for non-trivial codes
- [ ] Memory: unique_ptr/shared_ptr usage correct; no raw owning pointers
- [ ] Threading: minimal shared state; no unknown code while holding locks
- [ ] Formatting: project clang-format; braces/spacing/pointers per standard
- [ ] CMake: target-based; correct option naming; no file(GLOB)

---

# Compile After Code Changes

After making substantive edits to C++ source files, headers, or CMake files, **always compile** to verify the changes build successfully.

## Workflow

1. Make your code changes.
2. Reuse the project's existing build setup when possible:
   - Prefer an existing build directory.
   - Prefer commands documented in the project's `README` or existing scripts.
3. If a build directory already exists, build using its matching configuration, for example:
   ```
   cmake --build <build-dir> --config <config>
   ```
4. If no build directory or preset is available, inspect the project first and ask the user which configure/build flow should be used before creating a new one.
5. If compilation fails, read the error output, fix the issues you introduced, and rebuild.
6. Repeat until the build succeeds before moving on.

## Notes

- Do NOT skip the compile step; catching errors early avoids cascading issues.
- Fix only the errors you introduced; don't refactor unrelated code while fixing build errors.
- Do not assume `_build`, `Debug`, parallelism flags, SDK locations, Qt versions, or `CMAKE_PREFIX_PATH` values unless the project already uses them.
- If configuration requires local SDK or Qt paths and they are not already documented in the project, ask the user instead of hardcoding machine-specific values.

---

# ImFusion Core Development Principles

- Optimize for the reader, not the writer
- KISS: prefer lean, pragmatic interfaces; avoid over-engineering
- Medical device context: hold to high quality and safety standards
- Keep PRs small; delete feature branches after merge

---

# C++ Guidelines

## Naming Conventions
- Classes: PascalCase
- Methods/Variables: camelCase
- Members: m_ prefix; Parameters: p_ prefix; Signals: signal prefix; Globals: g_ prefix (avoid)
- Constants: PascalCase (e.g., `const int Border = 2`)

## Class Design
- Prefer composition over inheritance; minimize inheritance.
- Single-argument constructors must be `explicit`.
- Do not call virtual functions from constructors.
- Initialize all members; prefer `= value` in headers.
- Rule of Three; prefer copy-and-swap when implementing copy/assign.
- Put implementations in .cpp; keep trivial getters/setters inline if needed.

## Functions/Methods
- Inputs first, then outputs; avoid output parameters, prefer return structs.
- Pass non-fundamental inputs by `const&`.
- Use raw `T*` for nullable, non-owning references; `T&` for non-null references.
- Use `std::unique_ptr<T>` for ownership transfer.
- Mark const methods with `const`; use `override` on overrides.
- Keep functions ~<=50 lines; split if too long.

## Integral Types and Enums
- Prefer `int`; use `int64_t` when >2GB ranges.
- Avoid unsigned arithmetic types; use sized types like `uint16_t` when needed.
- Prefer `enum class` for mutually exclusive values.
- Use plain `enum` for bitfields/constants; scope properly.
- Use `Flags<Enum>` as parameter type for bitfield enums.

## Casting and Macros
- Prefer C++ casts (`static_cast`, `const_cast`, `reinterpret_cast`, `dynamic_cast`).
- Use `static_cast` with custom types; minimize `dynamic_cast`.
- Macros: UPPER_CASE_WITH_UNDERSCORES; avoid new macros; `#pragma once` for header guards.

## Lambdas and Move Semantics
- Use explicit captures if lambda escapes scope; avoid capturing by reference for non-local use.
- Keep lambdas small (<~20 lines); avoid deep nesting.
- Do not add move ops for copyable types unless needed; mark move ops `noexcept`.

## Namespaces
- All code under `ImFusion`.
- Use short PascalCase names (e.g., `GL`, `ML`). Use lowercase `detail` for implementation-only.
- Do not nest non-library/plugin namespaces deeper than one level beyond the top-level or plugin namespace (e.g., `ImFusion::Foo` and `ImFusion::CT::Bar` are OK; `ImFusion::Foo::Bar` is not).

## Error Handling
- Return values are primary failure indicator; `0` indicates success.
- Use a class-specific `enum` for non-trivial error codes.
- Use exceptions only for critical/unrecoverable errors; document with `\throws`.
- Check resource allocations when there is risk (e.g., >1MB).

## Formatting (Key Points)
- Use project clang-format; braces on their own lines; spaces around binary ops.
- `*`/`&` adjacent to type (e.g., `char* data`). One tab stop per indentation.
- Include order: project headers, ImFusionLib headers, other libraries, C++ headers.

## Critical Header Include Paths
- Use `ImFusion/Core/Properties.h` for configuration
- Use `ImFusion/Base/MemImage.h` and `ImFusion/Base/TypedImage.h` for CPU image access
- Use `ImFusion/Base/SharedImageSet.h` for image collections

## Logging
- Use the macros `LOG_ERROR`, `LOG_WARN`, `LOG_INFO`, `LOG_DEBUG`.
- These macros do not use fmt-style formatting, but you may explicitly call `fmt::format`.
- The first argument is the category, which should be hierarchical with the following fragments/levels: Module name (for ImFusionLib: folder name, for plugins: plugin name), Namespace if existent (everything underneath the ImFusion namespace), Class/algorithm/function name.
  - Example for classes: Core.Threading.ThreadPool, GL.Program, Base.BasicImageProcessing, US.FrameGeometry.
  - Examples for Free functions: Core.Threading, Base.ImageProcessing.rotate().
- Use `LOG_DEFAULT_CATEGORY` to define a log category for the entire file.

---

# GLSL Shader Guidelines

For full shader templates and visualization guide, see the `implement-visualization` skill.

- Use distinct extensions: `.vert`, `.geom`, `.frag`, `.comp`, `.glh`.
- Choose sufficiently unique shader filenames; match owning C++ class when applicable.
- IO blocks: use `in_` and `out_` prefixes.
- Uniforms: use `u_` prefix.
- Shared includes: use a common prefix for globals/functions to emulate namespacing.

---

# ML Operations Guidelines

Applies when implementing or modifying `ImFusion::ML::Operation` subclasses under `ImFusionLib/Include/ImFusion/ML/Operations` and `ImFusionLib/Source/ML/Operations`.

## Class Structure
- Derive from `ImFusion::ML::Operation` and place class in `ImFusion::ML` namespace.
- Class names end with `Operation` (e.g., `AxisRotationOperation`).
- Class names are usually verbs (e.g., `Normalize`, `Invert`).
- Constructors must accept parameters with default values so the class remains default-constructible (e.g., `explicit FooOperation(int param = 3)`). Keep constructor defaults in sync with parameter member defaults.
- Expose configuration via `AdvancedParameter<T>` members. Prefer `= value` initialization in headers.
- Set an appropriate `ProcessingPolicy` in the constructor (`Everything`, `OnlyLabels`, or `EverythingExceptLabels`).

## Processing Entry Points
- Prefer overriding delegate methods over the main `process(DataItem&)`:
  - `processImages`, `processBoxes`, `processPoints`, `processVectors`, `processTensors`.
- Only override `process(DataItem&)` when you need to add/remove/swap/reorder fields (pipeline-level transforms).
  - If so, disable the utility overloads with `ML_OPERATION_DISABLE_UTILITY_PROCESS`.
- If the operation will not modify inputs, override `doesNotModifyInput()` and return `true`.
- When overriding `process(DataItem&)`, use `m_activeFields` and/or the default `m_processingFieldsPolicy` to select the fields to be processed.
- Try to perform operations in-place on the `DataElement`.
- If you need to find the label map in the input data item, use `ML::Utils::isSemanticSegmentationMap`.

## Parameters and Properties
- Use `AdvancedParameter<T>` (or `OpParam<T>`) for all configurable parameters.
- Parameters must be public and start with the `p_` prefix (e.g., `p_kernelSize`).
- Names should be descriptive and consistent with Properties conventions (prefer `camelCase`) for the underlying property name.
- Document units and value domains in Doxygen (e.g., `distanceMm`, `pixelToWorldMatrix`).
- Mark required parameters with `ParamRequired::Yes`; otherwise provide sensible defaults.
- Use `signalValueChanged` from Parameters to react on value changes.

## Device, Performance, and GPU
- Use `computingDevice()/setComputingDevice()` and `useGPU()` to choose device.
- Call `prepareInputForDevice()` before GPU work; set `allowChannelBatchOnGPU()` only if supported.
- Keep shared mutable state minimal; prefer copying over synchronization.
- If possible, use ImageMath in the implementation so that both CPU and GPU implementations are available.

## Exceptions, Logging, and Behavior
- Throw errors via `throwOperationError(...)` (raises `OperationException` with proper domain).
- Use `warnOperationUnexpectedBehaviour(...)` for non-fatal anomalies and honor `errorOnUnexpectedBehaviour()`.
- Use `inputIsEmptyOrNull(...)` guard helpers where applicable.

## Inversion and Recording
- If supporting inversion, implement accordingly and override `supportsInversion()`.
- Use `recordIdentifier()` to tag operations in processing history when inversion/recording is intended.

## Factory Registration
- Register the operation in the C++ Operation factory so it can be constructed by name:
  - Get the C++ sub-factory via `ImFusion::ML::getCppOperationFactory()`.
  - Register your class with a unique operation name (typically the class name without namespace).

## Python Bindings and Changelog
- Add the new operation to Python bindings in `ImFusionLib/Source/ML/PythonBindings/OperationsBindings.cpp` using the appropriate `ml_bind_class_doc*` helper.
- Add a changelog entry to `ImFusionLib/Source/ML/Changelog.yaml` with the correct tags (Added/Changed/Fixed/Deprecation/API-Break), referencing the exact class name.

## Doxygen and Grouping
- Document the class and public/protected members.
- Use `\ingroup MLDataOperations` to group meta-operations and `\ingroup MLOperations` for actual ML operations.
- Do not use `\author` or `\brief`; the first sentence is used as summary.

## Implementation Checklist
- [ ] Class in `ImFusion::ML`, ends with `Operation`, constructor sets `ProcessingPolicy`.
- [ ] Add files to `CMakeLists.txt` of the ML pluigin.
- [ ] Public parameters as `AdvancedParameter<T>`/`OpParam<T>` with `p_` prefix and defaults; units documented.
- [ ] Override appropriate delegate(s); avoid overriding `process(DataItem&)` unless restructuring fields.
- [ ] Proper device handling and GPU preparation; channel batching supported only when safe.
- [ ] Use `throwOperationError`/`warnOperationUnexpectedBehaviour`; no raw exceptions for routine failures.
- [ ] If non-mutating, implement `doesNotModifyInput()`.
- [ ] Operation registered in C++ factory with unique name.
- [ ] Python bindings added in `OperationsBindings.cpp` with docstrings and named args.
- [ ] ML changelog updated in `ImFusionLib/Source/ML/Changelog.yaml`.
- [ ] Add a C++ test in the `ImFusionLib/Source/ML/Test/Operations` folder.
- [ ] Add a test case to `test_MLOperations.py` 

@ml-operation-header-template.h
@ml-operation-cpp-template.cpp

---

# ImFusion Plugin Conventions

For step-by-step creation guide, see the `create-imfusion-plugin` skill.

## Naming Pattern

| Component | Pattern | Example |
|-----------|---------|---------|
| Include dir | `ImFusion/<ShortName>` | `ImFusion/MyPlugin` |
| Namespace | `<ShortName>` under ImFusion | `ImFusion::MyPlugin` |
| Plugin ID | `ImFusion.<ShortName>` | `ImFusion.MyPlugin` |
| CMake target | `<ShortName>Plugin` | `MyPlugin` |
| Library | `ImFusion<ShortName>Plugin.dll/so/dylib` | `ImFusionMyPlugin.dll` |
| Plugin class | `<PluginName>Plugin` | `TorchPlugin` |
| Factory classes | `<PluginName>AlgorithmFactory`, `<PluginName>AlgorithmControllerFactory` | |
| Config file | Always `Config.h` | |

## Key Requirements

- Plugin class must inherit from `ImFusionLibPlugin`
- `IMFUSION_REGISTER_PLUGIN` macro must be in the `.cpp` file (not the header)
- Static `id()` must return `"ImFusion.<ShortName>"`
- Implement `getAlgorithmFactory()`, `getAlgorithmControllerFactory()`, `pluginName()`
- Config.h must use platform-aware export macros (Windows `__declspec`, no-op elsewhere)
- Log category: `#define IMFUSION_LOG_DEFAULT_CATEGORY "MyPlugin"`

## Common Mistakes

- Module names in `imfusion_require_modules()` are case-sensitive: `"Base"` not `"BASE"`
- `imfusion_set_common_target_properties(Plugin ...)` — use `Plugin`, not the target name
- `imfusion_common_install(Plugin)` — same, use `Plugin`

---

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

---

# Qt Lifecycle and Teardown Safety

- For objects with non-trivial destructors (controllers, annotation widgets), do not rely on implicit Qt child destruction if order matters.
- If a child destructor accesses the parent window, display state, or GL resources, destroy that child explicitly in the owner destructor first.

## Required Pattern for Manual Teardown

- Remove from layout (`removeWidget`), detach (`setParent(nullptr)`), then `delete`.
- Avoid half-manual ownership (`removeWidget` alone) for QObject trees.
- After explicit delete, null member pointers used during shutdown paths.

## `createWindowContainer` Rule

- `QWidget::createWindowContainer(window, parent)` takes ownership of `window`.
- Do not keep a second owning handle to that embedded `QWindow` (`std::unique_ptr`, `QScopedPointer`, manual `delete`, or another Qt owner).
- If later access is needed, store the embedded window as a non-owning pointer/member and treat the container widget as the sole owner.
- During teardown, explicitly destroy the container first if ordering matters, then null any non-owning pointers to the embedded window.
- If close-time crashes involve Qt/GL teardown, prefer explicit destruction of the container in owner destructor before base-class teardown.

## Close-Crash Checklist

- Verify destructor order: owner -> controllers -> child widgets.
- Verify no destructor calls into already-destroyed parent window internals.
- Check for double-destruction paths from mixed Qt-parent and manual deletion.
- Keep fixes minimal and targeted to ownership/order, not behavioral logic.

---

# UI / UX Best Practices

Use this as a short checklist to consider when adding or changing UI behavior.

- Initialize newly loaded data to a sensible visible state, including contrast/window-level when needed.

- Show progress for long-running work such as loading, inference, export, or preprocessing.
  * Bind progress UI to real algorithms or SDK progress when available.
  * Keep progress indicators responsive while synchronous work runs on the UI thread.
  * When the SDK is using OpenGL operations in the background thread, calls should be wrapped into `GL::ContextManager::get().runWithOpenGL`
  * Return progress UI to a clear idle state after completion, failure, or cancellation.  

- Remember user choices that should feel persistent across sessions.
For instance, persist file and folder dialog locations when they improve workflow continuity.
Store dialog history per parameter or per workflow, not as one shared path for unrelated actions.

- Preserve responsive feedback for failures: show a concise error, keep prior valid state when possible, and avoid silent no-op behavior.
