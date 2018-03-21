#3			JMP 	6
#4			ENTRY	a
#5			EXTRN	class

#6			MOVR	R1,	5
#7			MOVR	R2,	b
#8			ADD 	R1,	R2
#9			ADD 	R1,	3
#10			MULT	R1,	6
#11			MOVM	b,	R1
#12	
#13	loop_0	MOVR	R1,	b
#14			CMP 	R1,	a
#15			JNE 	cross_0

#16			MOVR	R1,	3
#17			ADD 	R1,	9
#18			MOVM	a,	R1
#19	
#20			JMP 	loop_0

#21	cross_0	MOVR	R1,	b
#22			ADD 	R1,	3
#23			MOVM	a,	R1
#24	
#25	loop_1	MOVR	R1,	5
#26			CMP 	R1,	b
#27			JG  	cross_1

#28			JMP 	loop_1

#29	cross_1	MOVR	R1,	b
#30			CMP 	R1,	a
#31			JG  	cond_0
#32	
#33	cond_0	MOVR	R1,	a
#34			MOVR	R2,	b
#35			ADD 	R1,	R2
#36			MOVM	a,	R1
#37	
#38	a		DC  	'3'
#39	b		DS  	1
