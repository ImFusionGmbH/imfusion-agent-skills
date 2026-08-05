---
name: imfusion-imagemath
description: >-
  ImFusion ImageMath expression-template API reference. Use when writing or
  reviewing code with SharedImageSetArithmetic.h, makeArray, or pixel-level
  image arithmetic on SharedImage/SharedImageSet/TypedImage.
---

# ImFusion ImageMath

Include `<ImFusion/ImageMath/SharedImageSetArithmetic.h>`.
Read `PluginImageMath.dox` for worked examples. Key headers: `Tpl/Array.h`,
`Tpl/ExprBaseTpl.h`, `Utils/ForwardDeclarations.h`, `Utils/Helpers.h`.

## Core model

```cpp
makeArray<T=void>(img,
    bool ignoreShiftAndScale = false,   // see Shift/scale
    MagFilter magFilter = MagFilter::Nearest, // GPU only; CPU always Nearest
    Wrap wrap = Wrap::ClampToEdge,       // ClampToEdge | ClampToBorder | Repeat
    vec4f borderColor = vec4f::Zero());  // for ClampToBorder
```

Returns `Array` leaf holding `T& m_img` (reference). Operators build expression trees storing
children **by value**. Evaluation fires only on `Array::operator=`.

`DeviceStrategy` is auto-determined per leaf (see GPU dispatch), overridable via
`.forceCPU()` / `.forceGPU()` / `setDeviceStrategy()`.

`auto` is safe for intermediates — danger only from temporaries whose owner is destroyed:

```cpp
auto tmp = algo.process(input);          // keep owner alive
auto ok  = makeArray<float>(*tmp) + rhs; // safe
// auto bad = makeArray<float>(*algo.process(input)) + rhs; // DANGLING
```

## SharedImageSet vs SharedImage

`makeArray(sis)` **assumes all images in the set have the same type and size**. If not, process
each `SharedImage` individually. Element-wise operations run per-image (each image independently).
**Reductions aggregate across all images**: `.sum()` sums all voxels in all selected images,
`.min()`/`.max()` find the global extremum (arg output includes image index in 4th component).
Selection is respected — unselected images are skipped.
Each `SharedImage` in a SIS can have its own world matrix; `imgDesc()` returns the focused image's
descriptor (default focus=0). `getShared()`/`get()` without index also return the focused image.

## Capabilities (see dox for details)

`+` `-` `*` `/` comparisons `&&` `||` unary `-` |
`.abs()` `.exp()` `.log()` `.pow2()` `.sqrt()` `.sin()` `.cos()` |
`.pow()` `.min()` `.max()` `.clamp()` `.divideIfNotZero()` |
`.cast<T>()` | `cond.select(a, b)`
**Scalars**: C++ arithmetic types and `Eigen::Vector` are auto-wrapped by operator overloads —
`2.0 * expr` and `expr * 2.0` both work. `makeScalar()`/`makeChannelWiseScalar()` only needed
for standalone scalar expressions (e.g., `makeChannelWiseScalar(vec3(...)).toDeformation(desc)`).

**Reductions** (immediate, accumulated in `double`, → `Eigen::VectorXd` — no overflow risk):
`.sum()` `.prod()` `.min(&arg)` `.max(&arg)` `.mean()` `.l1Norm()` `.l2Norm()` `.lpNorm(p)` `.lInfNorm()`.
**Channel reductions** (lazy): `.channelSum()` `.channelMax()` `.length()` etc.
**Swizzle**: `.x()` `.rgb()` `.channelSwizzle({})` `.streamChannels(n)` `combineChannels(...)`. Read+write.
**Block views**: `.block(offset, size)` — sub-region/broadcasting. CPU aliasing caveat.
**Coordinates**: `makeCoordinates(img, CoordinateType::World|Pixel|Image|Texture)` → 3ch.
**Resampling**: `expr.resample(inDesc, outDesc)`. CPU=nearest only; GPU may=linear — results differ.
**Masking**: `makeMaskLeaf(expr, mask)`, `expr.toMask()`.
**Deformations**: `DeformationLeaf(si, def)`, `expr.toDeformation(desc)`, `resample<true>(...)`.
**Gradients**: no built-in — use block-view offsets + `Wrap::ClampToBorder`.
**Custom ops**: `.unaryOp()`/`.binaryOp()` (functors/lambdas), `GlExpr` (GLSL).

## Type system

**Typed** `makeArray<float>(sis)`: compile-time `img_type`. **ASSERT if T ≠ actual PixelType.**
**Untyped** `makeArray(sis)` (`T=void`): dispatched by LHS `pixelType`. **ASSERT if any untyped leaf's type ≠ LHS type.**
Mixing typed + untyped is fine — typed leaves are independent of LHS dispatch.

## Shift/scale

`ignoreShiftAndScale` (default `false`):
- `false` → per-voxel `storageToOriginal`/`originalToStorage` (physical domain).
- `true` → raw storage values. Use for labels/masks or to signal raw-value intent.

Only matters semantically when shift/scale is non-trivial (e.g., `short` with DICOM HU offset).
No performance difference (GPU always computes with uniforms; CPU cost is negligible).
`uint8` labels, `float` maps, `evaluateIntoImage(true)` output typically have trivial 0/1 —
both flags give identical results. Don't flag working code that uses the default.
All leaves in one expression must use the same flag — mixing is silently wrong.

## GPU vs CPU dispatch

| Condition | Strategy | Notes |
|-----------|----------|-------|
| `TypedImage` leaf | `ForceCPU` | OpenMP, `double` precision |
| `SharedImage`/`SIS`, ch≤4, not `double`/`int`/`uint` | `Auto` | GPU if `hasGl()` |
| ch>4 or `double`/`int`/`uint` | `ForceCPU` | `vec4` shader limit |

Override: `.forceCPU()` > `.forceGPU()` > `Auto`.
**Precision**: CPU=`double`, GPU=`float` (integer results can differ by 1).
**Clamping**: OpenGL clamps to representable range; CPU does not — results differ at extremes.

**`prepare(shiftOnly=true)`**: `short`→`ushort` (shift), `double`→`float`. Makes images GPU-eligible.
`int`/`uint` convert only if range fits `ushort` (≤65535), else no-op. `SharedImageSet` forces `shiftOnly=true`.

## Memory & aliasing

`sharedMem()`/`mem()` auto-sync from GL; `hasMem()` checks without sync.
ImageMath auto-syncs internally — **no manual `syncMem()` before expressions**.
Manual `syncMem()` only before direct `pointer()` access outside ImageMath.

Element-wise self-assignment: **safe** on CPU. Block views with shifted offsets: **unsafe**.
Channel swizzle writes: aliasing warning. GPU: always safe.
`+=`/`-=`/`*=`/`/=` expand to `lhs = lhs op rhs` — same aliasing rules.

## `evaluateIntoImage`

```cpp
auto result = (makeArray(sis0) + makeArray(sis1)).evaluateIntoImage<float>(true);
```

Template = output `PixelType` (`void` = inferred). `clearShiftScale=true` zeros shift/scale.

**Warning**: output uses `ImageDescriptor` (spacing/dims preserved) but **not `ImageDescriptorWorld`**
— world matrix defaults to identity. Fix:

```cpp
for (size_t i = 0; i < result->size(); ++i)
    result->get(i)->setMatrix(source->get(i)->matrix());
```

## Direct voxel access (non-ImageMath)

For single-voxel, sparse, or neighbor-access patterns, use `MemImage`/`TypedImage`/`Utils::typeSwitch` directly.
See the **`work-with-image-data`** skill — section 4 covers type-erased access, typed pointer access, `TypeSwitcher`, and image creation.

See also `ImageDescriptor::index()`/`coord()` in `<ImFusion/Base/ImageDescriptor.h>`.

## Common patterns

```cpp
// Accumulate masks (wider type avoids uint8 overflow):
makeArray<float>(*sum, true) += makeArray<uint8_t>(*mask, true).cast<float>();
// Threshold to binary mask:
makeArray<uint8_t>(*dst, true) = (makeArray<float>(*src) > thresh).cast<uint8_t>();
// Scalar sum:
double total = makeArray<uint8_t>(*mask, true).sum()[0];
// Conditional blend:
makeArray(res) = (makeArray(m) > 0.0).select(makeArray(a), makeArray(b));
// evaluateIntoImage + restore world matrix:
auto prob = (makeArray<float>(*src) * 0.5f + 0.5f).evaluateIntoImage<float>(true);
for (size_t i = 0; i < prob->size(); i++)
    prob->get(i)->setMatrix(src->get(i)->matrix());
```

## Pitfalls checklist

1. **Shift/scale on non-trivially-scaled images** — only a real bug when shift/scale ≠ 0/1 (e.g., integer DICOM with HU offset). Trivially-scaled `uint8` labels or `float` maps are safe with either flag.
2. **Mixing shift/scale flags across leaves** — silently wrong results; all leaves must agree.
3. **Type mismatch asserts** — typed T ≠ actual type, or untyped leaf ≠ LHS type.
4. **GPU clamps, CPU doesn't** — results differ at extremes.
5. **`originalToStorage` rounds** — integer rounding to nearest storage value.
6. **Block-view aliasing on CPU** — undefined with shifted overlapping regions.
7. **`auto` captures expression tree, not result** — must assign to `Array` LHS to evaluate.
8. **Debug perf** — CPU expressions very slow without optimizations.
9. **Forced CPU types** — `double`/`int`/`uint`/ch>4 bypass GPU (`vec4` limit).
10. **Resampling CPU≠GPU** — CPU=nearest, GPU may=linear.
11. **`evaluateIntoImage` drops world matrix** — copy `setMatrix()` manually.