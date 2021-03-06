@require(libname, header_guard)
@include("cpp_copyright_comment")

#if _MSC_VER > 1000
#pragma once
#endif  // _MSC_VER

#ifndef @{header_guard}
#define @{header_guard}

@include("cpp_includes_comment")
#include "@{libname}/@{libname}_abi.h"

@include("cpp_class_comment")

namespace tycho
{
namespace @{libname}
{

	
} // end namespace
} // end namespace

#endif // @{header_guard}
