#include <string> 
#include <iostream> 
#include <cassert>
#include <vector>
#include <unordered_map>


enum BAD_CAST {
	not_siblings = -1,
	ambiguous = -2
};

#define deref(type, ptr)\
(*reinterpret_cast<type*>(ptr))

using Ptr = char*;
using Offset = int;

struct Typeinfo {
	std::string name;
	std::vector<Typeinfo*> parents;
	int parents_size;
	int size;
};

std::unordered_map<std::string, Typeinfo*> classes;

#define DECLARE_CLASS(CLASS)\
struct CLASS{\
	static Typeinfo type;\
\
	Offset parents_size = 0;\
	Offset next_pos = 0;\
    Typeinfo* typeinfo = &type;\
\
	CLASS() {\
		classes.emplace(#CLASS, &type);\
	}

#define END_CLASS(CLASS)\
};\
Typeinfo CLASS::type = { #CLASS,{}, 0, sizeof(CLASS) };

//--------------

#define DECLARE_DERIVED_CLASS(CLASS, PARENT)\
struct CLASS : PARENT {\
	static Typeinfo type;\
\
	Offset parents_size = sizeof(PARENT);\
	Offset next_pos = 0;\
	Typeinfo* typeinfo = &type;\
\
	CLASS() {\
		PARENT::next_pos = -PARENT::parents_size + sizeof(PARENT);\
		classes.emplace(#CLASS, &type);\
	}\

#define END_DERIVED_CLASS(CLASS, PARENT)\
};\
Typeinfo CLASS::type = { #CLASS, { &PARENT::type }, sizeof(PARENT), sizeof(CLASS) };

//----------

#define DECLARE_MULTIDERIVED_CLASS(CLASS, PARENT1, PARENT2)\
struct CLASS : PARENT1, PARENT2 {\
	static Typeinfo type;\
\
	int parents_size = sizeof(PARENT1) + sizeof(PARENT2);\
	int next_pos = 0;\
	Typeinfo* typeinfo = &type;\
\
	CLASS() { \
		PARENT1::next_pos = -PARENT1::parents_size + sizeof(PARENT1) + sizeof(PARENT2);\
		PARENT2::next_pos = -PARENT2::parents_size + sizeof(PARENT2);\
		classes.emplace(#CLASS, &type);\
	}

#define END_MULTIDERIVED_CLASS(CLASS, PARENT1, PARENT2)\
};\
Typeinfo CLASS::type = { #CLASS, { &PARENT1::type, &PARENT2::type }, sizeof(PARENT1) + sizeof(PARENT2), sizeof(CLASS) };

//----------------------

// Не только возвращает typeinfo настоящего класса, но и кастит к нему...
Typeinfo* get_typeinfo(void*& object) {
	Ptr pos = reinterpret_cast<Ptr>(object) + sizeof(Offset);
	// Под указателем лежит next_pos какого-то предка
	int offset = deref(int, pos);
	// Или самого себя, если offset = 0
	while (offset != 0) {
		assert(offset > 0);
		pos += offset;
		offset = deref(int, pos);
	}

	// Typeinfo лежит сразу после offset, а начало объекта ровно на размер родителей и инта раньше позиции
	Typeinfo* typeinfo = deref(Typeinfo*, pos + sizeof(Offset));
	object = pos - typeinfo->parents_size - sizeof(Offset);
	return typeinfo;
}

// Возвращает необходимое смещение или -1, если не нашли
int upcast(Typeinfo* start, std::string desired) {
	// Мы в нужном классе
	if (start->name == desired) {
		return 0;
	}
	// Мы в классе без предков
	if (start->parents.empty()) {
		return -1;
	}
	// Идем по всем предкам, сразу считая смещение
	int shift = -1;
	int siblings_offset = 0;
	for (const auto parent : start->parents) {
		int result = upcast(parent, desired);
		if (result != -1) {
			if (shift != -1) {
				return BAD_CAST::ambiguous;
			}
			shift = result + siblings_offset;
		}
		siblings_offset += parent->size;
	}
	return shift;
}

// Возвращает 0, если desired -- прямой наследник, иначе -1
int downcast(void* object, std::string desired) {
	Ptr pos = reinterpret_cast<Ptr>(object) + sizeof(Offset);
	Typeinfo* pos_info = deref(Typeinfo*, pos + sizeof(Offset));

	// Идем вниз, пока не найдем нужный
	while (pos_info->name != desired) {
		int offset = deref(int, pos);
		// Дальше идти некуда, но не нашли
		if (offset == 0) {
			return -1;
		}
		assert(offset > 0);
		pos += offset;
		pos_info = deref(Typeinfo*, pos + sizeof(Offset));
	}
	return 0;	
}

void* cast(Typeinfo* from, Typeinfo* to, Ptr ptr) {
	// Пытаемся пойти вверх от текущего класса, ~static_cast
	int shift = upcast(from, to->name);
	if (shift == BAD_CAST::ambiguous) {
		return nullptr;
	}
	if (shift != BAD_CAST::not_siblings) {
		return ptr + shift;
	}
	// Не нашли выше, идем ниже. 
	// Прямо на пути встречается нужный класс -> ок, тривиальный случай
	shift = downcast(ptr, to->name);
	if (shift != BAD_CAST::not_siblings) {
		return ptr;
	}
	// Остался шанс найти sibling...
	void* pos = ptr;
	Typeinfo* most_derived = get_typeinfo(pos);
	shift = upcast(most_derived, to->name);
	if (shift == BAD_CAST::ambiguous) {
		return nullptr;
	}
	if (shift != BAD_CAST::not_siblings) {
		return (char*)pos + shift;
	}
	return nullptr;
}

void* cast(std::string _from, std::string _to, void* _ptr) {
	Typeinfo* from = classes.at(_from);
	Typeinfo* to = classes.at(_to);
	Ptr ptr = reinterpret_cast<Ptr>(_ptr);
	return cast(from, to, ptr);
}

#define DYNAMIC_CAST(FROM, TO, ptr)\
(reinterpret_cast<TO*>(cast(#FROM, #TO, ptr)))

DECLARE_CLASS(D)
int d;
END_CLASS(D)

DECLARE_CLASS(E)
int e;
END_CLASS(E)

DECLARE_MULTIDERIVED_CLASS(B, D, E)
long b;
END_MULTIDERIVED_CLASS(B, D, E)

DECLARE_DERIVED_CLASS(C, E)
float c;
END_DERIVED_CLASS(C, E)

DECLARE_MULTIDERIVED_CLASS(A, B, C)
END_MULTIDERIVED_CLASS(A, B, C)


int main() {
	A* a = new A();	
	B* b = DYNAMIC_CAST(A, B, a);
	C* c = DYNAMIC_CAST(B, C, b);
	D* d = a;
	E* e = DYNAMIC_CAST(D, E, d);

}
