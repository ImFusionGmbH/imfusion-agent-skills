---
name: implement-visualization
description: Create custom OpenGL visualization for data types in ImFusion SDK. Use when implementing custom rendering, creating view objects, or adding visual overlays to displays.
---

# Implement Custom Visualization

Guide for creating custom OpenGL rendering and visualization in ImFusion SDK.

## Visualization Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DISPLAY HIERARCHY                        │
│                                                              │
│  DisplayWidgetMulti                                          │
│      │                                                       │
│      ├── View (2D/3D viewport)                               │
│      │      │                                                │
│      │      ├── ViewObject (wraps GlObject for GUI)          │
│      │      │      └── GlObject (OpenGL rendering)           │
│      │      │                                                │
│      │      └── ViewOverlay (2D annotations)                 │
│      │             └── GlAnnotation (OpenGL 2D)              │
│      │                                                       │
│      └── View (another viewport)                             │
│             └── ...                                          │
└─────────────────────────────────────────────────────────────┘
```

## Creating a GlObject

### Header File

```cpp
#pragma once

#include <ImFusion/GL/GlObject.h>
#include <MyPlugin/Config.h>

namespace ImFusion
{
	/// Custom OpenGL object for rendering analysis results.
	class MY_PLUGIN_API GlMyVisualization : public GlObject
	{
	public:
		explicit GlMyVisualization(MyCustomData& data);
		virtual ~GlMyVisualization();

		// GlObject interface
		void render(const GlRenderParameters& params) override;
		Box3 boundingBox() const override;

		// Configuration
		void setColor(const vec4& color) { m_color = color; }
		vec4 color() const { return m_color; }

	private:
		void initializeGL();
		void updateBuffers();

		MyCustomData& m_data;
		vec4 m_color{1.0f, 0.0f, 0.0f, 1.0f};
		
		// OpenGL resources
		std::unique_ptr<GlBuffer> m_vertexBuffer;
		std::unique_ptr<GlVertexArray> m_vao;
		bool m_needsUpdate = true;
	};
}
```

### Implementation File

```cpp
#include "GlMyVisualization.h"

#include <ImFusion/GL/GlBuffer.h>
#include <ImFusion/GL/GlProgram.h>
#include <ImFusion/GL/GlStateGuard.h>
#include <ImFusion/GL/GlVertexArray.h>

#undef IMFUSION_LOG_DEFAULT_CATEGORY
#define IMFUSION_LOG_DEFAULT_CATEGORY "MyPlugin.GlMyVisualization"

namespace ImFusion
{
	GlMyVisualization::GlMyVisualization(MyCustomData& data)
		: m_data(data)
	{
	}

	GlMyVisualization::~GlMyVisualization() = default;

	void GlMyVisualization::initializeGL()
	{
		if (m_vao)
			return;

		m_vao = std::make_unique<GlVertexArray>();
		m_vertexBuffer = std::make_unique<GlBuffer>(GL_ARRAY_BUFFER);
		
		m_vao->bind();
		m_vertexBuffer->bind();
		
		// Setup vertex attributes
		glEnableVertexAttribArray(0);
		glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(vec3), nullptr);
		
		m_vao->unbind();
	}

	void GlMyVisualization::updateBuffers()
	{
		if (!m_needsUpdate)
			return;

		// Generate vertex data from m_data
		std::vector<vec3> vertices;
		// ... populate vertices from data ...

		m_vertexBuffer->bind();
		m_vertexBuffer->setData(vertices);
		m_vertexBuffer->unbind();

		m_needsUpdate = false;
	}

	void GlMyVisualization::render(const GlRenderParameters& params)
	{
		initializeGL();
		updateBuffers();

		// Save and set OpenGL state
		GlStateGuard guard;
		guard.enable(GL_DEPTH_TEST);
		guard.enable(GL_BLEND);
		glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);

		// Get or create shader program
		GlProgram* program = GlProgramManager::get().program("MyVisualization");
		if (!program)
		{
			LOG_ERROR("Shader program not found");
			return;
		}

		program->bind();
		program->setUniform("u_color", m_color);
		program->setUniform("u_mvp", params.mvp());

		m_vao->bind();
		glDrawArrays(GL_TRIANGLES, 0, m_vertexCount);
		m_vao->unbind();

		program->unbind();

		GLCHECK;
	}

	Box3 GlMyVisualization::boundingBox() const
	{
		// Return bounding box of visualization
		return Box3(vec3(-10), vec3(10));
	}
}
```

## Creating a DataDisplayHandler

```cpp
class MyDataDisplayHandler : public DataDisplayHandler
{
public:
	bool canHandle(const Data& data) const override
	{
		return dynamic_cast<const MyCustomData*>(&data) != nullptr;
	}

	std::vector<ViewObject*> createViewObjects(
		Data& data,
		DisplayWidgetMulti& display
	) const override
	{
		auto& myData = static_cast<MyCustomData&>(data);
		
		std::vector<ViewObject*> objects;
		
		// Create GlObject
		auto glObj = std::make_unique<GlMyVisualization>(myData);
		
		// Wrap in ViewObject for all 3D views
		for (auto* view : display.views())
		{
			if (auto* view3D = dynamic_cast<ImageView3D*>(view))
			{
				auto* viewObj = new ViewObject(std::move(glObj));
				view3D->addViewObject(viewObj);
				objects.push_back(viewObj);
			}
		}
		
		return objects;
	}
};

// Register in plugin init()
DisplayManager::get().registerHandler(
    std::make_unique<MyDataDisplayHandler>()
);
```

## Creating ViewOverlay (2D Annotations)

```cpp
class MyOverlay : public ViewOverlay
{
public:
	explicit MyOverlay(View& view)
		: ViewOverlay(view)
	{
	}

	void render(const GlRenderParameters& params) override
	{
		// 2D rendering in screen coordinates
		GlStateGuard guard;
		guard.disable(GL_DEPTH_TEST);

		// Draw text
		m_font.renderText("Status: OK", vec2(10, 10), vec4(1, 1, 1, 1));

		// Draw 2D shapes
		drawRectangle(vec2(100, 100), vec2(200, 150), vec4(1, 0, 0, 0.5f));

		GLCHECK;
	}

private:
	GlFont m_font;
};
```

## GLSL Shaders

### Vertex Shader (MyVisualization.vert)

```glsl
#version 330 core

layout(location = 0) in vec3 in_position;

uniform mat4 u_mvp;

void main()
{
    gl_Position = u_mvp * vec4(in_position, 1.0);
}
```

### Fragment Shader (MyVisualization.frag)

```glsl
#version 330 core

uniform vec4 u_color;

out vec4 out_color;

void main()
{
    out_color = u_color;
}
```

### Registering Shaders

```cpp
// In plugin init or GlObject initialization
GlProgramManager::get().registerProgram(
    "MyVisualization",
    "MyVisualization.vert",
    "MyVisualization.frag"
);
```

## OpenGL Best Practices

### State Management

```cpp
void render(const GlRenderParameters& params)
{
    // Always use GlStateGuard
    GlStateGuard guard;
    
    // Set required state
    guard.enable(GL_DEPTH_TEST);
    guard.enable(GL_BLEND);
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    
    // Render...
    
    // State automatically restored when guard goes out of scope
}
```

### Error Checking

```cpp
// At end of render method
GLCHECK;  // Checks for OpenGL errors
```

### Context Management

```cpp
// Ensure GL context is active (for background operations)
if (!GlContextManager::get().hasActiveContext())
{
    GlContextManager::get().acquireContext();
    // ... GL operations ...
    GlContextManager::get().releaseContext();
}
```

## Interactive Views

### Handling Mouse Events

```cpp
class MyInteractiveView : public InteractiveView
{
public:
	void mousePressEvent(QMouseEvent* event) override
	{
		if (event->button() == Qt::LeftButton)
		{
			vec2 screenPos(event->pos().x(), event->pos().y());
			vec3 worldPos = screenToWorld(screenPos);
			// Handle click...
		}
	}

	void mouseMoveEvent(QMouseEvent* event) override
	{
		// Handle drag...
	}
};
```

### Picking Objects

```cpp
// In render, encode object IDs for picking
void renderForPicking(const GlRenderParameters& params)
{
    // Render with unique colors per object
    int objectId = 1;
    vec4 idColor = encodeId(objectId);
    program->setUniform("u_color", idColor);
    // Render...
}

// Query picked object
int pickedId = view.pickObject(screenPos);
```

## Performance Tips

1. **Minimize state changes**: Group draws by shader/state
2. **Use VAOs**: Cache vertex array setup
3. **Batch rendering**: Combine multiple objects when possible
4. **Frustum culling**: Skip objects outside view
5. **Level of detail**: Simplify distant objects

## Checklist

- [ ] GlObject implements `render()` and `boundingBox()`
- [ ] Uses `GlStateGuard` for state management
- [ ] Calls `GLCHECK` at end of render
- [ ] Shaders follow naming conventions (.vert, .frag)
- [ ] DataDisplayHandler registered for custom data
- [ ] Context management for background operations
- [ ] Resources cleaned up in destructor

## Related Rules

- See `.cursor/rules/glsl-shaders.mdc` for shader conventions
- See `AGENTS.md` OpenGL section for additional guidelines
