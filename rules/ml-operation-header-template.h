// Example ML Operation header following ImFusion conventions
#pragma once

#include <ImFusion/ML/Operation.h>

namespace ImFusion
{
	namespace ML
	{
		class ExampleOperation : public Operation
		{
		public:
			// Provide defaults so the type is default-constructible; pass parameters in ctor
			explicit ExampleOperation(int kernelSize = 3);

		protected:
			// Override relevant delegate(s)
			std::shared_ptr<SharedImageSet> processImages(std::shared_ptr<SharedImageSet> input) const override;

		public:
			// Public parameter with p_ prefix
			OpParam<int> p_kernelSize = {"kernelSize", 3, this, ParamRequired::No};
		};
	}
}


