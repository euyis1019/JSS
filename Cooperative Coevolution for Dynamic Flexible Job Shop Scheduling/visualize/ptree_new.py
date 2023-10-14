import matplotlib.pyplot as plt
import pygraphviz as pgv

class TreeNode:
    def __init__(self, x, left=None, right=None):
        self.val = x
        self.left = left
        self.right = right

def parse_expression(expression):
    operators = ['max', 'min', '+', '-', '*', 'protectedDiv', 'neg']
    variables = ['MWT', 'PT', 'OWT', 'WRK', 'NOR', 'TIS']

    tokens = expression.replace('(', ' ( ').replace(')', ' ) ').split()

    output = []
    ops = []

    for token in tokens:
        if token in variables:
            output.append(token)
        elif token == '(':
            ops.append(token)
        elif token == ')':
            while ops[-1] != '(':
                output.append(ops.pop())
            ops.pop()
        elif token in operators:
            while ops and (ops[-1] in operators) and operators.index(ops[-1]) >= operators.index(token):
                output.append(ops.pop())
            ops.append(token)
        else:
            print(f"Unexpected token {token}")

    while ops:
        output.append(ops.pop())

    OutDict = {}
    for i in range(len(output)):
        OutDict[i] = output[i]
        output[i] = i

    return output, OutDict, len(output)

def create_binary_tree(postfix_tokens, Dict):
    stack = []

    for token in postfix_tokens:
        if Dict[token] not in ['max', 'min', '+', '-', '*', 'protectedDiv', 'neg']:
            stack.append(TreeNode(token))
        else:
            if Dict[token] == 'neg':  # Handling unary operator
                operand = stack.pop()
                stack.append(TreeNode(token, operand))
            else:  # Handling binary operators
                right = stack.pop()
                left = stack.pop()
                stack.append(TreeNode(token, left, right))

    return stack[0]

def visualize_tree(node, OutDict, length):
    graph = pgv.AGraph(directed=True, strict=True, rankdir='TB')

    def traverse_tree(node, graph):
        if not node:
            return
        graph.add_node(node.val, label=OutDict[node.val])
        if node.left:
            graph.add_node(node.left.val, label=OutDict[node.left.val])
            graph.add_edge(node.val, node.left.val)
            traverse_tree(node.left, graph)
        if node.right:
            graph.add_node(node.right.val, label=OutDict[node.right.val])
            graph.add_edge(node.val, node.right.val)
            traverse_tree(node.right, graph)

    traverse_tree(node, graph)

    graph.layout(prog='dot')
    graph.draw('tree.png', prog='dot', format='png')
    plt.imshow(plt.imread('tree.png'))
    plt.axis('off')
    plt.show()

def preprocess_expression(expression):
    expression = expression.replace("sub", "-")
    expression = expression.replace("add", "+")
    expression = expression.replace("mul", "*")
    expression = expression.replace("protectedDiv", "/")  # 或者其他你的解析函数能理解的运算符
    return expression



expression = "mul(protectedDiv(mul(add(sub(WRK, MWT), protectedDiv(TIS, add(WRK, mul(OWT, add(max(OWT, OWT), OWT))))), neg(sub(WRK, MWT))), NOR), neg(add(add(sub(WRK, OWT), mul(OWT, TIS)), sub(WRK, MWT))))"
expression = preprocess_expression(expression)
postfix_tokens, OutDict, length = parse_expression(expression)
root = create_binary_tree(postfix_tokens, OutDict)
visualize_tree(root, OutDict, length)
