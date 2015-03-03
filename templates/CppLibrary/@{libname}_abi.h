@require(libname, libname_upper, header_guard)
@include("cpp_copyright_comment")

#if _MSC_VER > 1000
#pragma once
#endif  // _MSC_VER

#ifndef @{header_guard}
#define @{header_guard}

@include("cpp_includes_comment")


#if TYCHO_PC

// DLL interface
#ifdef TYCHO_@{libname_upper}_EXPORTS
#define TYCHO_@{libname_upper}_ABI __declspec(dllexport)
#else
#define TYCHO_@{libname_upper}_ABI __declspec(dllimport)
#endif 

// disable a few warnings globally. should move these into specific cpp's to avoid polluting
// user header files
#pragma warning(disable : 4251) // class needs to have dll-interface to be used by clients of class ''
#pragma warning(disable : 4355) // 'this' : used in base member initializer list

#else // TYCHO_PC

#define TYCHO_@{libname_upper}_ABI

#endif // TYCHO_PC


#endif // @{header_guard}
