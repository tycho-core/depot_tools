@include("cpp_copyright_comment")

@include("cpp_includes_comment")
#include "core/pc/safe_windows.h"

#ifdef _MANAGED
#pragma managed(push, off)
#endif

BOOL APIENTRY DllMain( HMODULE /*hModule*/,
                       DWORD  /*ul_reason_for_call*/,
                       LPVOID /*lpReserved*/
					 )
{
    return TRUE;
}

#ifdef _MANAGED
#pragma managed(pop)
#endif


