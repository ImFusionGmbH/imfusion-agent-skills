<!-- Auto-generated from cursor/rules/algorithm-pattern.mdc — do not edit directly -->

---
paths:
  - "**/*Algorithm.h"
  - "**/*Algorithm.cpp"
---

# Algorithm Pattern

For a full implementation guide and templates, see the `create-imfusion-algorithm` skill.

When implementing `Algorithm` classes:
- Set `m_status` correctly in `compute()` (Success or documented error enum)
- Avoid exceptions for regular failures; use return codes and enums
- Document preconditions/postconditions and any `\throws`
- Functions like `takeOutput` that just implement the `Algorithm` interface do not need docstrings, but new functions do