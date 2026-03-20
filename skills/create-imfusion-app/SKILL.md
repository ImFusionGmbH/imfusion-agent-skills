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

On Windows, start with only these post-build copies when they are required by your app:
- `onnxruntime.dll`
- `onnxruntime_providers_shared.dll`
- `platforms/qwindows.dll`

If your app uses Qt UI, make sure the Qt platform plugin is available beside the executable or in a configured Qt plugin path.

## When To Add Extra Debug Environment

Only add custom `VS_DEBUGGER_ENVIRONMENT` if startup still fails with DLL or Qt plugin errors.

If needed:
- put the ImFusion `plugins` directory before the Suite root in `PATH`
- include `QT_PLUGIN_PATH`
- include `QT_QPA_PLATFORM_PLUGIN_PATH`
- include `IMFUSION_PLUGIN_PATH`

## Fast Triage

- `qt.qpa.plugin ... "windows"`
  -> missing Qt platform plugin path or missing `qwindows.dll`

- ONNX API mismatch (`requested X, supported Y`) on Windows
  -> the wrong `onnxruntime.dll` was loaded first; verify `PATH` order and exe-local DLL copies

- executable starts in the IDE but not from Explorer
  -> runtime dependencies are coming from the debugger environment instead of the app folder

## Completion Checklist

- [ ] Target uses `add_executable(...)`
- [ ] No plugin registration macros or plugin classes are present
- [ ] `imfusion_set_common_target_properties(...)` is configured
- [ ] Required runtime DLL copies are configured for Windows
- [ ] Debug and Release builds succeed
- [ ] App startup smoke test succeeds outside the debugger when relevant

## Related Skills

- Use `choose-imfusion-app-architecture` before scaffolding if plugin vs app is still unclear
- Use `setup-sdk-cmake` for fuller CMake templates and helper-function details
