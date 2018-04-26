#include "virtual_header.h"

VIRTUAL_CLASS(Base)
	int a;
END(Base, a)

VIRTUAL_CLASS_DERIVED(Derived, Base)
	int b;
END(Derived, b)

int main() {
	DECLARE_METHOD(Base, both);
	DECLARE_METHOD(Base, base);
	DECLARE_METHOD(Derived, both);
	DECLARE_METHOD(Derived, der);

	Base base;
	base.a = 42;
	Derived derived;
	derived.b = 24;
	derived.base->a = 100500;
	Base* test = reinterpret_cast<Base*>(&derived);

	VIRTUAL_CALL(&base, "base"); // base.a = 
	VIRTUAL_CALL(test, "both");  // derived.b = 
	VIRTUAL_CALL(test, "base");  // derived->base.a = (0 по умолчанию)
	VIRTUAL_CALL(test, "der");  // derived.b = 
	system("pause");

	VIRTUAL_CALL(&base, "der");  // падает
}