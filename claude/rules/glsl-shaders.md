<!-- Auto-generated from cursor/rules/glsl-shaders.mdc — do not edit directly -->

---
paths:
  - "**/*.vert"
  - "**/*.frag"
  - "**/*.geom"
  - "**/*.comp"
  - "**/*.glh"
---

# GLSL Shader Guidelines

For full shader templates and visualization guide, see the `implement-visualization` skill.

- Use distinct extensions: `.vert`, `.geom`, `.frag`, `.comp`, `.glh`.
- Choose sufficiently unique shader filenames; match owning C++ class when applicable.
- IO blocks: use `in_` and `out_` prefixes.
- Uniforms: use `u_` prefix.
- Shared includes: use a common prefix for globals/functions to emulate namespacing.