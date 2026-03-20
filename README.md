# ImFusion SDK Cursor Rules & Skills

This repository contains rules and skills to help external developers create plugins and applications with the ImFusion SDK.

*Rules* are like general coding guidelines that should be automatically requested when relevant.
On the other hand, *skills* are similar to tutorials and checklists that are invoked on demand for specific tasks.

## Recommended setup

It has been mostly developed for CursorAI. To use it, place it as a `.cursor` subfolder in the root of your project:
```
your-project-root/
├── .cursor/
│   ├── README.md
│   └── rules/
│       ├── ...
│   └── skills/
│       ├── ...
└── (your regular project files and folders)
```

For optimal use, we recommend to use Cursor workspaces that includes your project but also the ImFusion SDK install folder, as well as the public demos.
Cursor will then be able to index all three folders and provide better suggestions.

This is done by creating a file `your-project.code-workspace` and opening it in Cursor:

```json
{
	"folders": [
		{
			"path": "." // your project
		},
		{
			"path": "C:/Program Files/ImFusion/ImFusion Suite" // path to the install folder of the ImFusion SDK
		},
		{
			"path": "C:/public-demos" // path to the ImFusion SDK public demos (https://github.com/ImFusionGmbH/public-demos)
		}
	],
	"settings": {}
}
```

## Contributing

The number of skills should be kept as low as possible.

Rules and skills should not duplicate the information contained in the documentation, but focus on implicit knowledge, unexpected behaviour or repeated errors made by AI agents.

In general, LLM-generated skills are not useful, and can be sometimes erroneous or confusing.
