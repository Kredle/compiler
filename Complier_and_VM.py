t_counter = 0
symbols = ['}', '[', ']', '*', '/', '+', '-', '(', ')', '{', '>', ';', '=']
operands = ['+','-','/','*']


def convertable_to_float(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def VM(file_name: str):
    mem = {}
    with open(file_name) as file:
        lines = file.readlines()

    ind = 0
    while ind < len(lines):
        line = lines[ind].split()
        if line[0] == "READ":
            mem[line[1]] = float(input(f"Enter value for {line[1]}: "))
        elif line[0] == "WRITE":
            print(mem.get(line[1], "Variable not found."))
        elif line[0] == "GOTO":
            ind = int(line[1]) - 1
        elif line[0] == "GOTOIFNOT":
            if mem.get(line[1], 0) <= 0:
                ind = int(line[2]) - 1
            else:
                ind += 1
                continue
        elif line[0] == "GOTOIF":
            if mem.get(line[1], 0) > 0:
                ind = int(line[2]) - 1
            else:
                ind += 1
                continue
        elif line[0] == "ADD":
            if convertable_to_float(line[1]) and convertable_to_float(line[2]):
                mem[line[3]] = float(line[1]) + float(line[2])
            elif convertable_to_float(line[1]):
                mem[line[3]] = float(line[1]) + mem.get(line[2], 0)
            elif convertable_to_float(line[2]):
                mem[line[3]] = mem.get(line[1], 0) + float(line[2])
            else:
                mem[line[3]] = mem.get(line[1], 0) + mem.get(line[2], 0)
        elif line[0] == "SUB":
            if convertable_to_float(line[1]) and convertable_to_float(line[2]):
                mem[line[3]] = float(line[1]) - float(line[2])
            elif convertable_to_float(line[1]):
                mem[line[3]] = float(line[1]) - mem.get(line[2], 0)
            elif convertable_to_float(line[2]):
                mem[line[3]] = mem.get(line[1], 0) - float(line[2])
            else:
                mem[line[3]] = mem.get(line[1], 0) - mem.get(line[2], 0)
        elif line[0] == "MUL":
            if convertable_to_float(line[1]) and convertable_to_float(line[2]):
                mem[line[3]] = float(line[1]) * float(line[2])
            elif convertable_to_float(line[1]):
                mem[line[3]] = float(line[1]) * mem.get(line[2], 0)
            elif convertable_to_float(line[2]):
                mem[line[3]] = mem.get(line[1], 0) * float(line[2])
            else:
                mem[line[3]] = mem.get(line[1], 0) * mem.get(line[2], 0)
        elif line[0] == "DIV":
            if convertable_to_float(line[1]) and convertable_to_float(line[2]):
                if float(line[2]) == 0:
                    raise ZeroDivisionError("Division by zero error.")
                mem[line[3]] = float(line[1]) / float(line[2])
            elif convertable_to_float(line[1]):
                if mem.get(line[2], 0) == 0:
                    raise ZeroDivisionError("Division by zero error.")
                mem[line[3]] = float(line[1]) / mem.get(line[2], 0)
            elif convertable_to_float(line[2]):
                if float(line[2]) == 0:
                    raise ZeroDivisionError("Division by zero error.")
                mem[line[3]] = mem.get(line[1], 0) / float(line[2])
            else:
                if mem.get(line[2], 0) == 0:
                    raise ZeroDivisionError("Division by zero error.")
                mem[line[3]] = mem.get(line[1], 0) / mem.get(line[2], 0)
        elif line[0] == "COPY":
            if convertable_to_float(line[1]):
                mem[line[2]] = float(line[1])
            else:
                mem[line[2]] = mem.get(line[1], 0)

        ind += 1

    return mem


#Make complier. code in code_for_complier.txt -> commands in code_from_complier.txt

class Command:
    def __init__(self, name, lhs='', rhs='', res=''):
        self.name = name
        self.lhs = lhs
        self.rhs = rhs
        self.res = res

    def __str__(self):
        return self.name + " " + self.lhs + " " + self.rhs + " " + self.res

def prior(op):
    if op == "+" or op == '-':
        return 1
    if op == "*" or op == '/':
        return 2
    if op == '(' or op == ')':
        return 0
    return 3


def handle_expression(token_list):
    global t_counter
    ARG = []
    OP = []
    L = []

    def generate_command():
        global t_counter
        op = OP.pop()
        if len(ARG) > 1:
            rhs = ARG.pop()
            lhs = ARG.pop()
            match op:
                case "+":
                    name = "ADD"
                case "-":
                    name = "SUB"
                case "*":
                    name = "MUL"
                case "/":
                    name = "DIV"
            res = f"t{t_counter}"
            L.append(Command(name, lhs, rhs, res))
            ARG.append(res)
            t_counter += 1
        else:
            var = ARG.pop()
            res = f"t{t_counter}"
            L.append(Command("COPY", var, "", res))
            ARG.append(res)
            t_counter += 1

    for index, token in enumerate(token_list):
        if token not in symbols:
            if len(token) > 1 and token[0].isalpha():
                ARG.append(token)
            else:
                ARG.append(token)
        elif token in operands:
            if token in operands and (index + 1 >= len(token_list) or token_list[index + 1] in operands or token_list[index + 1] == ")"):
                raise SyntaxError(f"Error: unnessary operand at position {index + 1}")
            while OP and OP[-1] in operands and (prior(OP[-1]) >= prior(token)):
                generate_command()
            OP.append(token)
        elif token == "(":
            if index + 1 < len(token_list) and token_list[index + 1] == ")":
                raise SyntaxError("Error: empty ()")
            OP.append(token)
        elif token == ")":
            while OP and OP[-1] != "(":
                generate_command()
            OP.pop()

    while OP:
        generate_command()

    if len(ARG) == 1 and ARG[0] not in operands:
        var = ARG.pop()
        res = f"t{t_counter}"
        L.append(Command("COPY", var, "", res))
        ARG.append(res)
        t_counter += 1

    return L


def parse_code(file_path):
    token_list = []
    keywords = {"if", "while", "ifnot", "whilenot", "read", "write"}

    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            i = 0
            n = len(line)

            while i < n:
                char = line[i]
                if char == ' ':
                    i += 1
                    continue
                if char.isalpha():
                    start = i
                    while i < n and line[i].isalpha():
                        i += 1
                    word = line[start:i]

                    if word in keywords:
                        token_list.append(word)
                    else:
                        token_list.extend(list(word))
                elif char.isdigit() or (char == '.' and i + 1 < n and line[i + 1].isdigit()):
                    start = i
                    has_decimal_point = False
                    while i < n and (line[i].isdigit() or (line[i] == '.' and not has_decimal_point)):
                        if line[i] == '.':
                            has_decimal_point = True
                        i += 1
                    number = line[start:i]
                    token_list.append(number)
                else:
                    token_list.append(char)
                    i += 1

    return token_list

def handle_command(token_list):
    global t_counter
    if token_list[0] == "read":
        return [Command("READ", token_list[2], "", "")]
    elif token_list[0] == "write":
        return [Command("WRITE", token_list[2], "", "")]
    else:
        if len(token_list) == 3 and token_list[1] == '=':
            return [Command("COPY", token_list[2], token_list[0], "")]
        else:
            temp = handle_expression(token_list[2:])
            if temp:
                temp[-1].res = token_list[0]
            t_counter -= 1
            return temp

#handle_block
def handle_block(commands, current_line):
    result_code = []
    index = 0

    while index < len(commands):
        current_token = commands[index]

        if current_token in ["read", "write"]:
            result_code.extend(handle_command(commands[index: index + 3]))
            index += 3

        elif current_token == '=':
            end_index = index

            while end_index < len(commands) and commands[end_index] != ';':
                end_index += 1

            if end_index >= len(commands) or commands[end_index] != ';':
                line_number = current_line + commands[:index].count('\n')
                raise IndexError(f"Error: missing ';' on line {line_number + 1}")

            result_code.extend(handle_command(commands[index - 1: end_index + 1]))
            index = end_index + 1

        elif current_token in ["if", "ifnot", "while", "whilenot"]:
            block_start = index
            while commands[block_start] != "{":
                block_start += 1
            block_start += 1

            depth = 1
            while depth != 0:
                if commands[block_start] == "{":
                    depth += 1
                elif commands[block_start] == "}":
                    depth -= 1
                block_start += 1

            result_code.extend(process_control_block(commands[index: block_start], current_line + len(result_code)))
            index = block_start
        else:
            index += 1

    return result_code

def process_control_block(commands, current_line):
    output = []

    def handle_if(name):
        end = 0
        for i in range(2, len(commands)):
            if commands[i] == "]":
                end = i
                break

        condition_part = commands[2:end]
        if not condition_part:
            raise ValueError("Condition in 'if' not found.")

        evaluated_condition = handle_expression(condition_part)
        if not evaluated_condition:
            raise ValueError("Couldn't evaluate condition in 'if' statement.")

        output.extend(evaluated_condition)
        start_of_block = current_line + len(output) + 1
        block_content = handle_block(commands[end + 2:len(commands) - 1], start_of_block)
        end_of_block = start_of_block + len(block_content)
        output.append(Command(name, evaluated_condition[-1].res, str(end_of_block), ""))
        output.extend(block_content)

    def handle_while(commands, current_line, is_not):
        end = 0
        for i in range(2, len(commands)):
            if commands[i] == "]":
                end = i
                break

        condition_part = commands[2:end]
        if not condition_part:
            raise ValueError("Condition in 'while' not found.")

        evaluated_condition = handle_expression(condition_part)
        if not evaluated_condition:
            raise ValueError("Couldn't evaluate condition in 'while' statement.")

        output.extend(evaluated_condition)
        condition_line = current_line + len(output)
        block_content = handle_block(commands[end + 2:len(commands) - 1], condition_line + 1)
        end_of_block = condition_line + len(output) + len(block_content) + 1

        if is_not:
            output.append(Command("GOTOIF", evaluated_condition[-1].res, str(end_of_block)))
            output.extend(block_content)
            output.append(Command("GOTO", res=str(end_of_block)))
        else:
            output.append(Command("GOTOIFNOT", evaluated_condition[-1].res, str(end_of_block)))
            output.extend(block_content)
            output.append(Command("GOTO", res=str(condition_line - 1)))

    if commands[0] == "if":
        handle_if("GOTOIFNOT")
    elif commands[0] == "ifnot":
        handle_if("GOTOIF")
    elif commands[0] == "while":
        handle_while(commands, current_line, False)
    elif commands[0] == "whilenot":
        handle_while(commands, current_line, True)

    return output


L = parse_code("code_for_complier.txt")
output = handle_block(L, 0)
with open("code_from_complier.txt", 'w') as f:
    for command in output:
        f.write(str(command) + "\n")

res = VM("code_from_complier.txt")
print(res)
#97 122 65 90

#Verifing with compiled code
a = 8
x = 0.01
e = 0.01
while True:
    x = 0.5 * (x + a/x)
    if abs(x - a/x) < 2*e:
        print(x)
        break





