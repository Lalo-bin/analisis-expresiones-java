import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import os
import sys
from main import (
    GRAMMAR, NON_TERMINALS, TERMINALS, START_SYMBOL,
    compute_first_sets, compute_follow_sets, create_parsing_table,
    Parser, Lexer
)


class ParserGUI:
    """Interfaz gráfica para el analizador sintáctico."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Analizador Sintáctico LL(1) - Proyecto INFO1148")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # Variables
        self.current_file = None
        self.parsing_table = None
        self.first_sets = None
        self.follow_sets = None
        self.analysis_performed = False
        
        # Inicializar conjuntos y tabla
        self.initialize_parser_components()
        
        # Crear interfaz
        self.create_widgets()
        
    def initialize_parser_components(self):
        """Inicializa los conjuntos FIRST, FOLLOW y la tabla sintáctica."""
        self.first_sets, self.get_first_seq_func = compute_first_sets(
            GRAMMAR, NON_TERMINALS, TERMINALS
        )
        self.follow_sets = compute_follow_sets(
            GRAMMAR, NON_TERMINALS, START_SYMBOL, 
            self.first_sets, self.get_first_seq_func
        )
        self.parsing_table = create_parsing_table(
            GRAMMAR, self.first_sets, self.follow_sets, 
            self.get_first_seq_func, NON_TERMINALS, TERMINALS
        )
        
    def create_widgets(self):
        """Crea todos los widgets de la interfaz."""
        
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar peso de filas y columnas
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # --- Sección superior: Controles ---
        control_frame = ttk.LabelFrame(main_frame, text="Controles", padding="10")
        control_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Botones
        ttk.Button(control_frame, text="📁 Abrir Archivo", 
                  command=self.open_file, width=20).grid(row=0, column=0, padx=5, pady=5)
        
        ttk.Button(control_frame, text="▶ Analizar", 
                  command=self.analyze_file, width=20).grid(row=0, column=1, padx=5, pady=5)
        
        self.btn_grammar = ttk.Button(control_frame, text="📋 Mostrar Gramática", 
                  command=self.show_grammar, width=20, state='disabled')
        self.btn_grammar.grid(row=0, column=2, padx=5, pady=5)
        
        self.btn_first_follow = ttk.Button(control_frame, text="📊 Mostrar FIRST/FOLLOW", 
                  command=self.show_first_follow, width=20, state='disabled')
        self.btn_first_follow.grid(row=0, column=3, padx=5, pady=5)
        
        self.btn_table = ttk.Button(control_frame, text="🗂️ Mostrar Tabla", 
                  command=self.show_table, width=20, state='disabled')
        self.btn_table.grid(row=0, column=4, padx=5, pady=5)
        
        # Label para archivo actual
        self.file_label = ttk.Label(control_frame, text="Ningún archivo seleccionado", 
                                    foreground="gray")
        self.file_label.grid(row=1, column=0, columnspan=5, pady=5)
        
        # --- Panel izquierdo: Editor de código ---
        left_frame = ttk.LabelFrame(main_frame, text="Código de Entrada", padding="10")
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        left_frame.columnconfigure(0, weight=1)
        left_frame.rowconfigure(0, weight=1)
        
        self.code_text = scrolledtext.ScrolledText(
            left_frame, wrap=tk.WORD, width=40, height=20,
            font=("Consolas", 11), bg='#ffffff', fg='#000000'
        )
        self.code_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # --- Panel derecho: Resultados ---
        right_frame = ttk.LabelFrame(main_frame, text="Resultados del Análisis", padding="10")
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(0, weight=1)
        
        self.result_text = scrolledtext.ScrolledText(
            right_frame, wrap=tk.WORD, width=60, height=20,
            font=("Consolas", 10), bg='#1e1e1e', fg='#d4d4d4'
        )
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar tags para colores
        self.result_text.tag_config("success", foreground="#4ec9b0")
        self.result_text.tag_config("error", foreground="#f48771")
        self.result_text.tag_config("info", foreground="#569cd6")
        self.result_text.tag_config("warning", foreground="#dcdcaa")
        
        # --- Sección inferior: Tokens ---
        tokens_frame = ttk.LabelFrame(main_frame, text="Tokens Identificados", padding="10")
        tokens_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        tokens_frame.columnconfigure(0, weight=1)
        tokens_frame.rowconfigure(0, weight=1)
        
        self.tokens_text = scrolledtext.ScrolledText(
            tokens_frame, wrap=tk.WORD, height=10,
            font=("Consolas", 9), bg='#ffffff', fg='#000000'
        )
        self.tokens_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def open_file(self):
        """Abre un archivo y muestra su contenido."""
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo",
            filetypes=[("Archivos Java", "*.java"), ("Archivos de texto", "*.txt"), 
                      ("Todos los archivos", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                self.current_file = filename
                self.code_text.delete(1.0, tk.END)
                self.code_text.insert(1.0, content)
                self.file_label.config(text=f"Archivo: {os.path.basename(filename)}", 
                                      foreground="black")
                self.log_result(f"Archivo cargado: {filename}\n", "info")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir el archivo:\n{str(e)}")
    
    def analyze_file(self):
        """Analiza el contenido del editor."""
        content = self.code_text.get(1.0, tk.END).strip()
        
        if not content:
            messagebox.showwarning("Advertencia", "No hay contenido para analizar.")
            return
        
        # Limpiar resultados previos
        self.result_text.delete(1.0, tk.END)
        self.tokens_text.delete(1.0, tk.END)
        
        # Crear lexer y obtener tokens
        lexer = Lexer(content)
        tokens = list(lexer.get_tokens())
        
        # Mostrar tokens
        self.tokens_text.insert(tk.END, "Tokens identificados:\n")
        self.tokens_text.insert(tk.END, "-" * 80 + "\n")
        for i, token in enumerate(tokens, 1):
            if token.type != '$':
                self.tokens_text.insert(
                    tk.END, 
                    f"{i:3}. Tipo: {token.type:10} Valor: {token.value:15} "
                    f"[Línea {token.line}, Columna {token.column}]\n"
                )
        
        # Realizar análisis sintáctico
        self.log_result("="*80 + "\n", "info")
        self.log_result("ANÁLISIS SINTÁCTICO\n", "info")
        self.log_result("="*80 + "\n\n", "info")
        
        # Crear un nuevo lexer para el parser
        lexer = Lexer(content)
        
        # Crear parser personalizado que escribe en la GUI
        parser = GUIParser(self.parsing_table, START_SYMBOL, self)
        parser.token_stream = lexer.get_tokens()
        parser._next_token()
        
        # Ejecutar análisis
        success = parser.parse_internal()
        
        # Habilitar botones después del primer análisis
        if not self.analysis_performed:
            self.analysis_performed = True
            self.btn_grammar.config(state='normal')
            self.btn_first_follow.config(state='normal')
            self.btn_table.config(state='normal')
        
        if success:
            self.log_result("\n" + "="*80 + "\n", "success")
            self.log_result("✓ ANÁLISIS EXITOSO\n", "success")
            self.log_result("="*80 + "\n", "success")
            self.log_result("La cadena es aceptada por la gramática.\n", "success")
        else:
            self.log_result("\n" + "="*80 + "\n", "error")
            self.log_result("✗ ANÁLISIS FALLIDO\n", "error")
            self.log_result("="*80 + "\n", "error")
    
    def show_grammar(self):
        """Muestra la gramática en los resultados."""
        self.result_text.delete(1.0, tk.END)
        self.log_result("="*80 + "\n", "info")
        self.log_result("GRAMÁTICA (Sin Recursión por la Izquierda)\n", "info")
        self.log_result("="*80 + "\n\n", "info")
        
        for nt, productions in GRAMMAR.items():
            for prod in productions:
                self.log_result(f"{nt} → {' '.join(prod)}\n", "warning")
        
        self.log_result("\n" + "="*80 + "\n", "info")
    
    def show_first_follow(self):
        """Muestra los conjuntos FIRST y FOLLOW."""
        self.result_text.delete(1.0, tk.END)
        
        self.log_result("="*80 + "\n", "info")
        self.log_result("CONJUNTOS FIRST\n", "info")
        self.log_result("="*80 + "\n\n", "info")
        
        for nt, f_set in self.first_sets.items():
            self.log_result(f"FIRST({nt}) = {{{', '.join(sorted(f_set))}}}\n", "warning")
        
        self.log_result("\n" + "="*80 + "\n", "info")
        self.log_result("CONJUNTOS FOLLOW\n", "info")
        self.log_result("="*80 + "\n\n", "info")
        
        for nt, f_set in self.follow_sets.items():
            self.log_result(f"FOLLOW({nt}) = {{{', '.join(sorted(f_set))}}}\n", "warning")
        
        self.log_result("\n" + "="*80 + "\n", "info")
    
    def show_table(self):
        """Muestra la tabla sintáctica LL(1)."""
        self.result_text.delete(1.0, tk.END)
        
        self.log_result("="*80 + "\n", "info")
        self.log_result("TABLA SINTÁCTICA LL(1)\n", "info")
        self.log_result("="*80 + "\n\n", "info")
        
        # Encabezado
        header = f"{'':4} |" + "".join([f"{t:<12}" for t in TERMINALS])
        self.log_result(header + "\n", "warning")
        self.log_result("-" * len(header) + "\n", "warning")
        
        # Filas
        for nt, row in self.parsing_table.items():
            row_str = f"{nt:<4} |"
            for t in TERMINALS:
                prod = row[t]
                if prod is None:
                    row_str += f"{'':<12}"
                elif prod == ['lambda']:
                    row_str += f"{'λ':<12}"
                else:
                    row_str += f"{' '.join(prod):<12}"
            self.log_result(row_str + "\n", "")
        
        self.log_result("\n" + "="*80 + "\n", "info")
    
    def log_result(self, message, tag=""):
        """Agrega un mensaje al área de resultados con formato."""
        self.result_text.insert(tk.END, message, tag)
        self.result_text.see(tk.END)


class GUIParser:
    """Parser adaptado para GUI."""
    
    def __init__(self, table, start_symbol, gui):
        self.table = table
        self.start_symbol = start_symbol
        self.gui = gui
        self.token_stream = None
        self.current_token = None
    
    def _next_token(self):
        """Consume el token actual y obtiene el siguiente."""
        try:
            self.current_token = next(self.token_stream)
        except StopIteration:
            from main import Token
            self.current_token = Token('$', '$', -1, -1)
    
    def parse_internal(self):
        """Análisis interno para GUI."""
        stack = ['$', self.start_symbol]
        
        while stack:
            top_of_stack = stack[-1]
            token_type = self.current_token.type
            token_value = self.current_token.value
            
            # Mostrar estado
            stack_str = str(stack)
            self.gui.log_result(
                f"Pila: {stack_str:<45} Token: ({token_type}, '{token_value}')\n", 
                ""
            )
            
            if top_of_stack == '$' and token_type == '$':
                return True
            
            if top_of_stack in TERMINALS or top_of_stack == '$':
                if top_of_stack == token_type:
                    stack.pop()
                    self._next_token()
                else:
                    self._error(f"Se esperaba '{top_of_stack}' pero se encontró '{token_type}'")
                    return False
            
            elif top_of_stack in NON_TERMINALS:
                production = self.table[top_of_stack].get(token_type)
                
                if production is None:
                    expected = ", ".join([t for t, v in self.table[top_of_stack].items() if v is not None])
                    self._error(f"Token inesperado '{token_type}'. Se esperaba: {expected}")
                    return False
                
                stack.pop()
                
                if production != ['lambda']:
                    for symbol in reversed(production):
                        stack.append(symbol)
                
                prod_str = ' '.join(production) if production != ['lambda'] else 'λ'
                self.gui.log_result(f"   → Aplicando: {top_of_stack} → {prod_str}\n", "info")
            else:
                self._error(f"Símbolo desconocido en la pila: {top_of_stack}")
                return False
        
        return False
    
    def _error(self, message):
        """Manejo de errores."""
        token = self.current_token
        self.gui.log_result(f"\n*** ERROR DE SINTAXIS ***\n", "error")
        self.gui.log_result(f"  {message}\n", "error")
        self.gui.log_result(
            f"  En línea {token.line}, columna {token.column} (token: '{token.value}')\n", 
            "error"
        )


def main():
    """Función principal para ejecutar la GUI."""
    root = tk.Tk()
    app = ParserGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
