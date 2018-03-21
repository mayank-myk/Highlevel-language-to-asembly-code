import argparse
import re

# def add_variable(var_name, var_value):
# 	if var_value[0].isdigit():
# 		data_section.append(var_name+" DB "+var_value+"\n")
# 	else:
# 		data_section.append(var_name+" DS "+var_value+"\n")

def perform(op, var_1, var_2):
	program_section.append("\t\tMOV\t"+var_1+",\t"+var_2+"\n")

# symbols and structure
def get_symbols(file_name):
	symbol_table = {}

	file = open(file_name,"r")
	code = file.read()
	diff_functions = code.split("function")

	functions = {} # [[parameters], [code lines]]

	# dividing each function
	for function in diff_functions:
		if function != "":
			name, params, body  = re.split(r"[\(\)]", function)
			functions[name.strip()] = [[x.strip() for x in params.strip().split(",")],
										[x.strip() for x in body.split("{")[1].split("}")[0].strip().split("\n")]]

	# for main function
	if "main" in functions:
		for i in range(len(functions["main"][1])):
			# get all declarations and store in symbols
			line = functions["main"][1][i]

			if re.match(r'public\s*var', line):
				line = line.split("public")[1].strip().split("var")[1].strip()
				var, val = [x.strip() for x in line.split("=")]
				if not re.compile(r'[+*/-]').search(val) and val[0].isdigit():
					symbol_table[var] = [val, 1, "_","_", file_name] # value, length, type(PD), Address, headerFile
					line = ""
				else:
					symbol_table[var] = ["_", 1, "_","_", file_name]
				symbol_table[var][2] = "PD"
				
			elif line.startswith("var"):
				line = line.strip("var").strip()
				var, val = [x.strip() for x in line.split("=")]
				if not re.compile(r'[+*/-]').search(val) and val[0].isdigit():
					symbol_table[var] = [val, 1, "_","_", file_name]
					line = ""
				else:
					symbol_table[var] = ["_", 1, "_","_", file_name]
			# saving changes to line
			functions["main"][1][i] = line

	return functions, symbol_table

def op_code(asm, op, var_1, var_2, label="\t"):
	if op == "+":
		op = "ADD "
	elif op == "-":
		op = "SUB "
	elif op == "*":
		op = "MULT"
	elif op == "/":
		op = "DIV "

	asm.append(label+"\t"+op+"\t"+var_1+",\t"+str(var_2)+"\n")

def make_assembly(functions, symbols):
	extern_vars = []
	asm = []
	i = 0
	loopCount = 0
	ifCount = 0
	curr_label = "\t"

	while i < len(functions["main"][1]):
		line = functions["main"][1][i].strip()
		if re.match(r'extern [^ ]*',line):
			extern_vars.append(line.split("extern")[1].strip())

		elif re.match(r'loop [^ ]*',line):
			cmp_1, operator,cmp_2 = [x.strip() for x in re.split(r'(\>|\<|\=|\!\=)',line.split("loop")[1].strip())]
			op_code(asm, "MOVR", "R1", cmp_2, "loop_"+str(loopCount))
			curr_label = '\t'
			op_code(asm, "CMP ", "R1", cmp_1, curr_label)
			curr_label = '\t'

			if operator == ">":
				operator = "JG  "
			elif operator == "<":
				operator = "JL  "
			elif operator == "=":
				operator = "JEQ "
			elif operator == "!=":
				operator = "JNE "
			else:
				operator = "Error"
			asm.append(curr_label+"\t"+operator+"\tcross_"+str(loopCount)+"\n\n")

		elif re.match(r'endloop.*', line):
			asm.append(curr_label+"\t"+"JMP \tloop_"+str(loopCount)+"\n\n")
			curr_label = "cross_"+str(loopCount)
			loopCount += 1

		elif re.match(r'if [^ ]*',line):
			cmp_1, operator,cmp_2 = [x.strip() for x in re.split(r'(\>|\<|\=|\!\=)',line.split("if")[1].strip())]
			op_code(asm, "MOVR", "R1", cmp_2, curr_label)
			curr_label = '\t'
			op_code(asm, "CMP ", "R1", cmp_1, curr_label)
			curr_label = '\t'

			if operator == ">":
				operator = "JG  "
			elif operator == "<":
				operator = "JL  "
			elif operator == "=":
				operator = "JEQ "
			elif operator == "!=":
				operator = "JNE "
			else:
				operator = "Error"

			asm.append(curr_label+"\t"+operator+"\tcond_"+str(ifCount)+"\n")
			curr_label = '\t'

			asm.append("\n")

		elif re.match(r'endif.*',line):
			curr_label="cond_"+str(ifCount)
			ifCount += 1

		elif re.compile(r'=.*[+*/-]').search(line):
			operands = [x.strip() for x in re.split(r'([+-/*=])', line)]
			j = 2
			k = 2
			while j < len(operands):
				if not re.compile(r"[+-/*]").search(operands[j]):
					op_code(asm, "MOVR", "R1", operands[j], curr_label)
					curr_label = '\t'
					j += 1
				else:
					if operands[j+1][0].isdigit():
						op_code(asm, operands[j],"R1",operands[j+1], curr_label)
						curr_label = '\t'
					else:
						op_code(asm, "MOVR","R"+str(k),operands[j+1], curr_label)
						curr_label = '\t'
						op_code(asm, operands[j],"R1","R"+str(k), curr_label)
						k+=1
					j += 2
			op_code(asm, "MOVM", operands[0], "R1", curr_label)
			asm.append("\n")
		i+=1

	if extern_vars != []:
		header = "\t\tEXTRN\t"+extern_vars[0]
		for i in range(1,len(extern_vars)):
			header += str(extern_vars[i])
		header += "\n\n"
		asm = [header] + asm

	header = ""
	for x in symbols:
		if symbols[x][2] == "PD":
			if header == "":
				header += "\t\tENTRY\t"+x
			else:
				header += ", "+x
	header += "\n"
	asm = [header] + asm

	for x in symbols:
		if symbols[x][0] != "_":
			asm += [x+"\t\tDC  \t\'"+symbols[x][0]+"\'\n"]
		else:
			asm += [x+"\t\tDS  \t1\n"]

	return asm

def translate_address(asm_code):
	offset = int(input("Offset Value: "))

	asm_code = ["\t\tJMP \t"+str(offset+3)+"\n"] + asm_code
	address = [(offset+i) for i in range(len(asm_code))]

	with open("translated"+str(len(file_funcs))+".asm","w") as out_file:
		for i in range(len(asm_code)):
			out_file.write("#"+str(i+offset)+"\t"+asm_code[i])

	return address

def symbol_write(symbols, i):
	with open("table"+str(i)+".sym","w") as out_file:
		out_file.write("Symbol\tValue\tLength\tType\tAddress"+"\n================================================ \n")
		for x in symbols:
			out_file.write(str(x)+"\t\t"+str(symbols[x][0])+"\t\t"+str(symbols[x][1])+"\t\t"+str(symbols[x][2])+"\t\t"+str(symbols[x][3])+"\t\t"+str(symbols[x][4])+"\n")

if __name__ == "__main__": 
	files = [x for x in input("Files: ").split()]
	file_funcs = []
	file_symbols = []
	file_asm = []
	file_add = []

	op_table = {}
	symbol_table = {}

	for file_name in files:
		functions, symbols = get_symbols(file_name) # tokenization and syntactical analysis

		asm_code = make_assembly(functions, symbols)

		with open("code"+str(len(file_funcs))+".asm","w") as out_file:
			for x in asm_code:
				out_file.write(x)

		symbol_write(symbols, len(file_funcs))
		address = translate_address(asm_code)


		file_funcs.append(functions)
		file_symbols.append(symbols)
		file_asm.append(asm_code)
		file_add.append(address)

	# storing variables to symbol table
	for i in range(len(file_asm)):
		for j in range(len(file_asm[i])):
			y = file_asm[i][j]
			if not re.match(r'loop.*',y) and not re.match(r'cond.*',y) and not re.match(r'cross.*',y):
				if re.match(r'[a-zA-Z]\t\tD',y):
					file_symbols[i][re.split(r'\t',y)[0]][3] = file_add[i][j]

	# storing labels in symbol table
	for i in range(len(file_asm)):
		for j in range(len(file_asm[i])):
			y = file_asm[i][j]
			if re.match(r"loop_.*", y):
				symbol_table[re.split(r'(loop_[0-9]*)',y)[1]] = ["_",1,"_",file_add[i][j],"_"]
			elif re.match(r"cross_.*", y):
				symbol_table[re.split(r'(cross_[0-9]*)',y)[1]] = ["_",1,"_",file_add[i][j],"_"]
			elif re.match(r"cond_.*", y):
				symbol_table[re.split(r'(cond_[0-9]*)',y)[1]] = ["_",1,"_",file_add[i][j],"_"]

	# generate optable 
	OP_ID = 0
	Op_codes = ["MOVR","MOVM","ADD","MULT","DIV","SUB","JMP","JNE", "JL", "JG", "JEQ","CMP"]
	Normal_Op_codes = ["MOVR","MOVM","ADD","MULT","DIV","SUB","CMP"]

	for i in range(len(file_asm)):
		for j in range(len(file_asm[i])):
			y = file_asm[i][j]
			arr = re.split(r"([A-Z]*)",y)
			if len(arr)>1:
				if arr[1] in Op_codes:
					if arr[1] not in op_table:
						if OP_ID <9:
							op_table[arr[1]] = ["0"+str(OP_ID), 1]
						else:
							op_table[arr[1]] = ["1"+str(OP_ID), 1]
						OP_ID += 1
						OP_ID = OP_ID%9


	# adding variables to symbol table
	for i in range(len(file_funcs)):
		for x in file_symbols[i]:
			symbol_table[x] = file_symbols[i][x]

	symbol_write(symbol_table, "_final")

	# printing tables
	print("OP Table:\n")
	for x in op_table:
		print(x,op_table[x])

	print("\nSYMBOL Table:\n")
	for x in symbol_table:
		print(x,"\t",symbol_table[x])

	# # removing symbols
	for i in range(len(file_asm)):
		for j in range(len(file_asm[i])):
			for x in symbol_table:
				temp = file_asm[i][j]
				print(temp, x)

				if x in symbol_table:
					if not re.match(r'loop_.*',x) and not re.match(r'cross_.*',x) and not re.match(r'cond_.*', x):
						x = symbol_table[x][3]
						print(x)
				if len(temp)>1:
					temp = temp[0] + str(x) + temp[1]
				file_asm[i][j] = temp
				print("Changed",temp)

	print(file_asm[0])
	with open("hello.txt","w") as file:
		for k in range(len(file_asm[0])):
			file.write(file_asm[0][k])
	# for i in range(len(file_asm)):
	# 	for j in range(len(file_asm[i])):
	# 		y = file_asm[i][j]
	# 		opes = re.split(r'([A-Z]+)',y)
	# 		if opes[1] in Normal_Op_codes:
	# 			print(len(opes))
	# 			if len(opes)>1:
	# 				new_opes = re.split(r'[\t\n,]*',opes[-1:][0])

	# 				print(opes[-2:])
	# 				# if var_1 in symbol_table:
	# 				# 	var_1 = symbol_table[var_1][4]
	# 				# elif var_2 in symbol_table:
	# 				# 	var_2 = symbol_table[var_2][4]
	# 				# opes[-2:] = [var_1, var_2]

	# 			for k in opes:
	# 				print(k,end="")



	# arr = re.split(r"([A-Z]*)",y)
	# if len(arr)>1:
	# 	if arr[1] == "MOVR" or arr[1] == "MOVM" or arr[1] == "JMP" or arr[1] == "JNE" or arr[1] == "JL" or arr[1] == "JG" or arr[1] == "JEQ":
			

	# for x in file_symbols:
	# 	for y in x:
	# 		if 
	# linking
	# x = file_add[0][0]
	# for i in range(len(file_add)):
	# 	for j in range(len(file_add[i])):
	# 		file_add[i][j] = x
	# 		x+=1
	# print(file_add)


