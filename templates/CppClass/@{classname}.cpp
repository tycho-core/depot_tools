@extends("cpp_source")
@require(classname)
@def cpp_includes():
#include "@{classname}.h"
@end

@def content():
	@include("cpp_comment_dashed_line")

	@{classname}::@{classname}()
	{

	}

	@include("cpp_comment_dashed_line")
	
	~@{classname}::@{classname}()
	{

	}

	@include("cpp_comment_dashed_line")
@end
