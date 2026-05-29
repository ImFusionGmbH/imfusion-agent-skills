---
name: setup-sdk-cmake
description: CMake reference for ImFusion SDK projects. Use when you need details on ImFusion CMake helper functions (imfusion_set_common_target_properties, imfusion_provide_ide_instructions, imfusion_compile_resource_repository), naming conventions, best practices, test setup, or linking optional SDK modules. For creating a new plugin or standalone app, prefer the create-imfusion-plugin or create-imfusion-app skills instead.
---

# Setup CMake for ImFusion SDK

CMake reference for external ImFusion SDK projects (customers building plugins or standalone apps).

## Project Types

1. **Plugin**: Shared library loaded by ImFusionSuite
2. **Standalone App**: Independent executable using the SDK

## Plugin CMake Template

```cmake
cmake_minimum_required(VERSION 3.13.0)
project(MyPlugin)

# List optional SDK modules in COMPONENTS (e.g. ImFusionML ImFusionSeg)
find_package(ImFusionLib REQUIRED)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

set(Sources
	src/MyPlugin.cpp
	src/MyAlgorithm.cpp
)
set(Headers
	include/MyPlugin.h
	include/MyAlgorithm.h
)

add_library(MyPlugin SHARED ${Sources} ${Headers})
target_include_directories(MyPlugin PRIVATE include)
target_link_libraries(MyPlugin PRIVATE ImFusionLib)

# Configure output directories and VS launch settings
imfusion_set_common_target_properties()
# Print instructions for loading the plugin in ImFusionSuite
imfusion_provide_ide_instructions()
```

## Standalone App CMake Template

```cmake
cmake_minimum_required(VERSION 3.13.0)
project(MyApp)

find_package(ImFusionLib REQUIRED)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

set(Sources
	src/main.cpp
)
set(Headers
	include/MyProcessor.h
)

add_executable(MyApp ${Sources} ${Headers})
target_include_directories(MyApp PRIVATE include)
target_link_libraries(MyApp PRIVATE ImFusionLib)

imfusion_set_common_target_properties()
```

## Linking Optional SDK Modules

List modules in `COMPONENTS` and add them to `target_link_libraries`:

```cmake
find_package(ImFusionLib COMPONENTS ImFusionML ImFusionSeg ImFusionDicom REQUIRED)

target_link_libraries(MyPlugin PRIVATE ImFusionLib ImFusionML ImFusionSeg ImFusionDicom)
```

Common modules: `ImFusionGL`, `ImFusionIO`, `ImFusionReg`, `ImFusionSeg`, `ImFusionML`,
`ImFusionStream`, `ImFusionUS`, `ImFusionDicom`, `ImFusionITK`, `ImFusionOpenCV`

## ImFusion CMake Functions

### imfusion_set_common_target_properties

Configures output directories, Visual Studio launch settings, and plugin discovery paths.
Call with no arguments after `target_link_libraries`:

```cmake
imfusion_set_common_target_properties()
```

### imfusion_provide_ide_instructions

Prints a message in the build output with instructions on how to load the built plugin
in ImFusionSuite. Call after `imfusion_set_common_target_properties()` in plugin targets:

```cmake
imfusion_provide_ide_instructions()
```

### imfusion_compile_resource_repository

Compiles files (e.g. GLSL shaders) into a binary resource repository that can be loaded
at runtime without needing to distribute loose files:

```cmake
imfusion_compile_resource_repository(
	MyPluginShaders
	FILES ${Shaders}
	BASE_DIR "shaders"
)
```

The generated target (`MyPluginShaders`) must be linked into the plugin target.

## Best Practices

### List Files Explicitly

```cmake
# Good: explicit file list
set(Sources
	src/File1.cpp
	src/File2.cpp
)

# Bad: glob pattern (misses new files until CMake re-runs)
file(GLOB Sources "src/*.cpp")
```

### Use Target-Based Commands

```cmake
# Good
target_link_libraries(MyPlugin PRIVATE SomeLib)
target_include_directories(MyPlugin PRIVATE include)

# Bad: global variables affect all targets
link_libraries(SomeLib)
include_directories(include)
```

## Adding Tests

```cmake
if(BUILD_TESTING)
	add_subdirectory(Test)
endif()
```

Test subdirectory:

```cmake
project(MyPluginTest)

set(TestSources
	TestMyAlgorithm.cpp
)

add_executable(MyPluginTest ${TestSources})
target_link_libraries(MyPluginTest PRIVATE MyPlugin doctest::doctest)

add_test(NAME MyPluginTest COMMAND MyPluginTest)
```

## Common Patterns

### Conditional CUDA Support

```cmake
option(MYPLUGIN_USE_CUDA "Enable CUDA support" OFF)

if(MYPLUGIN_USE_CUDA)
	find_package(CUDA REQUIRED)
	target_compile_definitions(MyPlugin PRIVATE MYPLUGIN_USE_CUDA)
	target_link_libraries(MyPlugin PRIVATE CUDA::cudart)
endif()
```

### Platform-Specific Code

```cmake
if(WIN32)
	target_compile_definitions(MyPlugin PRIVATE WIN32_LEAN_AND_MEAN)
elseif(APPLE)
	target_link_libraries(MyPlugin PRIVATE "-framework CoreFoundation")
endif()
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Module not found | Check spelling — module names are case-sensitive (`ImFusionML`, not `ImFusionml`) |
| Linking error | Ensure all required modules are in both `COMPONENTS` and `target_link_libraries` |
| Header not found | Verify `target_include_directories` paths |
| Plugin not loading | Check that `imfusion_set_common_target_properties()` was called |

## Checklist

- [ ] Files listed explicitly (no GLOB)
- [ ] Target-based link and include commands used
- [ ] Optional modules listed in both `COMPONENTS` and `target_link_libraries`
- [ ] `imfusion_set_common_target_properties()` called with no arguments
- [ ] `imfusion_provide_ide_instructions()` called for plugin targets

## Related Rules

- See `.cursor/rules/cmake-guidelines.mdc` for additional CMake conventions
