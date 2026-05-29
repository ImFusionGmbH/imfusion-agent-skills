<!-- Auto-generated from cursor/rules/compile-after-changes.mdc — do not edit directly -->

---
paths:
  - "**/*.cpp"
  - "**/*.h"
  - "**/*.h.in"
  - "**/*.cmake"
  - "**/CMakeLists.txt"
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