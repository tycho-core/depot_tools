@extends("cpp_header")
@require(classname, lib_abi)

@def header_content():
	@include("cpp_comment_dashed_line")
	// 
	@include("cpp_comment_dashed_line")
	class @{lib_abi} @{classname}
	{
	public:
		/// Default constructor
		@{classname}();
		
		/// Destructor
		~@{classname}();
		
	private:

	};
@end
