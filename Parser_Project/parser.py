import re
import sys

inputString = ""
nextToken = ""


def lex():
    global inputString
    global nextToken
    termList = ['program', 'if', 'while', 'begin', 'read', 'write', 'then', 'else', 'do']

    # match 'end'
    p = re.compile('(end)')
    m = p.match(inputString)
    if m is not None:
        nextToken = 'end'
        # handle if we have nested programs (ie structured stmt)
        if len(inputString) > 3:
            inputString = inputString.replace(m.group(1) + " ", "", 1)
        else:
            inputString = inputString.replace(m.group(1), "", 1)
        return m.group(1)

    # match parenthesis
    p = re.compile('([(),;]) ')
    m = p.match(inputString)
    if m is not None:
        if m.group(1) == '(':
            nextToken = '<leftParenthesis>'
            inputString = inputString.replace(m.group(1) + " ", "", 1)
            return m.group(1)
        elif m.group(1) == ')':
            nextToken = '<rightParenthesis>'
            inputString = inputString.replace(m.group(1) + " ", "", 1)
            return m.group(1)
        elif m.group(1) == ',':
            nextToken = '<comma>'
            inputString = inputString.replace(m.group(1) + " ", "", 1)
            return m.group(1)
        elif m.group(1) == ';':
            nextToken = ';'
            inputString = inputString.replace(m.group(1) + " ", "", 1)
            return m.group(1)

    # match assignment
    p = re.compile('(:=) ')
    m = p.match(inputString)
    if m is not None:
        nextToken = '<assignment_op>'
        inputString = inputString.replace(m.group(1) + " ", "", 1)
        return m.group(1)

    # match + | -
    p = re.compile('([+-]) ')
    m = p.match(inputString)
    if m is not None:
        if nextToken == '<term>':
            nextToken = '<adding_operator>'
            inputString = inputString.replace(m.group(1) + " ", "", 1)
            return m.group(1)
        else:
            nextToken = '<sign>'
            inputString = inputString.replace(m.group(1) + " ", "", 1)
            return m.group(1)

    # match * | /
    p = re.compile('([*/]) ')
    m = p.match(inputString)
    if m is not None:
        if nextToken == '<factor>':
            nextToken = '<multiplying_operator>'
            inputString = inputString.replace(m.group(1) + " ", "", 1)
            return m.group(1)

    p = re.compile('([=><][=>]?) ')
    m = p.match(inputString)
    if m is not None:
        if len(m.group(1)) == 1:
            nextToken = '<relational_operator>'
            inputString = inputString.replace(m.group(1) + " ", "", 1)
            return m.group(1)
        elif m.group(1)[0] == '=' or m.group(1)[0] == '>' or m.group(1)[0] == '<':
            if m.group(1)[1] == '=':
                nextToken = '<relational_operator>'
                inputString = inputString.replace(m.group(1) + " ", "", 1)
                return m.group(1)
        elif m.group(1)[1] == '>':
            if m.group(1)[0] != '=':
                nextToken = '<relational_operator>'
                inputString = inputString.replace(m.group(1) + " ", "", 1)
                return m.group(1)

    p = re.compile('([A-Za-z]\w*) ')
    m = p.match(inputString)
    if m is not None:
        p2 = re.compile('([A-Z]\w*) ')
        m2 = p2.match(inputString)
        if m.group(1) in termList:
            nextToken = m.group(1)
            inputString = inputString.replace(m.group(1) + " ", "", 1)
            return m.group(1)
        elif m2 is not None and nextToken == 'program':
            nextToken = '<progname>'
            inputString = inputString.replace(m2.group(1) + " ", "", 1)
            return m.group(1)
        else:
            nextToken = '<variable>'
            inputString = inputString.replace(m.group(1) + " ", "", 1)
            return m.group(1)

    p = re.compile('([1-9]\d*) ')
    m = p.match(inputString)
    if (m is not None) or (inputString[0] == '0'):
        nextToken = '<constant>'
        inputString = inputString.replace(m.group(1) + " ", "", 1)
        return m.group(1)

    # grab unidentified symbol
    p = re.compile('([^\s]+)')
    m = p.match(inputString)
    print('Unrecognizable symbol error')
    sys.exit('Lex analyzer: Unrecognized symbol ' + m.group(1))


# <program> ::= program <progname> <compound stmt>
def program():
    global inputString
    global nextToken
    lex()
    if nextToken == 'program':
        lex()
        if nextToken == '<progname>':
            compound_stmt()
            return
        else:
            print("Expected a program name; got " + nextToken)
            sys.exit(3)
    else:
        print("Expected 'program' got " + nextToken)
        sys.exit(2)


# <compound stmt> ::= begin <stmt> {; <stmt>} end
def compound_stmt():
    global inputString
    global nextToken
    lex()
    if nextToken == 'begin':
        stmt()
        lex()
        while nextToken == ';':
            stmt()
            lex()
        if nextToken == 'end':
            return
        else:
            print("Error program failed to exit properly")
            sys.exit('compound_stmt_end')
    else:
        print("Expected 'begin' got " + nextToken)
        sys.exit('compound_stmt_start')


# <stmt> ::= <simple stmt> | <structured stmt>
def stmt():
    global inputString
    global nextToken
    lex()
    if nextToken == 'read' or nextToken == 'write' or nextToken == '<variable>':
        simple_stmt()
        return
    elif nextToken == 'begin' or nextToken == 'if' or nextToken == 'while':
        structured_stmt()
        return
    else:
        print("Error: Expected statement keyword, got ", nextToken)
        sys.exit('stmt')

# <structured stmt> ::= <compound stmt> | <if stmt> | <while stmt>
def structured_stmt():
    global inputString
    global nextToken

    if nextToken == 'begin':
        # put 'begin' flag back
        inputString = 'begin ' + inputString
        compound_stmt()
        return
    elif nextToken == 'if':
        if_stmt()
        return
    elif nextToken == 'while':
        while_stmt()
        return

# <if stmt> ::= if <expression> then <stmt> | if <expression> then <stmt> else <stmt>
def if_stmt():
    global inputString
    global nextToken
    expression_stmt()
    lex()
    if nextToken == 'then':
        stmt()
        tok = lex()
    else:
        print('Improperly structured if statement')
        sys.exit('if_stmt')
    if nextToken == 'else':
        stmt()
    else:
        if nextToken == 'end':
            inputString = 'end'
        else:
            inputString = tok + ' ' + inputString
    return

# <while stmt> ::= while <expression> do <stmt>
def while_stmt():
    global inputString
    global nextToken
    expression_stmt()
    lex()
    if nextToken == 'do':
        stmt()
    else:
        print('Improperly structured while statement')
        sys.exit('while_stmt')
    return

# <simple stmt> ::= <assignment stmt> | <read stmt> | <write stmt>
def simple_stmt():
    global inputString
    global nextToken

    if nextToken == 'read':
        read_stmt()
        return
    elif nextToken == 'write':
        write_stmt()
        return
    elif nextToken == '<variable>':
        assign_stmt()
        return

# <read stmt> ::= read ( <variable> { , <variable> } )
def read_stmt():
    global inputString
    global nextToken
    lex()
    # loop until we close the function
    if nextToken == '<leftParenthesis>':
        lex()
        try:
            while nextToken != '<rightParenthesis>':
                lex()
        except IndexError:
            print('Read statement not closed properly')
            sys.exit('read_stmt')
    else:
        print('Error expected (, got ', nextToken)
        sys.exit('read_stmt')
    return

# <write stmt> ::= write ( <expression> { , <expression> } )
def write_stmt():
    global inputString
    global nextToken
    lex()
    # loop until we close the function
    if nextToken == '<leftParenthesis>':
        try:
            while nextToken != '<rightParenthesis>':
                expression_stmt()
                lex()
        except IndexError:
            print('Write statement not closed properly')
            sys.exit('write_stmt')
    else:
        print('Error expected (, got ', nextToken)
        sys.exit('write_stmt')
    return

# <assignment stmt> ::= <variable> := <expression>
def assign_stmt():
    global inputString
    global nextToken
    lex()
    if nextToken == '<assignment_op>':
        expression_stmt()
    else:
        print('Error expected assignment op, got ', nextToken)
        sys.exit('assign_stmt')
    return

# <expression> ::= <simple expr> | <simple expr> <relational_operator> <simple expr>
def expression_stmt():
    global inputString
    global nextToken
    simple_expr()
    # check for relational operator
    # terminal hit - put back

    tok = lex()
    if nextToken == '<relational_operator>':
        simple_expr()
    elif nextToken == 'end':
        inputString = tok
    elif nextToken == '<rightParenthesis>':
        inputString = tok + ' ' + inputString
    else:
        print('Error expression not properly closed')
        sys.exit('expr_stmt')
    return

# <simple expr> ::= [ <sign> ] <term> { <adding_operator> <term> }
def simple_expr():
    global inputString
    global nextToken
    lex()
    # check for sign
    # if sign, grab next token
    # else descend
    if nextToken == '<sign>':
        lex()
        term()
    elif nextToken == '<variable>' or nextToken == '<constant>' or nextToken == '<leftParenthesis>':
        term()
    else:
        sys.exit('simple_expr')
    # check if the next value is { <adding_operator> <term> }
    # if not, put back the symbol
    while True:
        nextToken = '<term>'
        tok = lex()
        if nextToken == '<adding_operator>':
            lex()
            term()
        elif nextToken == 'end':
            inputString = nextToken
            return
        else:
            inputString = tok + ' ' + inputString
            return

# <term> ::= <factor> { <multiplying_operator> <factor> }
def term():
    global inputString
    global nextToken
    factor()
    # check if the next value is { <multiplying_operator> <factor> }
    # if not, put back the symbol
    while True:
        nextToken = '<factor>'
        tok = lex()
        if nextToken == '<multiplying_operator>':
            lex()
            factor()
        elif nextToken == 'end':
            inputString = nextToken
            return
        else:
            inputString = tok + ' ' + inputString
            return

# <factor> ::= <variable> | <constant> | ( <expression> )
def factor():
    global inputString
    global nextToken
    if nextToken == '<variable>' or nextToken == '<constant>':
        return
    elif nextToken == '<leftParenthesis>':
        expression_stmt()
        # consume right parenthesis
        lex()
        return
    else:
        print('Did not find terminal or expression')
        sys.exit('factor')

# console input
def manual_parser():
    global inputString
    inputString = input("Enter a string: ")
    try:
        print(inputString)
        program()
        print("The string is syntactically correct! :)\n")
    except SystemExit:
        print(sys.exc_info())
        print("Program exception raised\n")

# file I/O function
# treat '#' as a comment - does not pass line to program()
def parser(fileName):
    global inputString
    with open(fileName, 'r') as file:
        programs = file.readlines()
        for inputString in programs:
            inputString = inputString.replace('\n', '')
            if inputString[0] != '#':
                try:
                    print(inputString)
                    program()
                    print("The string is syntactically correct! :)\n")
                except SystemExit:
                    print(sys.exc_info())
                    print("Program exception raised\n")

# pass file to run program
parser('ValidTestProgram.txt')
