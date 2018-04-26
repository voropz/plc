#include <unordered_map> 
#include <string> 
#include <functional> 
#include <iostream> 
#include <exception> 

struct Object;
typedef std::unordered_map<std::string, std::function<void(Object*)>> Vtable;

struct Object {
	Vtable* vtablePtr;
	Object* base = nullptr;

	friend void virtual_call(void* object, const std::string& method);
};

// -------------------------

#define VIRTUAL_CLASS(class_name)\
	struct class_name { \
		Vtable* vtablePtr;\
		Object* base = nullptr;\
		\
		static Vtable vtable;\
		\
		Base(int a = 0)\
			:vtablePtr(&Base::vtable), a(a) {}\
		static void declare_method(const std::string& name);

// -------------------------

#define END(class_name, variable_name)\
	 }; \
	Vtable class_name::vtable; \
\
void class_name::declare_method(const std::string& name) {\
	std::function<void(Object* obj)> func = [name](Object* obj) {\
		class_name* me = reinterpret_cast<class_name*>(obj);\
		std::cout << #class_name << "::" << name << "\t" << me->variable_name << "\n"; };\
	vtable.insert({ name, func });\
}

// -------------------------

#define VIRTUAL_CLASS_DERIVED(class_name, base_name)\
	struct class_name {\
		Vtable* vtablePtr; \
		Base* base; \
	\
		static Vtable vtable; \
	\
		class_name(int b = 1)\
			:vtablePtr(&Derived::vtable), b(b), base(new base_name()) {}\
		~class_name() {}\
		static void declare_method(const std::string& name);

// -------------------------

void virtual_call(void* ptr, const std::string& method) {
	Object* object = reinterpret_cast<Object*>(ptr);
	Vtable* vtable;
	std::function<void(Object*)> func;

	do {
		vtable = object->vtablePtr;
		try {
			func = vtable->at(method);
			break;
		}
		catch (std::out_of_range& e) {
			object = reinterpret_cast<Object*>(object->base);
		}
	} while (object != nullptr);

	func(object);
}

#define VIRTUAL_CALL(ptr, func) virtual_call(ptr,func)

// -------------------------

#define DECLARE_METHOD(class_name, name) class_name::declare_method(#name)  