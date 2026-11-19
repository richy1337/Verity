#!/usr/bin/env python3
"""Audit MG/MIS traces, dependency consistency, guards and interface completeness.

This checks the design specification, not product behavior or personal attestations.
Run with python3 test/documentation/verify_design.py.
"""
from pathlib import Path
import ast
import re, itertools, json
r=Path(__file__).resolve().parents[2]
mg=(r/'docs/Design/SoftArchitecture/MG.tex').read_text()
mis=(r/'docs/Design/SoftDetailedDes/MIS.tex').read_text()
required=[*(f'FR{i}' for i in range(1,15)),*(f'NFR{i}' for i in range(1,11)),*(f'NFR.E.{i}' for i in range(1,6)),*(f'SR{i}' for i in range(1,10)),*(f'INV{i}' for i in range(1,5)),*(f'H{i}' for i in range(1,11))]
rows={m[1]:[int(i) for i in re.findall(r'\\modref\{(\d+)\}',m[2])] for m in re.finditer(r'^(FR\d+|NFR\d+|NFR\.E\.\d+|SR\d+|INV\d+|H\d+) & (.*?) &',mg,re.M)}
assert set(required)<=rows.keys(),set(required)-rows.keys()
assert all(rows[k] for k in required)
assert set(range(1,11))==set(itertools.chain.from_iterable(rows.values()))
assert set(re.findall(r'AC\d+ & (LC\d+)',mg))=={f'LC{i}' for i in range(1,7)}
changes=re.findall(r'^AC(\d+) & .*? & (.*?) \\\\$',mg,re.M)
assert len(changes)==13 and all(len(re.findall(r'\\modref\{\d+\}',m[1]))==1 for m in changes)

# Parse each MIS Uses list and check its matching diagram edges.
modules={int(n):body for n,body in re.findall(r'\\section\{MIS of M(\d+) [^}]+\}.*?(.*?)(?=%% ------------------------------------------------------------------ M|\\bibliographystyle)',mis,re.S)}
assert set(modules)==set(range(1,11)),modules.keys()
graph={}
for n,body in modules.items():
    uses=body.split('\\subsection{Uses}',1)[1].split('\\subsection{Syntax}',1)[0].strip()
    refs=set()
    for a,b in re.findall(r'M(\d+)--M(\d+)',uses): refs.update(range(int(a),int(b)+1))
    refs.update(map(int,re.findall(r'M(\d+)',uses)))
    graph[n]=refs
    names=set(re.findall(r'\\texttt\{(\w+)\} &',body))
    semantics=set(re.findall(r'\\texttt\{(\w+)\}\(\)',body))
    assert names-{'initialize'}<=semantics,(n,names-semantics)
    assert ('initialize' in names)==(n!=4)
    assert not re.search(r'\\(?:sub)*section\{[^}]+\}(?:\s*\\label\{[^}]+\})?\s*\\(?:sub)*section',body)
diagram=set((int(a),int(b)) for a,b in re.findall(r'\\draw\[->\] \(m(\d+)\) -- \(m(\d+)\);',mg))
for targets,origin in re.findall(r'\\foreach \\i in \{([\d,]+)\} \{\\draw\[[^]]+\] \(m(\d+)\)',mg):
    diagram.update((int(origin),int(b)) for b in targets.split(','))
assert diagram=={(a,b) for a,bs in graph.items() for b in bs},(diagram,graph)
visited=set()
def visit(n,stack):
    assert n not in stack,('cycle',n)
    if n in visited:return
    for dep in graph[n]:visit(dep,stack|{n})
    visited.add(n)
for n in graph:visit(n,set())

table=mis.split('\\label{TblLifecycle}',1)[1].split('\\end{tabularx}',1)[0]
guards=re.findall(r'^\$(.*?)\$ &',table,re.M)
assert len(guards)==5
compiled=[g.replace(r'\neg',' not ').replace(r'\land',' and ').replace(r'\lor',' or ') for g in guards]
for bits in itertools.product([False,True],repeat=5):
    env=dict(zip(['c','d','e','a','v'],bits))
    matches=[]
    for i,g in enumerate(compiled):
        tree=ast.parse(g.strip(),mode='eval')
        allowed=(ast.Expression,ast.BoolOp,ast.UnaryOp,ast.And,ast.Or,ast.Not,ast.Name,ast.Load)
        assert all(isinstance(n,allowed) for n in ast.walk(tree)), 'Unsupported guard expression'
        if eval(compile(tree,'<MIS guard>','eval'),{'__builtins__':{}},env): matches.append(i)
    assert len(matches)==1,(bits,matches)
    c,d,e,a,v=bits
    expected=0 if c else 1 if d or e else 2 if not a else 4 if v else 3
    assert matches[0]==expected
for doc in [mg,mis]:
    labels=set(re.findall(r'\\label\{([^}]+)\}',doc))
    refs=set(re.findall(r'\\(?:ref|pageref)\{([^}]+)\}',doc))
    refs.update(re.findall(r'\\hyperref\[([^]]+)\]',doc))
    refs={v for v in refs if not v.startswith("#")}
    assert refs<=labels,refs-labels
    assert not re.search(r'^\+|\\wss\{|\bTBD\b|Describe \.\.\.',doc,re.M)
    assert not re.search(r'\\(?:sub)*section\{[^}]+\}(?:\s*\\label\{[^}]+\})?\s*\\(?:sub)*section',doc)

constant_table=mis.split('\\label{TblConstants}',1)[1].split('\\end{longtable}',1)[0]
def names(s):return {re.sub(r'\\allowbreak\{\}','',n).replace(r'\_','_') for n in re.findall(r'\\Const\{((?:[^{}]|\{\})+)\}',s)}
assert names(mis)<=names(constant_table), names(mis)-names(constant_table)
assert len(names(constant_table))==16,names(constant_table)
# The implementation plan must cover each module with a distinct owner/reviewer.
schedule=mg.split(r'\label{TblSchedule}',1)[1].split(r'\end{longtable}',1)[0]
assignments=re.findall(r'& M(\d+): ([^;]+); ([^&]+) &',schedule)
assert {int(n) for n,_,_ in assignments}==set(range(1,11))
assert all(owner.strip()!=reviewer.strip() for _,owner,reviewer in assignments)
summary={'modules':len(modules),'requirement_and_hazard_rows':len(rows),'anticipated_changes':len(changes),'dependency_edges':len(diagram),'lifecycle_assignments':32,'exported_constant_values':len(names(constant_table)),'status':'passed'}
print(json.dumps(summary,indent=2))
