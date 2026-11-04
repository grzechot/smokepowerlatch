import re

def parse(txt):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', txt)
    st = [[]]
    for t in toks:
        if t == '(':
            st.append([])
        elif t == ')':
            x = st.pop(); st[-1].append(x)
        else:
            st[-1].append(t)
    return st[0][0]

def dump(x, ind=0):
    if not isinstance(x, list):
        return x
    if all(not isinstance(e, list) for e in x):
        return '(' + ' '.join(x) + ')'
    s = '(' + ' '.join(e for e in x if not isinstance(e, list))
    for e in x:
        if isinstance(e, list):
            s += '\n' + '\t' * (ind + 1) + dump(e, ind + 1)
    return s + ')'

def find(x, key):
    return [e for e in x if isinstance(e, list) and e and e[0] == key]

def uq(s):
    return s[1:-1] if s.startswith('"') else s
