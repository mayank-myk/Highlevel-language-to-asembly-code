		ENTRY	a
		EXTRN	class

		MOVR	R1,	5
		MOVR	R2,	b
		ADD 	R1,	R2
		ADD 	R1,	3
		MULT	R1,	6
		MOVM	b,	R1

loop_0	MOVR	R1,	b
		CMP 	R1,	a
		JNE 	cross_0

		MOVR	R1,	3
		ADD 	R1,	9
		MOVM	a,	R1

		JMP 	loop_0

cross_0	MOVR	R1,	b
		ADD 	R1,	3
		MOVM	a,	R1

loop_1	MOVR	R1,	5
		CMP 	R1,	b
		JG  	cross_1

		JMP 	loop_1

cross_1	MOVR	R1,	b
		CMP 	R1,	a
		JG  	cond_0

cond_0	MOVR	R1,	a
		MOVR	R2,	b
		ADD 	R1,	R2
		MOVM	a,	R1

a		DC  	'3'
b		DS  	1
