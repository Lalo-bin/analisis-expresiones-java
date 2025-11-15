# 📖 Manual de Usuario - Analizador Sintáctico LL(1)

### **Ejecutar la Aplicación**

```bash
python gui.py
```

Se abrirá la interfaz gráfica del analizador sintáctico.

---

## Funcionalidades Principales

### **1. Abrir un Archivo**

1. Haz clic en el botón **📁 Abrir Archivo**
2. Selecciona un archivo `.java` o `.txt` con código a analizar
3. El contenido aparecerá en el panel "Código de Entrada"

También puedes escribir o pegar código directamente en el editor.

---

### **2. Analizar el Código**

1. Asegúrate de tener código en el editor (cargado o escrito manualmente)
2. Haz clic en el botón **▶ Analizar**
3. El análisis se ejecutará y mostrará:
   - **Tokens identificados** (panel inferior)
   - **Proceso paso a paso** (panel derecho)
   - **Resultado**: ✅ Exitoso o ❌ Error con descripción

**Después del primer análisis**, se habilitarán los botones de información.

---

### **3. Consultar Información del Análisis**

Una vez realizado el análisis, puedes consultar:

#### ** Mostrar Gramática**

- Muestra la gramática sin recursión por la izquierda
- Formato: `E → T EP`, `EP → + T EP | λ`, etc.

#### ** Mostrar FIRST/FOLLOW**

- **FIRST(X)**: Conjunto de terminales que pueden iniciar X
- **FOLLOW(X)**: Conjunto de terminales que pueden seguir a X

#### ** Mostrar Tabla**

- Tabla sintáctica LL(1) completa
- Formato: Filas = No-terminales, Columnas = Terminales
- Cada celda indica qué producción aplicar

---

## Sintaxis Válida

### **Operadores Soportados:**

- `+` Suma
- `-` Resta
- `*` Multiplicación
- `/` División
- `%` Módulo

### **Elementos:**

- **Números**: `5`, `3.14`, `100`
- **Identificadores**: `x`, `variable`, `num1`
- **Paréntesis**: `(` y `)`

### **Ejemplos Válidos:**

```java
5 + 3
20 * 30
(5 + 3) * 2
x + y * z
10 % 3
((a + b) * (c - d))
variable
```

---

## ❌ Errores Comunes

### **Error: Operador sin operando**

```java
5 +        ❌ Falta operando después del +
```

### **Error: Paréntesis sin cerrar**

```java
(5 + 3     ❌ Falta paréntesis de cierre
```

### **Error: Operadores consecutivos**

```java
5 + * 3    ❌ Dos operadores seguidos
```

### **Error: Paréntesis vacíos**

```java
()         ❌ Debe haber una expresión dentro
```

---

## Interpretación de Resultados

### **Panel de Tokens (Inferior)**

Muestra cada token reconocido con:

- **Tipo**: `num`, `id`, `+`, `-`, `*`, `/`, `%`, `(`, `)`
- **Valor**: El texto literal del token
- **Posición**: Línea y columna en el código

### **Panel de Resultados (Derecha)**

Muestra el proceso de análisis:

- **Pila**: Estado actual de la pila de símbolos
- **Token**: Token de entrada actual
- **Aplicando**: Regla de la gramática aplicada
- **Colores**:
  - 🟢 Verde: Éxito
  - 🔴 Rojo: Error
  - 🔵 Azul: Información
  - 🟡 Amarillo: Reglas aplicadas

---

## 💡 Consejos de Uso

1. **Prueba expresiones simples primero** (`5 + 3`) antes de complejas
2. **Usa paréntesis** para clarificar precedencia: `(a + b) * c`
3. **Revisa los tokens** para verificar que se reconocen correctamente
4. **Lee los mensajes de error** - indican línea, columna y el problema específico
5. **Consulta la gramática** si no entiendes por qué algo es inválido

---

## Solución de Problemas

### **La aplicación no inicia**

```bash
# Verifica que tienes Python instalado
python --version

# Instala tkinter si falta (viene con Python por defecto)
```

### **Error al importar main.py**

- Asegúrate de que `main.py` y `gui.py` están en la misma carpeta

### **Los botones no se habilitan**

- Debes hacer clic en "▶ Analizar" al menos una vez

---

## Notas Técnicas

- **Gramática**: LL(1) sin recursión por la izquierda
- **Analizador**: Descendente predictivo dirigido por tabla
- **Tokens**: Reconocidos mediante expresiones regulares
- **Precedencia**: `*` y `/` tienen mayor precedencia que `+`, `-` y `%`

---

## Referencia Rápida

| Acción          | Botón/Atajo             |
| --------------- | ----------------------- |
| Abrir archivo   | 📁 Abrir Archivo        |
| Analizar código | ▶ Analizar              |
| Ver gramática   | 📋 Mostrar Gramática    |
| Ver conjuntos   | 📊 Mostrar FIRST/FOLLOW |
| Ver tabla       | 🗂️ Mostrar Tabla        |
