---
name: qt-embed-resources
description: Embed binary assets (images, icons, fonts, etc.) into a Qt/CMake C++ executable using Qt resources. Use when the user wants to embed files, add icons or logos, bundle assets, or use Qt resource system (.qrc) in a CMake project.
---

# Embedding Resources in a Qt/CMake Project

## Problem

`CMAKE_AUTORCC` with relative paths in `.qrc` files is unreliable: `rcc` may fail to resolve paths depending on the build system's working directory. This is a known issue with certain CMake + Qt version combinations.

## Solution

Use `configure_file()` to generate a `.qrc` containing **absolute paths**, then compile it with `qt5_add_resources()`.

## Step-by-Step

### 1. Create a `.qrc.in` template next to your assets

```xml
<!-- assets/resources.qrc.in -->
<!DOCTYPE RCC>
<RCC version="1.0">
    <qresource prefix="/">
        <file alias="logo.png">@APP_ASSETS_DIR@/logo.png</file>
        <!-- add more files as needed -->
    </qresource>
</RCC>
```

The `alias` attribute controls the runtime resource path (`:/logo.png`).
The file path uses a CMake variable that will expand to an absolute path.

### 2. In CMakeLists.txt

```cmake
# Define the absolute path to the assets directory
set(APP_ASSETS_DIR "${CMAKE_CURRENT_SOURCE_DIR}/assets")

# Generate the .qrc with absolute paths into the build directory
configure_file(
    "${CMAKE_CURRENT_SOURCE_DIR}/assets/resources.qrc.in"
    "${CMAKE_CURRENT_BINARY_DIR}/resources.qrc"
    @ONLY
)

# Compile the .qrc into a C++ source file
qt5_add_resources(QRC_SOURCES "${CMAKE_CURRENT_BINARY_DIR}/resources.qrc")

# Include the generated source in your target
add_executable(MyApp ${QRC_SOURCES} src/main.cpp ...)
```

**Important:** Do NOT use `CMAKE_AUTORCC` for this. Remove it or leave it for other `.qrc` files that don't need this treatment.

### 3. Access the resource in C++ code

```cpp
// Images
QPixmap pixmap(":/logo.png");
QIcon icon(":/icon.svg");

// Text files
QFile file(":/config.json");
file.open(QIODevice::ReadOnly);

// Style sheets
QFile qss(":/style.qss");
qss.open(QIODevice::ReadOnly | QIODevice::Text);
qApp->setStyleSheet(qss.readAll());
```

## Why This Works

- `rcc` receives absolute file paths in the generated `.qrc`, so it finds files regardless of working directory.
- `qt5_add_resources()` gives CMake explicit control over the `rcc` invocation (unlike `AUTORCC` which uses an opaque custom build step).
- `configure_file(@ONLY)` only substitutes `@VAR@` placeholders, leaving everything else untouched.

## Adding More Assets

Add entries to the `.qrc.in` template:

```xml
<file alias="icon.svg">@APP_ASSETS_DIR@/icon.svg</file>
<file alias="style.qss">@APP_ASSETS_DIR@/style.qss</file>
<file alias="fonts/Roboto.ttf">@APP_ASSETS_DIR@/fonts/Roboto.ttf</file>
```

All paths are resolved at CMake configure time. After adding files, re-run CMake.
