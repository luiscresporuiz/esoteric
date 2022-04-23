'''FThue''' is a programming language invented by [[User:LuisCR]]. It is similar to [[Thue]], and adds to the same line as [[Thube]], [[Thubi]], [[Thutu]] and [[Object-oriented Thue]]. What makes FThue different is that, instead of a "working string", it uses a ''working expression''.

In Thue, as you know, the program state is a string, that is nothing but a sequence of characters. In FThue, instead, the sequence contains characters but also ''function calls''. A function call consists in a ''head'', which is the function name, and one or more ''arguments'', that are expressions themselves. For example, this is an expression:

 12 f(3,g(4),5)

This has two characters, <code>1</code> and <code>2</code>, followed by a call to the function <code>f</code> with the arguments <code>3</code>, <code>g(4)</code> and <code>5</code>. Yes, the second argument contains another function call. The space is ignored.

Same as in Thue, the program is a list of rules, but in this case the rules are given as definitions of functions. For example

 g(x) = x1
 f(a,b,c) = c b a

The letters here are not fixed strings, but variables that can represent every string. With this, the expression above becomes

 12 f(3,41,5)

and then

 125413

You can also give a definition that only accepts arguments starting with <code>1</code>: just put <code>g(1x)</code> as left hand side. Also ending in <code>1</code>: <code>g(x1)</code>. Or containing <code>1</code>: <code>g(x1y)</code>. Or only <code>1</code>: <code>g(1)</code>.

Suppose you want to write the "Hello, world!" program. Knowing that the initial state is <code>A()</code> and a newline is <code>\.</code>, you will be tempted to write

 A() = Hello, world!\.

This gives an error. Obviously <code>Hello</code> and <code>world</code> are being parsed as variables, which are not in the left hand side. Moreover, the comma is a special character to separate arguments: it makes no sense outside a function. And, let me repeat, the space is ignored.
What can we do?

Well, it turns out that putting a backslash before a character removes the special meaning of that character. This includes letters, parentheses, commas and spaces. So we could write

 A() = \H\e\l\l\o\,\ \w\o\r\l\d!\.

This doesn't seem a good solution. But there is another escaping method: the double quote.

 A() = "Hello, world!\."

(Note how the <code>\</code> is still special inside quotes.)

==Source format==

A FThue program is a sequence of rules/function definitions. Each one consists in a function call with the argument pattern, followed by an equals sign, and the definition.

 instruction := <fc> = <expr>
 expr := (<char>|<string>|<var>|<fc>)*
 char := [^\\"a-zA-Z(),]|\\.
 string := "([^\\"]|\\.)*"
 var := [A-Za-z]+
 fc := <var>\(<expr>(,<expr>)*\)

That is:

- <code>\</code> forms an escape sequence with the next character. <code>\.</code> is newline, <code>\:</code> is carriage return, <code>\></code> is tab, <code>\;</code> is form feed, <code>\!</code> is alarm, and <code>\?</code> will be replaced by a line of input. Any other escape sequence <code>\c</code> represents the same character <code>c</code>.
- <code>"</code> starts a string. From then and until the next <code>"</code>, all the characters are normal except <code>\</code>.
- Unescaped letters form variables.
- <code>(</code> starts the arguments of a function. It must be after a "variable" (which is not a variable, but a function name).
- <code>,</code> ends an argument and starts the next.
- <code>)</code> ends a function call.
- Spaces are ignored (unless escaped or in a string).
- The rest of characters are normal and will represent themselves. (Concretely, <code>=</code> is a normal character; it is only special after the first <code>)</code>).

This implies that all code lines start with a letter. Any line not starting with a letter is a comment.

==Argument pattern==

Each argument in the left hand side of a rule is a sort of "regular expression" that will match some values of the argument. The matching proceeds from left to right without backtracking.

- A character, or character sequence, matches itself and rejects any other thing.
- A variable at the end of the pattern matches everything left.
- A variable followed by a character sequence, not at the end of the pattern, matches everything until the first appearance of the sequence (excluded), and rejects if the sequence does not appear.
- A variable followed by a character sequence, at the end of the pattern, rejects the argument if it does not end with the sequence, otherwise, the sequence is removed and the rest is matched.
- A variable followed by another variable matches one character and rejects if there are no more.
- A variable already matched in the same rule is treated as if it was new, but if the new value is different from the one already matched, it is rejected.

For example:

- <code>x1 y z12 t3</code> matches <code>21212123</code>: <code>x=2, y=2, z=empty, t=12</code>
- <code>x1 y z12 t3</code> does not match <code>212121234567</code>.
- <code>x1 y z12 t3 end</code> matches <code>212121234567</code>: <code>x=2, y=2, z=empty, t=12, end=4567</code>
- <code>a b c d e</code> matches every string with at least 4 characters (<code>e</code> may be empty, but the rest must take a character).

==Execution==

The working expression starts as <code>A()</code>. Then the following steps are repeated:

1. The next function to evaluate is located: it is the first function call that has no function call inside. Note that its arguments will be strings.
2. One by one, the definitions for this function are tried, in the order they appear in the program: to be accepted, a definition must have the same number of arguments than the call and the patterns must match the arguments in the call. If no definition is accepted, execution stops with an error.
3. In the right hand side of the accepted rule, the variables are replaced by the matched text, and the sequence <code>\?</code> by a line read from input, including the trailing newline.
4. In the working expression, the function to evaluate located in step 1 is replaced by the result of step 3.
5. All characters in the beginning of the working expression, if there is any, are removed and printed.
6. If the working expression is empty, execution halts; otherwise, go back to step 1.

==Examples==

===[[Hello, world!]]===

 A() = "Hello, world!\."

===[[Cat]]===

 A() = \?

===Addition of two input integers===

 rev(a\.) = rev(a)
 rev(x a) = rev(a) x
 rev() =
 
 U(x) = U(x, 0123456789)
 U(x, x r) =
 U(x, y r) = 1 U(x, r)
 
 D(x) = D(x, 0123456789)
 D(, d r) = d
 D(1 x, d r) = D(x, r)
 
 A() = A(rev(\?), rev(\?), )\.
 A(x a, y b, c) = B(U(x) U(y) c, a, b)
 A(, b, ) = rev(b)
 A(, b, 1) = A(0, b, 1)
 A(a, , c) = A(, a, c)
 
 B(1111111111 res, a, b) = A(a, b, 1) D(res)
 B(res, a, b) = A(a, b, ) D(res)

The first function defined, <code>rev</code>, takes a string, removes any newline from the end, and reverses the result.

The function <code>U</code> converts a digit to unary. It works by searching the digit in the string <code>0123456789</code> and returning a 1 for each digit skipped.

The function <code>D</code> is the inverse to the previous one, removing a character from <code>0123456789</code> for each 1 in the argument, and returning the first remaining digit.

With this we can define the main function <code>A</code>. At the beginning it reads two inputs and reverses them. A third argument is initialized empty, but it can hold a 1 if there is a carry. Then it converts to unary the first digit of the two numbers and joins the resulting strings, possibly together with the carry, and passes it to another function <code>B</code>, with the remainder of the operands as second and third arguments.

The function <code>B</code> decides the value of the result's digit, converting it back to decimal, and calls back <code>A</code> with the remaining digits and the new value of the carry. The loop ends when an operand becomes empty and there is no carry, at which point the remaining digits are reversed and printed.

==Computational class==
FThue is Turing-complete because there is a reduction from Thue.

{| class="wikitable"
!Thue
!FThue
|-
|<code>1::=2</code>
|<code>a(x1y)=a(x2y)</code>
|-
|<code>1::=~2</code>
|<code>a(x1y)=2 a(xy)</code>
|-
|<code>1::=:::</code>
|<code>a(x1y)=a(x\?y)</code>
|-
|<code>::=
1234</code>
|<code>A()=a(1234)</code>
|}

==External resources==

[** Interpreter and sample programs]

[[Category:Languages]]
[[Category:String rewriting]]
[[Category:Turing complete]]
[[Category:Implemented]]