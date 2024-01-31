from django.shortcuts import render, redirect
from django.http import HttpResponse, FileResponse, HttpResponseRedirect, JsonResponse
from .forms import MiFormulario
from django.contrib import messages
from django.apps import apps
from django.urls import reverse
from datetime import timedelta


from django.conf import settings
import string
import ply.lex as lex
import ply.yacc as yacc

def deteccion(request):

    formulario = MiFormulario(request.POST or None, request.FILES or None)
    
    if formulario.is_valid():

        try:

            textoP = formulario.cleaned_data['texto']

            # Definición de tokens
            tokens = [
                'ID', 'INT', 'EQUALS', 'SEMICOLON', 'PLUS', 'NUMBER', 'STRING', 'SHIFT_LEFT', 
                'MINUS', 'TIMES', 'DIVIDE', 'FLOAT', 'STRING1', 'BOOL', 'CHAR', 'LBRACKET', 
                'RBRACKET', 'LKEYS', 'RKEYS', 'COMMA', 'IF', 'LPAREND', 'RPAREND', 'ELSE', 'EQ',
                'FOR', 'COLON', 'AUM', 'RETURN', 'PRIVATE', 'PUBLIC', 'CLASS', 'POINTS', 'MAIN'
            ]

            # Reglas de expresiones regulares para tokens simples
            t_EQUALS = r'='
            t_SEMICOLON = r';'
            t_PLUS = r'\+'
            t_MINUS = r'-'
            t_TIMES = r'\*'
            t_DIVIDE = r'/'
            t_LBRACKET = r'\['
            t_RBRACKET = r'\]'
            t_LPAREND = r'\('
            t_RPAREND = r'\)'
            t_EQ = r'=='
            t_LKEYS = r'\{'
            t_RKEYS = r'\}'
            t_SHIFT_LEFT = r'<<'
            t_COMMA = r','
            t_AUM = r'\++'
            t_COLON = r'\<'
            t_POINTS = r':'

            # Ignorar espacios y tabulaciones
            t_ignore = ' \t'

            # Reglas de expresiones regulares con acciones asociadas
            def t_INT(t):
                r'int'
                return t
            
            def t_MAIN(t):
                r'main'
                return t

            def t_CLASS(t):
                r'class'
                return t

            def t_PRIVATE(t):
                r'private'
                return t

            def t_PUBLIC(t):
                r'public'
                return t

            def t_RETURN(t):
                r'return'
                return t

            def t_FOR(t):
                r'for'
                return t


            def t_ELSE(t):
                r'else'
                return t

            def t_IF(t):
                r'if'
                return t

            def t_FLOAT(t):
                r'float'
                return t

            def t_STRING1(t):
                r'string'
                return t

            def t_BOOL(t):
                r'bool'
                return t

            def t_CHAR(t):
                r'char'
                return t

            def t_STRING(t):
                r'"([^"]*)"'
                t.value = t.value[1:-1]  # Eliminar las comillas
                return t

            def t_NUMBER(t):
                r'\d+'
                t.value = int(t.value)
                return t

            def t_ID(t):
                r'[a-zA-Z_][a-zA-Z_0-9]*'
                return t

            # Manejo de errores léxicos
            def t_error(t):
                print(f"Illegal character '{t.value[0]}'")
                t.lexer.skip(1)

            # Construcción del analizador léxico
            lexer = lex.lex()

            # Reglas de gramática
            def p_statement_cout(p):
                'statement : ID SHIFT_LEFT STRING SEMICOLON'
                p[0] = f'print("{p[3]}")'



            def p_statement_float_assign(p):
                'statement : FLOAT ID EQUALS expr SEMICOLON'
                p[0] = f'{p[2]} = {p[4]}'



            def p_statement_string1_assign(p):
                'statement : STRING1 ID EQUALS expr SEMICOLON'
                p[0] = f'{p[2]} = {p[4]}'



            def p_statement_bool_assign(p):
                'statement : BOOL ID EQUALS expr SEMICOLON'
                p[0] = f'{p[2]} = {p[4]}'

            def p_statement_char_assign(p):
                'statement : CHAR ID EQUALS expr SEMICOLON'
                p[0] = f'{p[2]} = {p[4]}'

            def p_statement_int_assign(p):
                'statement : INT ID EQUALS expr SEMICOLON'
                p[0] = f'{p[2]} = {p[4]}'


            def p_statement_char_array(p):
                'statement : CHAR ID LBRACKET NUMBER RBRACKET SEMICOLON'
                p[0] = f"{p[2]} = ['\0'] * {p[4]};"

            def p_statement_float_array(p):
                'statement : FLOAT ID LBRACKET NUMBER RBRACKET SEMICOLON'
                p[0] = f'{p[2]} = [0.0] * {p[4]};'


            def p_statement_bool_array(p):
                '''statement : BOOL ID LBRACKET NUMBER RBRACKET SEMICOLON
                            | BOOL ID LBRACKET RBRACKET EQUALS LKEYS val_list RKEYS SEMICOLON'''

                if len(p) == 7:
                    p[0] = f'{p[2]} = [False] * {p[4]};'
                else:
                    p[0] = f'{p[2]} = {p[7]};'
                    p[0] = p[0].replace("'", "")

            def p_val_list(p):
                '''val_list : ID
                            | val_list COMMA ID'''
                if len(p) == 2:
                    p[0] = [p[1]]
                else:
                    p[0] = p[1] + [p[3]]

            def p_statement_string1_array(p):
                '''statement : STRING1 ID LBRACKET NUMBER RBRACKET SEMICOLON
                            | STRING1 ID LBRACKET NUMBER RBRACKET EQUALS LKEYS string_list RKEYS SEMICOLON'''

                if len(p) == 7:
                    p[0] = f'{p[2]} = [""] * {p[4]};'
                else:
                    strings = ', '.join([f'"{s}"' for s in p[8]])
                    p[0] = f'{p[2]} = [{strings}];'

            def p_string_list(p):
                '''string_list : STRING
                            | string_list COMMA STRING'''
                if len(p) == 2:
                    p[0] = [p[1]]
                else:
                    p[0] = p[1] + [p[3]]


            def p_statement_int_array(p):
                '''statement : INT ID LBRACKET NUMBER RBRACKET SEMICOLON
                            | INT ID LBRACKET RBRACKET SEMICOLON
                            | INT ID LBRACKET RBRACKET EQUALS LKEYS number_list RKEYS SEMICOLON'''

                if len(p) == 7:
                    p[0] = f'{p[2]} = [0] * {p[4]};'
                elif len(p) == 6:
                    p[0] = f'{p[2]} = [];'
                else:
                    p[0] = f'{p[2]} = {p[7]};'

            def p_number_list(p):
                '''number_list : NUMBER
                            | number_list COMMA NUMBER''' 
                if len(p) == 2:
                    p[0] = [p[1]]
                else:
                    p[0] = p[1] + [p[3]]


            def p_expr_binop(p):
                '''expr : expr MINUS expr
                        | expr PLUS expr
                        | expr TIMES expr
                        | expr DIVIDE expr
                        | NUMBER
                        | ID'''
                if len(p) == 4:
                    p[0] = f'({p[1]} {p[2]} {p[3]})'
                else:
                    p[0] = p[1]
                
            def p_statement_if_else(p):
                'statement : IF LPAREND ID EQ NUMBER RPAREND LKEYS statement RKEYS ELSE LKEYS statement RKEYS'
                p[0] = f'if {p[3]} == {p[5]}:\n\t{p[8]}\nelse:\n\t{p[12]}'

            def p_statement_for(p):
                'statement : FOR LPAREND INT ID EQUALS NUMBER SEMICOLON ID COLON NUMBER SEMICOLON ID AUM RPAREND LKEYS statement RKEYS'
                p[0] = f'for {p[4]} in range({p[6]}, {p[10]}):\n\t{p[16]}'

            def p_statement_function(p):
                '''statement : INT ID LPAREND INT ID COMMA INT ID RPAREND LKEYS RETURN ID AUM ID SEMICOLON RKEYS
                            | INT ID LPAREND INT ID COMMA INT ID RPAREND LKEYS RETURN ID TIMES ID SEMICOLON RKEYS
                            | INT ID LPAREND INT ID COMMA INT ID RPAREND LKEYS RETURN ID MINUS ID SEMICOLON RKEYS
                            | INT ID LPAREND INT ID COMMA INT ID RPAREND LKEYS RETURN ID DIVIDE ID SEMICOLON RKEYS'''
                p[0] = f'def {p[2]}({p[5]}, {p[8]}):\n\treturn {p[12]} {p[13]} {p[14]}'

            def p_statement_class(p):
                '''statement : CLASS ID LKEYS PRIVATE POINTS INT ID SEMICOLON PUBLIC POINTS ID LPAREND INT ID RPAREND LKEYS ID EQUALS ID SEMICOLON RKEYS RKEYS SEMICOLON
                            | CLASS ID LKEYS PRIVATE POINTS INT ID SEMICOLON INT ID SEMICOLON PUBLIC POINTS ID LPAREND INT ID COMMA INT ID RPAREND LKEYS ID EQUALS ID SEMICOLON ID EQUALS ID SEMICOLON RKEYS RKEYS SEMICOLON'''

                if len(p) >= 25:  
                    p[0] = f'class {p[2]}:\n\tdef __init__(self, {p[17]}, {p[20]}):\n\t\tself.{p[7]} = {p[25]}\n\t\tself.{p[9]} = {p[29]}'
                else:
                    p[0] = f'class {p[2]}:\n\tdef __init__(self, {p[7]}):\n\t\tself.{p[7]} = {p[14]}'

            def p_statement_main(p):
                'statement : INT MAIN LPAREND RPAREND LKEYS statement RETURN NUMBER SEMICOLON RKEYS'
                p[0] = f'if __name__ == "__main__":\n\t{p[6]}'

            # Manejo de errores sintácticos
            def p_error(p):
                print(f"Syntax error at '{p.value}'")

            # Construcción del analizador sintáctico
            parser = yacc.yacc()

            # Prueba con una sentencia C++ cout
            result = parser.parse(textoP, lexer=lexer)

        except Exception as e:
            mensaje_error = "No se pudo completar la traducción"
            return render(request, 'paginas/index.html', {'formulario': formulario, 'mensaje_error': mensaje_error})


        
        return render(request, 'paginas/index.html', {'formulario': formulario, 'traducido': result})


    return render(request, 'paginas/index.html', {'formulario': formulario})






    