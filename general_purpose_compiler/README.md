# Компилятор подмножества Pascal

Учебный компилятор: лексический и синтаксический анализ, AST, семантика, оптимизации, три целевых представления.

## Возможности языка

- Типы: `integer`, `real`, `boolean`, `char`, `string`, массивы
- Операторы: присваивание, `if`, `while`, `for`, `repeat`/`until`
- Ввод-вывод: `read`, `readln`, `write`, `writeln`
- Арифметика: `+`, `-`, `*`, `/`, `div`, `mod`, сравнения, `and`, `or`, `not`
- Функции без параметров: `function name: type; begin ... end;`

## Этапы компиляции

1. `Lexer` — токены
2. `Parser` — AST
3. `SemanticAnalyzer` — типы и ошибки, вставка `Cast`
4. `optimize` — свёртка констант, упрощение выражений, ветки `if` с константным условием
5. Целевой код:
   - **Python** (`PythonCodeGenerator`) — исполняемый `.py`
   - **x86** (`X86CodeGenerator`) — NASM, 32-bit
   - **Интерпретатор** (`Interpreter`) — выполнение по AST

## Запуск

```bash
cd general_purpose_compiler
python main_file.py
```

Сгенерированные файлы: `generated/*_generated.py`, `generated/*_generated.asm`.

Запуск сгенерированного Python:

```bash
python generated/test2_generated.py
```

Сборка x86 (нужны NASM и MinGW/gcc):

```bash
nasm -f win32 generated/test2_generated.asm -o generated/test2.obj
gcc generated/test2.obj -o generated/test2.exe -lmsvcrt
generated/test2.exe
```

Проверка семантических ошибок:

```bash
python run_semantic_checks.py
```

Пример из строки:

```bash
python main_string.py
```

## Структура

| Файл | Назначение |
|------|------------|
| `lexer.py` | Лексер |
| `parser.py` | Парсер |
| `ast.py` | Узлы AST |
| `semantic_analyzer.py` | Семантика |
| `optimizer.py` | Оптимизации AST |
| `code_generator.py` | Код Python |
| `x86_codegen.py` | Код x86 |
| `interpreter.py` | Интерпретатор AST |
| `PascalSubset.g4` | Грамматика ANTLR |
| `examples/` | Тестовые программы |

## Примеры

- `test1` — вывод строки
- `test2` — арифметика
- `test3` — `if` и `read`
- `test4` — `repeat`/`until`
- `test5` — массивы и циклы
- `test6_function` — вызов функции

## Оптимизации

- Вычисление константных выражений
- `x + 0`, `x * 1`, `x * 0`, `x - 0`
- Удаление недостижимых веток `if` при константном условии
