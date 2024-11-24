'''
 Copyright (C) 2024 Cristian Ioan Vasile <cvasile@lehigh.edu>
 Explainable Robotics Lab, Lehigh University
 See license.txt file for license information.
'''

from stl import Operation, RelOperation


template_latex_standalone = r'''
\documentclass{{standalone}}
\usepackage{{amsmath}}
\usepackage{{amssymb}}
\usepackage{{amsfonts}}
\usepackage{{tikz}}
{tikz_libraries}

{tikz_style}

\begin{{document}}
{figure}
\end{{document}}
'''

template_use_tikz_library = r'\usetikzlibrary{{{lib}}}'

template_figure = r'''
\begin{{tikzpicture}}[->,>=stealth',level/.style={{sibling distance = 5cm/#1, level distance = 1.5cm}}]
{tree}
\end{{tikzpicture}}
'''

template_tree = r'''\{tree}
;
'''

template_node = r'''node [{style}] {{{text}}} {children}'''

template_child = r'''child {{
{node}
}}'''

template_style_block = r'''\tikzset{{
    treenode/.style = {{align=center, text centered}},
{node_styles}
}}'''

default_node_styles = {
    'leaf':
        r'''    leaf/.style = {{treenode, ellipse, black, draw=black}},''',
    'intermediate':
        r'''    intermediate/.style = {{treenode, ellipse, black, draw=black}},''',
}


node_styles = {
    Operation.BOOL: 'leaf',
    Operation.PRED: 'leaf',
    Operation.AND: 'intermediate',
    Operation.OR: 'intermediate',
    Operation.IMPLIES: 'intermediate',
    Operation.NOT: 'intermediate',
    Operation.ALWAYS: 'intermediate',
    Operation.EVENT: 'intermediate',
    Operation.UNTIL: 'intermediate',
    # Operation.RELEASE: 'intermediate', #TODO: add when release operation is added
}

node_label = {
    Operation.BOOL: {True: '$\top$', False: '$\bot$'},
    Operation.PRED: ('${signal} {rop} {threshold}$',
                     {RelOperation.LT: '<',
                      RelOperation.LE: '\leq',
                      RelOperation.GT: '>',
                      RelOperation.GE: '\geq',
                      RelOperation.EQ: '=',
                      RelOperation.NQ: '\neq'}),
    Operation.AND: r'$\land$',
    Operation.OR: r'$\lor$',
    Operation.IMPLIES: r'$\implies$',
    Operation.NOT: r'$\lnot$',
    Operation.ALWAYS: r'$\square_{{[{low}, {high}]}}$',
    Operation.EVENT: r'$\lozenge_{{[{low}, {high}]}}$',
    Operation.UNTIL: r'$\mathcal{{U}}_{{[{low}, {high}]}}$',
    # Operation.RELEASE: r'$\mathcal{{R}}_{{[{low}, {high}]}}$', #TODO: add when release operation is added
}

indent_size = 4

def tikz_tree(ast, depth=1):
    '''Generates latex Tikz tree graph from AST.
    '''
    style=node_styles[ast.op]
    
    if ast.op == Operation.BOOL:
        text = node_label[ast.op][ast.value]
        children = ''
    elif ast.op == Operation.PRED:
        text, rel = node_label[ast.op]
        text = text.format(signal=ast.variable,
                           rop=rel[ast.relation],
                           threshold=ast.threshold)
        children = ''
    elif ast.op in (Operation.AND, Operation.OR):
        text = node_label[ast.op]
        children = '\n'.join(
            template_child.format(node=tikz_tree(ch, depth+1))
                                          for ch in ast.children)
    elif ast.op == Operation.NOT:
        text = node_label[ast.op]
        children = template_child.format(
                        node=tikz_tree(ast.child, depth+1))
    elif ast.op == Operation.IMPLIES:
        text = node_label[ast.op]
        children = '\n'.join(
          (template_child.format(node=tikz_tree(ast.left, depth+1)),
           template_child.format(node=tikz_tree(ast.right, depth+1))))
    elif ast.op in (Operation.ALWAYS, Operation.EVENT):
        text = node_label[ast.op]
        text = text.format(low=ast.low, high=ast.high)
        children = template_child.format(
                        node=tikz_tree(ast.child, depth+1))
    elif ast.op in (Operation.UNTIL,): # Operation.RELEASE):
        text = node_label[ast.op]
        text = text.format(low=ast.low, high=ast.high)
        children = '\n'.join(
          (template_child.format(node=tikz_tree(ast.left, depth+1)),
           template_child.format(node=tikz_tree(ast.right, depth+1))))

    if children:
        indent = ' ' * (indent_size * depth)
        children = indent.join(('\n' + children.lstrip()).splitlines(True))
    
    return template_node.format(style=style, text=text, children=children)

def tikz_node_styles(node_style_options=default_node_styles):
    '''Generates the node style options.
    '''
    styles = set(node_styles.values())
    return template_style_block.format(
        node_styles='\n'.join(node_style_options[s] for s in styles)
    )

def ast2latex(ast, standalone=True, libraries=()):
    '''Generates a latex Tikz figure from an abstract syntax tree.
    '''
    tree = tikz_tree(ast)
    tree = template_tree.format(tree=tree)
    figure = template_figure.format(tree=tree)
    if standalone:
        document = template_latex_standalone
        tikz_libraries = '\n'.join(template_use_tikz_library.format(lib=lib)
                                   for lib in libraries)
        style = tikz_node_styles()
        document = document.format(tikz_libraries=tikz_libraries,
                        tikz_style=style,
                        figure=figure)
    else:
        document = figure
    return document


if __name__ == '__main__':
    from stl import to_ast

    formula = "!(x > 10) && F[0, 2] y > 2 && G[1, 3] z <= 8"
    ast = to_ast(formula)
    print(ast)

    print(ast2latex(ast, libraries=('arrows', 'shapes')))