---
name: create-imfusion-algorithm
description: Create C++ Algorithm classes following the ImFusion SDK pattern. Use when the user wants to implement a new algorithm, image processing operation, or data transformation that inherits from the Algorithm base class.
---

# Create ImFusion Algorithm

Guide for creating Algorithm subclasses following ImFusion SDK conventions.

For generic C++ conventions and the baseline algorithm lifecycle contract, apply the `cpp-guidelines` and `algorithm-pattern` project rules.

## Gather Requirements

Before creating the algorithm, determine:

1. **Input data type**: SharedImageSet (2d or 3d?), Mesh, PointCloud, TrackingSequence, etc.
2. **Output data type**: Same options as input
3. **Algorithm category**: Processing, I/O, Registration, Segmentation
4. **Modality constraints**: CT, MRI, US, or any (NA)
5. **Parameters**: Configuration values the algorithm needs

## Key Implementation Points

### createCompatible() Guidelines

- Return `false` early if data doesn't match requirements
- Unless otherwise specified, accept `Modality::NA` for flexibility with 2D/3D data
- Unless otherwise specified, accept `Data::IMAGE` and `Data::VOLUME` for flexibility with unknown data dimension
- Only create instance when `a` pointer is non-null

### compute() Guidelines

- Reset output at start: `m_output.reset()`
- Set `m_status = Status::Error` initially
- Use `m_status = Status::Success` only after successful completion
- Report progress for long operations via `setProgress()`
- Use appropriate log category: `Module.Namespace.ClassName`

### Parameter Declaration

```cpp
Parameter<double> p_threshold = {"threshold", 100.0, this};
Parameter<int> p_iterations = {"iterations", 10, this};
Parameter<bool> p_enabled = {"enabled", true, this};
Parameter<std::string> p_mode = {"mode", "default", this};
```

### Adding Actions

Actions are particularly useful when the algorithm is associated to a `DefaultAlgorithmController`.
This controller will automatically add a button that will let the user call that function.

```cpp
// In constructor
registerAction("myAction", "Run Action", &MyAlgorithm::runAction);

// Action method
Algorithm::Status MyAlgorithm::runAction()
{
	// Action implementation
	return Status::Success;
}
```

## Factory Registration

Register the algorithm in your plugin's AlgorithmFactory:

```cpp
registerAlgorithm<MyAlgorithm>("MyAlgorithm", "Category;My Algorithm Name");
```

## Checklist

- [ ] Parameters use `Parameter<T>` with descriptive names
- [ ] `createCompatible()` validates input correctly
- [ ] `compute()` resets output and sets status
- [ ] Log category follows `Module.Namespace.ClassName` pattern
- [ ] Algorithm registered in factory

## Related Rules

- See the `algorithm-pattern` project rule for additional patterns
- See the `cpp-guidelines` project rule for C++ conventions
