DEBUG = False

COMMAND_LEN = 3
STACK_SIZE = 33 * 3
STATIC_SIZE = 33 * 3


def Check(condition, error_string="Неизвестная ошибка"):
    if not condition:
        print(error_string)
        assert False


# Коды операций
# копирует в регистр другой регистр
MOV = 0
# копирует в регистр число
MOVN = 1
# складывает два регистра
ADD = 2
# складывает регистр и число
ADDN = 3
# вычитает из регистра значение другого
SUB = 4
# вычитает из регистра число
SUBN = 5
# безусловный переход на номер строки
JMP = 6
# переход на строку, если значение регистра меньше 0
JLZ = 7
# записать регистр в стек
PUSH = 8
# записать вершину стека в регистр
POP = 9
# вызвать функцию (по номеру строки)
CALL = 10
# возврат из функции
RET = 11
# конец программы
END = 12
# вывести на экран что-нибудь
PRINT = 13
# ввести число
READN = 14
command_names = ["mov", "movn", "add", "addn", "sub", "subn", "jmp", "jlz", "push", "pop", "call", "ret", "end",
                 "print", "readn"]
command_ids = [MOV, MOVN, ADD, ADDN, SUB, SUBN, JMP, JLZ, PUSH, POP, CALL, RET, END, PRINT, READN]
commands = {command_names[i]: command_ids[i] for i in range(len(command_ids))}
commands_id_to_name = {command_ids[i]: command_names[i] for i in range(len(command_ids))}

# Регистры
EIP = 0
ESP = 1
EBP = 2
EAX = 3
EBX = 4
ECX = 5
EDX = 6
STC = 7
NIU = 8  # неиспользуемый регистр, чтобы выровнять команды
reg_names = ["eip", "esp", "ebp", "eax", "ebx", "ecx", "edx", "stc", "anu"]
reg_ids = [EIP, ESP, EBP, EAX, EBX, ECX, EDX, STC, NIU]
registers = {reg_names[i]: reg_ids[i] for i in range(len(reg_ids))}
registers_id_to_name = {reg_ids[i]: reg_names[i] for i in range(len(reg_ids))}
FIRST_COMMAND_ADDR = len(registers)