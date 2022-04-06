# TinyGo

A simple `Golang` subset interpreter based `Python`.

## Usage
### Quick start
```shell
python3 tinygo.py test.go
```
which will interpret  `test.go` and print result from function `main()`.

## Rule 

* Package declaration
  * `"package" ident`
* Function declaration
  * `"func" ident"("ident type")" (type) "{" {statement} "}"`
* Variable declaration
  * `"var" ident type`
* Type
  * `["int" | "float"]`
* Assign Operator
  * `ident "=" expression | ident "(" (expression)* ")"`
* Expression
  * `term {( "-" | "+" ) term}`
* Term
  * `unary {( "/" | "*" ) unary}`
* Unary
  * `["+" | "-"] primary`
* Primary
  * `number | ident "(" (expression)* ")" | "(" expression ")"`
* Condition
  * `expression (("==" | "!=" | ">" | ">=" | "<" | "<=") expression)`
* For Statement
  * `"for" condition "{" {statement} "}"`
* If Statement
  * `"if" condition "{" {statement} "}"`
* Return Statement
  * `"return" expression`

## Reference:
* [Let’s Build A Simple Interpreter.](https://ruslanspivak.com/lsbasi-part1/)
* [Let's make a Teeny Tiny compiler.](https://austinhenley.com/blog/teenytinycompiler1.html)


