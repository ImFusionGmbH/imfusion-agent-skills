<!-- Auto-generated from cursor/rules/code-review-checklist.mdc — do not edit directly -->

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