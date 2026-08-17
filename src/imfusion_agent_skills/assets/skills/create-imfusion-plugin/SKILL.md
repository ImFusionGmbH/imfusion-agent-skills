---
name: create-imfusion-plugin
description: Create ImFusion plugins with proper structure, registration, and factory wiring. Use when the user wants to create a new plugin, extend ImFusionSuite with custom functionality, or scaffold a plugin project.
---

# Create ImFusion Plugin

Guide for creating ImFusion plugins following SDK conventions.

Use this skill for plugin-specific structure and registration.

For the canonical plugin `CMakeLists.txt` template and helper-function details, use the `setup-sdk-cmake` skill.

## Directory Structure

```
MyPlugin/
├── CMakeLists.txt
├── include/
│   └── ImFusion/
│       └── MyPlugin/
│           ├── Config.h
│           └── MyPlugin.h
└── src/
    └── MyPlugin.cpp
```

## Plugin Naming

| Component | Pattern | Example |
|-----------|---------|---------|
| Include dir | `ImFusion/<ShortName>` | `ImFusion/MyPlugin` |
| Namespace | `<ShortName>` under ImFusion | `ImFusion::MyPlugin` |
| Plugin ID | `ImFusion.<ShortName>` | `ImFusion.MyPlugin` |
| CMake target | `<ShortName>Plugin` | `MyPlugin` |
| Library | `ImFusion<ShortName>Plugin.dll/so/dylib` | `ImFusionMyPlugin.dll` |

For the full invariant list, see the `plugin` project rule.

## Step 1: Create Config.h

```cpp
#pragma once

#if defined(_MSC_VER)
#   if defined(MY_PLUGIN_DLL)
#       define MY_PLUGIN_API __declspec(dllexport)
#   elif defined(IMFUSIONLIB_STATIC)
#       define MY_PLUGIN_API
#   else
#       define MY_PLUGIN_API __declspec(dllimport)
#   endif
#else
#   define MY_PLUGIN_API
#endif

#define MY_PLUGIN_NO_SDK_API MY_PLUGIN_API
```

## Step 2: Create Plugin Header

```cpp
#pragma once

#include <ImFusion/MyPlugin/Config.h>
#include <ImFusion/Base/AlgorithmControllerFactory.h>
#include <ImFusion/Base/AlgorithmFactory.h>
#include <ImFusion/Base/ImFusionPlugin.h>

namespace ImFusion
{
	/// Algorithm factory for MyPlugin algorithms
	class MyAlgorithmFactory : public AlgorithmFactory
	{
	public:
		MyAlgorithmFactory();
	};

	/// Algorithm controller factory for MyPlugin algorithms
	class MyAlgorithmControllerFactory : public AlgorithmControllerFactory
	{
	public:
		MyAlgorithmControllerFactory();
		AlgorithmController* create(Algorithm* a) const override;
	};

	/// Main plugin class for MyPlugin
	class MY_PLUGIN_API MyPlugin : public ImFusionLibPlugin
	{
	public:
		static const char* id() { return "ImFusion.MyPlugin"; }
		std::string author() const override { return "Your Name"; }
		std::string description() const override { return "Plugin description"; }
	protected:
		Status init() override;
	};
}
```

## Step 3: Create Plugin Implementation

```cpp
#include <ImFusion/MyPlugin/MyPlugin.h>

IMFUSION_REGISTER_PLUGIN(ImFusion::MyPlugin)

#undef IMFUSION_LOG_DEFAULT_CATEGORY
#define IMFUSION_LOG_DEFAULT_CATEGORY "MyPlugin"

namespace ImFusion
{
	MyAlgorithmFactory::MyAlgorithmFactory()
		: AlgorithmFactory("MyPlugin", false)
	{
		// Register algorithms:
		// registerAlgorithm<MyAlgorithm>("MyAlgorithm", "Category;Display Name");
	}

	MyAlgorithmControllerFactory::MyAlgorithmControllerFactory()
		: AlgorithmControllerFactory("MyPlugin", false)
	{
	}

	AlgorithmController* MyAlgorithmControllerFactory::create(Algorithm* a) const
	{
		// Return nullptr or create controllers for your algorithms
		return nullptr;
	}

	PluginBase::Status MyPlugin::init()
	{
		// Optional license check:
		// if (!isLicensed("MyPlugin"))
		//     return Status::LicenseCheckFailed;
		
		registerFactories(
			std::make_unique<MyAlgorithmFactory>(),
			std::make_unique<MyAlgorithmControllerFactory>(),
			nullptr
		);
		return Status::Success;
	}
}
```

## Step 4: Create CMakeLists.txt

Use the plugin template from `setup-sdk-cmake`.

The plugin-specific points to verify are:
- the target name matches your plugin short name
- `DEFINE_SYMBOL` matches the export macro in `Config.h`
- install/register helpers use the plugin pattern expected by the SDK

## Adding Algorithms

1. Create algorithm class (see `create-imfusion-algorithm` skill)
2. Register in factory constructor:

```cpp
MyAlgorithmFactory::MyAlgorithmFactory()
	: AlgorithmFactory("MyPlugin", false)
{
	registerAlgorithm<MyAlgorithm>("MyAlgorithm", "Processing;My Algorithm");
}
```

## Adding Module Dependencies

```cmake
# Available modules: Base, GL, IO, REG, SEG, ML, Python, Stream, US, LiveUS
imfusion_require_modules("Base;ML;SEG")

# External dependencies
imfusion_soup_target_require(MyPlugin PRIVATE some_external_lib)
```

## Adding Plugin Dependencies

```cpp
// In plugin header
std::vector<std::string> dependencies() const override
{
	return {"ImFusion.OtherPlugin"};
}
```

## Critical Invariants

Before considering the plugin complete, verify:
- `IMFUSION_REGISTER_PLUGIN(...)` is in the `.cpp` file, not the header
- `static id()` returns `ImFusion.<ShortName>`
- `Config.h` owns the platform-aware export macros
- factory registration happens from the plugin initialization path

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Plugin not loading | Check `IMFUSION_REGISTER_PLUGIN` is in .cpp file |
| Module requirement error | Module names are case-sensitive (Base, not BASE) |
| CMake function error | Use `imfusion_set_common_target_properties(Plugin ...)` not target name |
| Linking errors | Verify required modules are listed |

## Checklist

- [ ] Directory structure follows convention
- [ ] Config.h has platform-aware export macros
- [ ] Plugin ID matches `ImFusion.<ShortName>` pattern
- [ ] `IMFUSION_REGISTER_PLUGIN` in .cpp file
- [ ] Factory classes created and registered
- [ ] Log category set: `#define IMFUSION_LOG_DEFAULT_CATEGORY "MyPlugin"`

## Related Guidance

- See the `plugin` project rule for additional patterns
- See the `cmake-guidelines` project rule for CMake conventions
- Use `setup-sdk-cmake` for the full plugin CMake template
