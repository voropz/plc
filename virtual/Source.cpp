#include "virtual_header.h"

VIRTUAL_CLASS(Base1)
	int a;
END(Base1)

VIRTUAL_CLASS_DERIVED(Derived2, Base1)
	int b;
END(Derived2)

int main() {
	DECLARE_METHOD(Base1, both, std::cout << "BOTH " << _this->a << std::endl;);
	DECLARE_METHOD(Base1, base, std::cout << "BASE " << _this->a << std::endl;);
	DECLARE_METHOD(Derived2, both, std::cout << "BOTH " << _this->b << std::endl;);
	DECLARE_METHOD(Derived2, der, std::cout << "DER " << _this->b << std::endl;);

	Base1 base;
	base.a = 42;
	Derived2 derived;
	derived.b = 24;
	derived.base->a = 100500;
	Base1* test = reinterpret_cast<Base1*>(&derived);

	VIRTUAL_CALL(&base, "both"); // base.a = 42
	VIRTUAL_CALL(test, "both");  // derived.b = 24
	VIRTUAL_CALL(test, "base");  // derived.base.a = 100500
	VIRTUAL_CALL(test, "der");  // derived.b = 24
	system("pause");

	VIRTUAL_CALL(&base, "der");  // падает
}