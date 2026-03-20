// Example ML Operation implementation
#include "ml-operation-header-template.h"

using namespace ImFusion;
using namespace ImFusion::ML;

ExampleOperation::ExampleOperation(int kernelSize)
: Operation("ExampleOperation", ProcessingPolicy::Everything)
{
	p_kernelSize = kernelSize;

	// Example of emitting a signal when parameter changes (pattern):
	//p_kernelSize.signalValueChanged.connect([this]() { /* do something here */ });
}

std::shared_ptr<SharedImageSet> ExampleOperation::processImages(std::shared_ptr<SharedImageSet> input) const
{
	if (inputIsEmptyOrNull(input.get()))
		return input;

	// ... perform work; respect computing device if applicable
	return input;
}


