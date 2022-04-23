class Variable:
    def __init__(self,name):
        self.name=name
    def __str__(self):
        return self.name

class FunctionCall:
    def __init__(self,f,args):
        self.f=f
        self.args=args
    def __str__(self):
        res=self.f+'('
        for arg in self.args:
            res+=expstr(arg)+', '
        return res[:-2]+')'

class Special: # for a special token such as ( ) , \? or end
    def __init__(self,c):
        self.c=c

class NoRuleFound(Exception):
    pass

def expstr(exp):
    res=''
    lt=None
    for t in exp:
        if lt!=None and (type(lt)==FunctionCall or type(t)==FunctionCall):
            res+=' '
        if type(t)==FunctionCall:
            res+=str(t)
        else:
            for c in esc:
                if t==esc[c]:
                    t='\\'+c
                    break
            if t.isalpha() or t=='(' or t==')' or t==',' or t=='\\' or t=='"':
                t='\\'+t
            res+=t
        lt=t
    return res

esc={'.':'\n', ':':'\r', ';':'\f', '>':'\t', '!':'\a', '?':Special('?')}

def run(file):
    f=open(file)
    global rules,trace
    rules={}
    for line in f:
        parse(line)
    f.close()
    state=[FunctionCall('A',[[]])]
    while len(state)>0:
        fc,pos,parent=findFC(state)
        defs=rules[fc.f]
        args=[''.join(arg) for arg in fc.args]
        res=None
        for defi in defs:
            res=match(defi,args)
            if res!=None:
                break
        if res==None:
            raise NoRuleFound('no match found for '+str(fc))
        if trace:
            print(str(fc),'=',expstr(res))
        rescomp=parent[:pos]+res+parent[pos+1:]
        parent.clear()
        parent.extend(rescomp)
        while len(state)>0 and type(state[0])==str:
            if trace:
                print('Output:',state.pop(0))
            else:
                print(state.pop(0),end='')

def parse(line):
    line=line.strip()
    if line=='' or not line[0].isalpha():
        return
    tok=[]
    i=0
    string=False
    while i<len(line):
        c=line[i]
        if c.isalpha() and not string:
            j=i+1
            while j<len(line) and line[j].isalpha():
                j+=1
            tok.append(Variable(line[i:j]))
            i=j
        elif (c=='(' or c==')' or c==',') and not string:
            tok.append(Special(c))
            i+=1
        elif c.isspace() and not string:
            i+=1
        elif c=='\\':
            c=line[i+1]
            if c in esc:
                tok.append(esc[c])
            else:
                tok.append(c)
            i+=2
        elif c=='"':
            string=not string
            i+=1
        else:
            tok.append(c)
            i+=1
    tok.append(Special(''))
    f=tok[0].name
    if type(tok[1])!=Special or tok[1].c!='(':
        raise SyntaxError(line+': ( expected after function name')
    i=1
    lhs=[]
    while tok[i].c!=')':
        arg,i=parseLHSArg(tok,i)
        if tok[i].c=='':
            raise SyntaxError(line+': line ends prematurely')
        if tok[i].c=='(':
            raise SyntaxError(line+
                              ": can't call a function in argument pattern")
        if tok[i].c=='?':
            raise SyntaxError(line+": can't do input in argument pattern")
        lhs.append(arg)
    i+=1
    if tok[i]!='=':
        raise SyntaxError(line+': = expected after argument pattern')
    rhs,i=parseRHSArg(line,tok,i)
    if tok[i].c!='':
        raise SyntaxError(line+': invalid '+tok[i].c)
    if f in rules:
        rules[f].append((lhs,rhs))
    else:
        rules[f]=[(lhs,rhs)]

def parseLHSArg(tok,i):
    pat=['']
    i+=1
    t=tok[i]
    while type(t)!=Special:
        if type(t)==Variable:
            pat.append((t.name,''))
        else:
            if len(pat)==1:
                pat[0]+=t
            else:
                pat[-1]=(pat[-1][0],pat[-1][1]+t)
        i+=1
        t=tok[i]
    return pat,i

def parseRHSArg(line,tok,i):
    exp=[]
    while True:
        i+=1
        t=tok[i]
        if type(t)!=Special or t.c=='?':
            exp.append(t)
            continue
        if t.c!='(':
            return exp,i
        lt=exp.pop() # the last 'variable', which is the function name
        if type(lt)!=Variable:
            raise SyntaxError(line+': invalid (')
        args=[]
        while tok[i].c!=')':
            arg,i=parseRHSArg(line,tok,i)
            if tok[i].c=='':
                raise SyntaxError(line+': line ends prematurely')
            args.append(arg)
        exp.append(FunctionCall(lt.name,args))

def addValue(dic,var,val):
    if var in dic:
        if dic[var]!=val:
            raise ValueError
    else:
        dic[var]=val

def match(rule,args):
    if len(args)!=len(rule[0]):
        return None
    dic={}
    try:
        for arg,pat in zip(args,rule[0]):
            matchArg(pat,arg,dic)
    except ValueError or IndexError:
        return None
    return subs(rule[1],dic,rule[0])

def matchArg(pat,string,dic):
    if len(pat)==1:
        if pat[0]==string:
            return
        else:
            raise ValueError
    start=pat[0]
    if string[:len(start)]!=start:
        raise ValueError
    lvar,end=pat[-1]
    pat=pat[1:-1]
    pos=len(start)
    for var,term in pat:
        if term=='': # no terminator
            addValue(dic,var,string[pos])
            pos+=1
        else:
            ind=string.index(term,pos)
            addValue(dic,var,string[pos:ind])
            pos=ind+len(term)
    string=string[pos:]
    if end=='':
        addValue(dic,lvar,string)
        return
    if string[-len(end):]!=end:
        raise ValueError
    addValue(dic,lvar,string[:-len(end)])

def subs(s,dic,lhs):
    res=[]
    for item in s:
        if type(item)==Variable:
            try:
                res.append(dic[item.name])
            except KeyError:
                raise NameError("'"+item.name+"' not found")
        elif type(item)==FunctionCall:
            res.append(FunctionCall(item.f,
                                    [subs(arg,dic,lhs) for arg in item.args]))
        elif type(item)==Special: # can only be \?
            if trace:
                res.append(input('Input: '))
            else:
                res.append(input())
        else:
            res.append(item)
    return res

# returns a function call, its position, and the expression that contains it
def findFC(exp):
    for i,obj in enumerate(exp):
        if type(obj)==FunctionCall:
            for arg in obj.args:
                ret=findFC(arg)
                if ret!=None:
                    return ret
            # no argument contains a function call
            return obj,i,exp

if __name__=='__main__':
    name=input('Enter filename: ')
    trace=input('Trace evaluation? (y/n) ')=='y'
    run(name)
