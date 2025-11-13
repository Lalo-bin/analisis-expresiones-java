import re
import sys
from collections import namedtuple

# --- Definición de la Gramática (Proyecto_01_INFO1148.pdf) ---
# Tarea: "Generar una gramática (G(L))"
# Tarea: "Eliminar la recursión directa y recursión indirecta"

# Esta gramática ya ha sido transformada para eliminar la recursión por la izquierda,
# preparándola para un analizador LL(1).
# E -> T E'
# E' -> + T E' | - T E' | % T E' | lambda
# T -> F T'
# T' -> * F T' | / F T' | lambda
# F -> ( E ) | id | num
# (Usamos 'EP' para E' y 'TP' para T')

GRAMMAR = {
    'E': [['T', 'EP']],
    'EP': [['+', 'T', 'EP'], ['-', 'T', 'EP'], ['%', 'T', 'EP'], ['lambda']],
    'T': [['F', 'TP']],
    'TP': [['*', 'F', 'TP'], ['/', 'F', 'TP'], ['lambda']],
    'F': [['(', 'E', ')'], ['id'], ['num']]
}

NON_TERMINALS = list(GRAMMAR.keys())
START_SYMBOL = 'E'

# Extraemos los terminales de la gramática
TERMINALS = set()
for productions in GRAMMAR.values():
    for production in productions:
        for symbol in production:
            if symbol not in NON_TERMINALS and symbol != 'lambda':
                TERMINALS.add(symbol)
TERMINALS = sorted(list(TERMINALS)) + ['$'] # '$' representa el fin de la entrada


# --- Tarea: "Identificar el conjunto first" ---

def compute_first_sets(grammar, non_terminals, terminals):
    """Calcula los conjuntos FIRST para todos los no-terminales."""
    first_sets = {nt: set() for nt in non_terminals}
    
    # Un helper para calcular el FIRST de una secuencia de símbolos (e.g., T E')
    def get_first_of_sequence(sequence):
        first_seq = set()
        i = 0
        while i < len(sequence):
            symbol = sequence[i]
            
            if symbol in terminals:
                first_seq.add(symbol)
                break # Se detiene al encontrar un terminal
            
            if symbol in non_terminals:
                first_of_symbol = first_sets[symbol]
                first_seq.update(first_of_symbol - {'lambda'})
                
                if 'lambda' not in first_of_symbol:
                    break # No es anulable, nos detenemos
            
            if symbol == 'lambda':
                break
                
            i += 1
        
        # Si todos los símbolos de la secuencia fueron anulables (o la secuencia estaba vacía)
        if i == len(sequence):
            first_seq.add('lambda')
            
        return first_seq

    changed = True
    while changed:
        changed = False
        for nt, productions in grammar.items():
            for production in productions:
                first_of_production = get_first_of_sequence(production)
                
                if not first_of_production.issubset(first_sets[nt]):
                    first_sets[nt].update(first_of_production)
                    changed = True
                    
    return first_sets, get_first_of_sequence

def compute_follow_sets(grammar, non_terminals, start_symbol, first_sets):
    """Calcula los conjuntos FOLLOW para todos los no-terminales."""
    follow_sets = {nt: set() for nt in non_terminals}
    follow_sets[start_symbol].add('$') # Regla 1

    changed = True
    while changed:
        changed = False
        for nt_A, productions in grammar.items():
            for production in productions:
                for i in range(len(production)):
                    symbol_B = production[i]
                    if symbol_B in non_terminals:
                        # Buscamos el FOLLOW de symbol_B
                        # Regla 2: A -> a B b
                        beta = production[i+1:]
                        if beta:
                            first_of_beta, _ = compute_first_sets(
                                {symbol_B: [beta]}, [symbol_B], TERMINALS
                            )
                            first_beta = first_of_beta[symbol_B]
                            
                            # Añadir FIRST(beta) - {lambda}
                            new_symbols = first_beta - {'lambda'}
                            if not new_symbols.issubset(follow_sets[symbol_B]):
                                follow_sets[symbol_B].update(new_symbols)
                                changed = True
                            
                            # Regla 3: Si FIRST(beta) contiene lambda
                            if 'lambda' in first_beta:
                                if not follow_sets[nt_A].issubset(follow_sets[symbol_B]):
                                    follow_sets[symbol_B].update(follow_sets[nt_A])
                                    changed = True
                        else:
                            # Regla 3: A -> a B (beta está vacío)
                            if not follow_sets[nt_A].issubset(follow_sets[symbol_B]):
                                follow_sets[symbol_B].update(follow_sets[nt_A])
                                changed = True
    return follow_sets


# --- Tarea: "genere una tabla sintáctica" ---

def create_parsing_table(grammar, first_sets, follow_sets, get_first_seq_func, non_terminals, terminals):
    """Crea la tabla de análisis sintáctico LL(1)."""
    # Inicializar tabla vacía (diccionario de diccionarios)
    table = {nt: {t: None for t in terminals} for nt in non_terminals}

    for nt_A, productions in grammar.items():
        for production in productions:
            # 1. Calcular FIRST(produccion)
            first_of_production = get_first_seq_func(production)
            
            # 2. Regla 1: Para cada 'a' en FIRST(produccion)
            for terminal_a in first_of_production - {'lambda'}:
                if table[nt_A][terminal_a] is not None:
                    # Conflicto: Múltiples entradas para la misma celda
                    raise ValueError(f"Conflicto LL(1) en T[{nt_A}, {terminal_a}]")
                table[nt_A][terminal_a] = production
            
            # 3. Regla 2: Si lambda está en FIRST(produccion)
            if 'lambda' in first_of_production:
                # Para cada 'b' en FOLLOW(A)
                for terminal_b in follow_sets[nt_A]:
                    if table[nt_A][terminal_b] is not None:
                        raise ValueError(f"Conflicto LL(1) en T[{nt_A}, {terminal_b}] (conflicto lambda/FOLLOW)")
                    table[nt_A][terminal_b] = production
    
    return table


# --- Tarea: "Lectura de archivo" (Implementación del Lexer) ---
# Usamos expresiones regulares como se vio en c2_Expresiones Regulares.pdf

# Definición de un Token
Token = namedtuple('Token', ['type', 'value', 'line', 'column'])

class Lexer:
    """Analizador Léxico (Tokenizer)."""
    
    def __init__(self, file_content):
        self.content = file_content
        # Patrones de Expresiones Regulares para los tokens
        # El orden es importante (ej. ID vs palabras clave si las tuviéramos)
        token_specs = [
            ('num',     r'\d+(\.\d*)?'),      # Números (enteros o flotantes)
            ('id',      r'[a-zA-Z_][a-zA-Z0-9_]*'), # Identificadores
            ('+',       r'\+'),              # Suma
            ('-',       r'-'),              # Resta
            ('*',       r'\*'),              # Multiplicación
            ('/',       r'/'),              # División
            ('%',       r'%'),              # Módulo
            ('(',       r'\('),              # Paréntesis izquierdo
            (')',       r'\)'),              # Paréntesis derecho
            ('NEWLINE', r'\n'),              # Salto de línea (para contar líneas)
            ('SKIP',    r'[ \t]+'),          # Espacios y tabs (ignorar)
            ('MISMATCH',r'.'),               # Cualquier otro caracter (error)
        ]
        
        # Compilamos el regex
        self.tok_regex = re.compile('|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_specs))
        self.line_num = 1
        self.line_start = 0

    def get_tokens(self):
        """Generador que produce tokens uno por uno."""
        for mo in self.tok_regex.finditer(self.content):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - self.line_start
            
            if kind == 'NEWLINE':
                self.line_start = mo.end()
                self.line_num += 1
            elif kind == 'SKIP':
                continue
            elif kind == 'MISMATCH':
                # Ignoramos comentarios o caracteres no reconocidos
                # para este analizador simple de expresiones
                continue 
            else:
                # Mapeamos el 'kind' del regex a los símbolos de la gramática
                # Ej. El 'kind' es 'num', el símbolo de la gramática es 'num'
                yield Token(kind, value, self.line_num, column)
                
        # Fin de la entrada
        yield Token('$', '$', self.line_num, 0)


# --- Tarea: "Implementar los métodos" (Implementación del Parser) ---
# Implementamos un Analizador Sintáctico Descendente (ASD) dirigido por tabla

class Parser:
    """Analizador Sintáctico (Parser) LL(1) Dirigido por Tabla."""
    
    def __init__(self, table, start_symbol):
        self.table = table
        self.start_symbol = start_symbol
        self.lexer = None
        self.token_stream = None
        self.current_token = None

    def _next_token(self):
        """Consume el token actual y obtiene el siguiente."""
        try:
            self.current_token = next(self.token_stream)
        except StopIteration:
            self.current_token = Token('$', '$', -1, -1) # Fin de stream

    def parse(self, file_path):
        """Lee y analiza el archivo de entrada."""
        print(f"\n--- Analizando archivo: {file_path} ---")
        try:
            with open(file_path, 'r') as f:
                content = f.read()
        except FileNotFoundError:
            print(f"Error: El archivo '{file_path}' no fue encontrado.")
            return

        self.lexer = Lexer(content)
        self.token_stream = self.lexer.get_tokens()
        self._next_token()
        
        # 1. Inicializar Pila
        stack = ['$', self.start_symbol] # $ = Fin de pila, S = Símbolo inicial
        
        # 2. Bucle principal del analizador
        while stack:
            # Ver el tope de la pila
            top_of_stack = stack[-1]
            
            # Ver el token de entrada actual
            token_type = self.current_token.type
            token_value = self.current_token.value
            
            print(f"Pila: {str(stack):<40} Token Actual: ({token_type}, '{token_value}')")

            if top_of_stack == '$' and token_type == '$':
                print("--- Análisis Exitoso ---")
                print("La cadena es aceptada por la gramática.")
                return True

            if top_of_stack in TERMINALS or top_of_stack == '$':
                # Caso: Tope de pila es un Terminal
                if top_of_stack == token_type:
                    stack.pop() # Hacer pop
                    self._next_token() # Avanzar token
                else:
                    self._error(f"Se esperaba el token '{top_of_stack}' pero se encontró '{token_type}'")
                    return False
            
            elif top_of_stack in NON_TERMINALS:
                # Caso: Tope de pila es un No-Terminal
                # 3. Consultar la tabla
                production = self.table[top_of_stack].get(token_type)
                
                if production is None:
                    # Error: Celda vacía en la tabla
                    expected = ", ".join([t for t, v in self.table[top_of_stack].items() if v is not None])
                    self._error(f"Token inesperado '{token_type}'. Se esperaba uno de: {expected}")
                    return False
                
                # 4. Aplicar la regla
                stack.pop() # Sacar el No-Terminal
                
                # Si no es lambda, empujar los símbolos de la producción (en orden inverso)
                if production != ['lambda']:
                    for symbol in reversed(production):
                        stack.append(symbol)
                
                print(f"   -> Aplicando regla: {top_of_stack} -> {' '.join(production)}")
                
            else:
                self._error(f"Símbolo desconocido en la pila: {top_of_stack}")
                return False
                
        print("--- Análisis Fallido (Fin de pila inesperado) ---")
        return False

    def _error(self, message):
        """Manejo de errores sintácticos."""
        token = self.current_token
        print(f"\n*** Error de Sintaxis! ***")
        print(f"  {message}")
        print(f"  En línea {token.line}, columna {token.column} (token: '{token.value}')")


# --- Ejecución Principal ---

def main():
    # --- 1 y 2. Gramática ---
    print("--- 1. Gramática (Sin Recursión Izquierda) ---")
    for nt, productions in GRAMMAR.items():
        for prod in productions:
            print(f"{nt} -> {' '.join(prod)}")
    
    # --- 3. Conjuntos FIRST y FOLLOW ---
    print("\n--- 3. Conjuntos FIRST ---")
    first_sets, get_first_seq_func = compute_first_sets(GRAMMAR, NON_TERMINALS, TERMINALS)
    for nt, f_set in first_sets.items():
        print(f"FIRST({nt}) = {f_set}")

    print("\n--- 3. Conjuntos FOLLOW ---")
    follow_sets = compute_follow_sets(GRAMMAR, NON_TERMINALS, START_SYMBOL, first_sets)
    for nt, f_set in follow_sets.items():
        print(f"FOLLOW({nt}) = {f_set}")
        
    # --- 4. Tabla Sintáctica ---
    print("\n--- 4. Tabla Sintáctica LL(1) ---")
    try:
        parsing_table = create_parsing_table(GRAMMAR, first_sets, follow_sets, get_first_seq_func, NON_TERMINALS, TERMINALS)
        # Imprimir la tabla de forma legible
        header = f"{'':<4} |" + "".join([f"{t:<10}" for t in TERMINALS])
        print(header)
        print("-" * len(header))
        for nt, row in parsing_table.items():
            row_str = f"{nt:<4} |"
            for t in TERMINALS:
                prod = row[t]
                if prod is None:
                    row_str += f"{'':<10}"
                elif prod == ['lambda']:
                    row_str += f"{'lambda':<10}"
                else:
                    row_str += f"{' '.join(prod):<10}"
            print(row_str)
            
    except ValueError as e:
        print(f"\nError al generar la tabla: {e}")
        print("La gramática no es LL(1).")
        sys.exit(1)

    # --- 5 y 6. Implementación (Lexer y Parser) ---
    # MODIFICACIÓN: Se elimina la creación automática de archivos.
    # Ahora puedes probar tus propios archivos.

    # Instanciamos el parser con la tabla generada
    parser = Parser(table=parsing_table, start_symbol=START_SYMBOL)
    
    print("\n--- Analizador Sintáctico Interactivo ---")
    print("Crea tus propios archivos .java (ej: prueba1.java, error1.java)")
    print("Escribe el nombre del archivo que quieres analizar.")
    print("Escribe 'salir' para terminar.")
    
    while True:
        filename = input("\nArchivo a analizar > ")
        if filename.lower() == 'salir':
            break
        
        # Opcional: auto-añadir .java si no está
        if not filename.endswith(".java") and '.' not in filename:
             filename += ".java"
            
        parser.parse(filename)


if __name__ == "__main__":
    main()