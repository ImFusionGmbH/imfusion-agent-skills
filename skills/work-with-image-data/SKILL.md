---
name: work-with-image-data
description: >-
  Choose the right approach to process, transform, or access image data in the
  ImFusion SDK. Use when normalizing, thresholding, filtering, resampling, or
  reading/writing pixel values on SharedImage, SharedImageSet, MemImage, or
  TypedImage — covers ML Operations, built-in Algorithms, ImageMath, and
  low-level TypedImage/TypeSwitcher access.
---

# Image Intensity Manipulation

Consider the following options, in this order:
```
Need to manipulate image intensities?
│
├─► 1. Does an ML Operation exist for this?  →  use it (ML::Operation)
│
├─► 2. Does a built-in Algorithm exist?      →  use it directly (or via the FactoryRegistry if necessary)
│
├─► 3. Can it be expressed as a formula?     →  use ImageMath (see imfusion-imagemath skill)
│
└─► 4. Sparse/structural access needed?      →  use MemImage / TypedImage / TypeSwitcher
```

---

## 1. ML Operations

`ML::Operation`s are simple transforms for images, tensors and keypoints. They can be applied to a single data or to a `ML::DataItem`.
They have a clear interface and are well-tested.

**Discovering available operations**: browse `ImFusion/ML/Operations/` headers, or search
the Python bindings (`imfusion.ml` module) for the full list with docstrings.

```cpp
#include <ImFusion/ML/Operations/NormalizeOperation.h>


auto op = std::make_shared<ML::NormalizePercentileOperation>();
op->p_minPercentile = 0.05f;
op->p_maxPercentile  = 0.95f;
op->p_clamp = true;

ML::DataItem item;
item.addImage("image", sharedImage);
pipeline.process(item);
auto* result = item.getImage("image");
```
or as a one-liner
```cpp
image = ML::NormalizePercentileOperation(0.05f, 0.95f, true).process(std::move(image));
```
Note that `ML::Operation` support both unique_ptr and shared_ptr as input.

`ML::Operation` are particularly relevant for pre/post-processing pipelines (since they can be chained via `ML::OperationsSequence`) or when Python interop matter.

---

## 2. Built-in Algorithms

Some more transforms are only available as `Algorithm`.
They are typically more advanced/complex, but the interface is more ambiguous.
Unlike `ML::Operation` it is sometimes not obvious to know whether they work in-place or not. Check if there is an in-place parameter.

Algorithms can be either directly instantiated

```cpp
#include <ImFusion/Base/MeshToLabelMapAlgorithm.h>

MeshToLabelMapAlgorithm algo(input);
algo.p_marginPx = 15;
algo.compute();
auto res = algo.takeOutput().extractFirstImage();
```

or via the algorithm factory
```cpp
#include <ImFusion/Base/FactoryRegistry.h>

std::unique_ptr<Algorithm> alg = FactoryRegistry::get().instantiateAlgorithm("ImFusion.MeshToLabelMapAlgorithm", DataList{input});
if (algo)
{
    Properties config;
    config.setParam("marginPx", 15);
    algo->configure(config);
    algo->compute();
    auto res = algo->takeOutput().extractFirstImage();
}
```
Prefer the direct instantiation, unless the algorithm lives in another plugin on which you do not want to introduce a hard dependency.

Search for available algorithms via `FactoryRegistry::get().compatibleDescriptors(inputData)`.

---

## 3. ImageMath

For dense, vectorized, expression-template-based operations on `SharedImage` /
`SharedImageSet` / `TypedImage`. Automatically dispatches to GPU when eligible.

See the **`imfusion-imagemath`** skill for the complete API reference (type system, GPU dispatch, reductions, resampling, pitfalls).

Quick example:

```cpp
#include <ImFusion/ImageMath/SharedImageSetArithmetic.h>

// Normalize to [0, 1]
auto [minV, maxV] = si->sharedMem()->getRangeDouble();
makeArray<float>(*si) = (makeArray<float>(*si) - minV) / (maxV - minV);

// Threshold to binary mask
makeArray<uint8_t>(*mask, true) = (makeArray<float>(*src) > threshold).cast<uint8_t>();
```

Prefer ImageMath over low-level access whenever the operation is expressible as an
element-wise or reduction formula — it is faster, shorter, and GPU-capable.

---

## 4. Low-level: MemImage / TypedImage / TypeSwitcher

Use when:
- You need to read/write individual pixels or sparse neighborhoods
- The logic involves conditional branching per voxel that ImageMath cannot express

### Type-erased access (any type, slower)

`MemImage` provides type-erased `double` accessors. Use for simple, infrequent access.

```cpp
MemImage* mem = si->sharedMem().get();
// Read
double v = mem->valueDouble(x, y, z, channel);
// Write
mem->setValueDouble(newValue, x, y, z, channel);
```

Avoid calling `valueDouble(x,y,z,c)` in tight loops — the coordinate-to-index computation is slow. Prefer the `index`-based overload with a manually incremented index, or use the typed pointer directly (see below).

### Typed access (known type, fastest)

When you know the pixel type at compile time:

```cpp
auto* typed = si->sharedMem()->typed<float>(); // returns nullptr if wrong type
if (!typed) return;

float* ptr = typed->pointer(); // layout: c + ch*(x + w*(y + h*z))
const auto& desc = typed->descriptor();
int w = desc.width(), h = desc.height(), d = desc.slices(), ch = desc.channels();

for (int z = 0; z < d; ++z)
    for (int y = 0; y < h; ++y)
        for (int x = 0; x < w; ++x)
            ptr[0 + ch * (x + w * (y + h * z))] *= 2.0f; // channel 0
```

Alternatively use the bounds-checked accessors:

```cpp
float v = typed->value(x, y, z, channel);
typed->setValue(newVal, x, y, z, channel);
```

### TypeSwitcher (unknown type at compile time)

Use `Utils::typeSwitch` to dispatch a typed lambda based on the runtime `PixelType`,
avoiding a manual switch statement over all types.

```cpp
#include <ImFusion/Base/Utils/TypeSwitcher.h>

MemImage* mem = si->sharedMem().get();

Utils::typeSwitch(*mem, [&](auto wrapper) {
    using T = typename decltype(wrapper)::type;
    auto* typed = static_cast<TypedImage<T>*>(mem);
    T* ptr = typed->pointer();
    const int n = typed->descriptor().numElements();
    for (int i = 0; i < n; ++i)
        ptr[i] = static_cast<T>(ptr[i] * 2);
});
```
The lambda must have a return type consistent across all branches (or `void`).

### Original (physical) vs Storage values

Direct pixel intensities access functions this will return raw (storage) values rather than original (physical) values.
This is important to consider when operating on several images, or when using a reference value (e.g. threshold an image with respect to 1000 Hounsfield units).
Use functions like `shift()`, `scale()` and `storageToOriginal()` to handle intensities consistently.

Refer to the C++ documentation `Pixel Value Domains` for more information.

---

## Pitfalls

- **Sync before pointer access**: call `si->syncMem()` to ensure GL→CPU sync before using `pointer()`. Call `si->setDirtyMem()` after you have modified it.
- **Pixel layout**: `c + ch*(x + w*(y + h*z))` — channels are innermost.
- **Shift/scale**: `valueDouble` returns *original* (physical) values applying shift/scale; `pointer()` gives raw storage values.
- **`typeSwitch` and `HFLOAT`**: `half-float` is handled as `float` — do not try to cast to a hypothetical `half` type.
