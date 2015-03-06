#include <foo.h>
#include "bar.g"

namespace Outer {
namespace Inner {

//----------------------------------------------------------------------------
// Enums
//----------------------------------------------------------------------------
enum Foo { a = 1,	b = 2,	c = 3};

//----------------------------------------------------------------------------
// Typedefs
//----------------------------------------------------------------------------
typedef int foo;

//----------------------------------------------------------------------------
// Classes
//----------------------------------------------------------------------------
/* 
	Class multiline comment
	with a really very long line which is longer than this but not as long as a piece of long string which maybe longer depending on the length of it or shorter depending.
*/
class TestClass {
public:
	// single line comment
	TestClass();
	TestClass(int this, int has, int many, int parameters);
	TestClass(int this, int has, int many, int parameters, int that, int stretch, int over, int the, int column, int limit, int which, int is, int one_twenty, int characters);

	void TestFunction(int this, int has, int many, int parameters);
	void TestFunction(int this, int has, int many, int parameters, int that, int stretch, int over, int the, int column, int limit, int which, int is, int one_twenty, int characters);

	struct Hello {
		int a; // comment
		int b; // comment
		int c; // comment
	};

	template<class T>
	int TFunc(T & in, T * out);

	int single_line_func()
	{
		return 0;
	}
};

TestClass::TestClass()
{

}
TestClass::TestClass(int this, int has, int many, int parameters)
{}
TestClass::TestClass(int this, int has, int many, int parameters, int that, int stretch, int over, int the, int column, int limit, int which, int is, int one_twenty, int characters)
{

}

void TestClass::TestFunction(int this, int has, int many, int parameters)
{}
void TestClass::TestFunction(int this, int has, int many, int parameters, int that, int stretch, int over, int the, int column, int limit, int which, int is, int one_twenty, int characters) {}

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Templates
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

template<class Foo> 
class T
{
};



template<int this, int has, int many, int parameters>
class T
{};

template<int this, int has, int many, int parameters, int that, int stretch, int over, int the, int column, int limit, int which, int is, int one_twenty, int characters>
class T
{};


///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Statements
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

void Function()
{
	// switch statements
	switch(3)
	{
		case 0 : break;
		case 1 : break;

		default : break;
	}

	// if statements
	if(true)
	{

	}

	if()
	{

	}

	if(true)
		hello();

	if()
		hello();

	// for statements
	for(int i = 0, c = 0; i < 5; ++i)
	{}

	
	// do 
	do {
		foo();
	} while(bar);

	// function calls
	foo(param);
	foo();
	foo(param1, param2, param3, param4);
	foo(this, has, many, parameters, that, stretch, over, the, column, limit, which, is, one_twenty, characters, but, we, need, to, use, quite, a, lot);
}

} // end namespace Inner
} // end namespace Outer

