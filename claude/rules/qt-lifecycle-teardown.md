<!-- Auto-generated from cursor/rules/qt-lifecycle-teardown.mdc — do not edit directly -->

# Qt Lifecycle and Teardown Safety

- For objects with non-trivial destructors (controllers, annotation widgets), do not rely on implicit Qt child destruction if order matters.
- If a child destructor accesses the parent window, display state, or GL resources, destroy that child explicitly in the owner destructor first.

## Required Pattern for Manual Teardown

- Remove from layout (`removeWidget`), detach (`setParent(nullptr)`), then `delete`.
- Avoid half-manual ownership (`removeWidget` alone) for QObject trees.
- After explicit delete, null member pointers used during shutdown paths.

## `createWindowContainer` Rule

- `QWidget::createWindowContainer(window, parent)` takes ownership of `window`.
- Do not keep a second owning handle to that embedded `QWindow` (`std::unique_ptr`, `QScopedPointer`, manual `delete`, or another Qt owner).
- If later access is needed, store the embedded window as a non-owning pointer/member and treat the container widget as the sole owner.
- During teardown, explicitly destroy the container first if ordering matters, then null any non-owning pointers to the embedded window.
- If close-time crashes involve Qt/GL teardown, prefer explicit destruction of the container in owner destructor before base-class teardown.

## Close-Crash Checklist

- Verify destructor order: owner -> controllers -> child widgets.
- Verify no destructor calls into already-destroyed parent window internals.
- Check for double-destruction paths from mixed Qt-parent and manual deletion.
- Keep fixes minimal and targeted to ownership/order, not behavioral logic.