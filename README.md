# oo2c-compiler
# oo2c Compiler (Object-Oriented oo2c → C)

A small source-to-source compiler that translates the object-oriented language **oo2c** into **C**.
The project uses **ANTLR** for parsing and a custom compilation pipeline implemented in **Python**.

## Language Overview
oo2c is an object-oriented language inspired by a subset of Python:
- Programs contain **classes** and a `main` entry point
- Supports class inheritance, fields, methods, constructors (`__init__`)
- Supported statements include `if/else`, `while`, `print`, `return`, assignments, and method calls
- Access to object fields/methods uses dot notation (e.g., `obj.field`, `obj.method(...)`)

(Grammar/spec based on coursework definition of oo2c.)  

## Compiler Pipeline
1. **Parsing (ANTLR)**  
   The grammar (`oos.g4`) is used to generate a lexer/parser.
2. **Symbol Collection / Semantic Checks**  
   Builds symbol tables for classes, fields, methods, and validates basic semantic rules.
3. **Code Generation (C output)**  
   Translates oo2c constructs into equivalent procedural C code.

## Project Structure
- `grammar/oos.g4` : ANTLR grammar for oo2c
- `src/` : compiler implementation (symbol collection + code generation)
- `examples/` : sample oo2c programs used for testing
- `output/` : generated C output (ignored by git)

## How to Run

The compiler translates an oo2c source file into C code, which can then be compiled and executed.

### 1) Translate oo2c to C
From the project root directory:

``bash
`py test_symbols.py examples/shape.oos > out.c`

### 2) Compile the generated C code
Using gcc (e.g. via MinGW):
``bash
`gcc out.c -o out.exe`

3) Run the executable
``bash
`./out.exe`
