<!-- Auto-generated from cursor/rules/cpp-guidelines.mdc — do not edit directly -->

---
paths:
  - "**/*.cpp"
  - "**/*.h"
  - "**/*.hpp"
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