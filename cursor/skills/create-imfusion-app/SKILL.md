---
name: create-imfusion-app
description: Create ImFusion standalone applications with the proper project structure, executable target setup, runtime bootstrap, and Windows dependency handling. Use when building a separate executable with the ImFusion SDK rather than an ImFusionSuite plugin.
---

# Create ImFusion App

Guide for creating standalone ImFusion SDK applications.

Use this skill for **standalone executables**. For Suite extensions, use the plugin workflow instead.

## Scope

This skill covers:
- project structure for a standalone app
- minimal executable scaffolding
- runtime bootstrap for Windows
- validation and startup troubleshooting

For shared CMake patterns and helper functions, also use the `setup-sdk-cmake` skill.

## Minimal Rules

1. Use `add_executable(...)`, not plugin registration macros.
2. Do not create `ImFusionLibPlugin` classes for standalone apps.
3. Keep `imfusion_set_common_target_properties()` as the default for Visual Studio launch/output setup.
4. On Windows, copy only the runtime files you actually need for startup.

## Directory Structure

```text
MyApp/
|-- CMakeLists.txt
|-- src/
|   |-- main.cpp
|   `-- MyProcessor.cpp
`-- include/
    `-- MyProcessor.h
```

## Minimal CMake Template

```cmake
cmake_minimum_required(VERSION 3.16)
project(MyApp)

find_package(ImFusionLib REQUIRED)

set(Sources
    src/main.cpp
    src/MyProcessor.cpp
)

set(Headers
    include/MyProcessor.h
)

add_executable(MyApp ${Sources} ${Headers})
target_link_libraries(MyApp PRIVATE ImFusionLib)
target_include_directories(MyApp PRIVATE include)

imfusion_set_common_target_properties(MyApp)
```

## Minimal Application Entry Point

```cpp
#include <ImFusion/Base/SharedImageSet.h>
#include <ImFusion/IO/ImageIO.h>

int main(int argc, char** argv)
{
    // Keep startup minimal first. Load data and call processing only after the
    // executable launches cleanly.
    return 0;
}
```

## Windows Runtime Bootstrap

`imfusion_set_common_target_properties()` already configures the Visual Studio debugger `PATH` and `QT_PLUGIN_PATH` so that all SDK and Qt DLLs are found automatically when running inside the IDE.

### Exception: ONNX Runtime version mismatch

On Windows, a different `onnxruntime.dll` already present on the system `PATH` (e.g. Windows) may load before the SDK-provided one. The symptom is a startup error like:

> `The requested API version [N] is not available, only API versions [...] are supported`

Fix: always copy only `onnxruntime.dll` next to the exe as a post-build step. Because the exe's own directory is searched first on Windows, this guarantees the correct version wins.

```cmake
# Only needed when using ImFusionML: ensures the SDK-bundled onnxruntime.dll
# is found before any incompatible version that may be present on PATH.
add_custom_command(TARGET MyApp POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
        "$<TARGET_FILE_DIR:ImFusionLib>/onnxruntime.dll"
        "$<TARGET_FILE_DIR:MyApp>"
)
```


## When To Add Extra Debug Environment

Only add custom `VS_DEBUGGER_ENVIRONMENT` if startup still fails with DLL or Qt plugin errors.

If needed:
- put the ImFusion `plugins` directory before the Suite root in `PATH`
- include `QT_PLUGIN_PATH`
- include `QT_QPA_PLATFORM_PLUGIN_PATH`
- include `IMFUSION_PLUGIN_PATH`

## Fast Triage

- ONNX API mismatch (`requested X, supported Y`) on Windows
  -> a stale `onnxruntime.dll` elsewhere on `PATH` loaded first; copy `onnxruntime.dll` from `$<TARGET_FILE_DIR:ImFusionLib>` next to the exe (see **ONNX Runtime version mismatch** above)

- executable starts in the IDE but not from Explorer
  -> runtime dependencies are coming from the debugger environment instead of the app folder; verify the post-build copy step is present

## Completion Checklist

- [ ] Target uses `add_executable(...)`
- [ ] No plugin registration macros or plugin classes are present
- [ ] `imfusion_set_common_target_properties(...)` is configured
- [ ] Required runtime DLL copies are configured for Windows

## Related Skills

- Use `choose-imfusion-app-architecture` before scaffolding if plugin vs app is still unclear
- Use `setup-sdk-cmake` for fuller CMake templates and helper-function details
