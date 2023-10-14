import matplotlib.pyplot as plt
class TreeNode:
    def __init__(self, x, left=None, right=None):
        self.val = x
        self.left = left
        self.right = right
        self.root = 'Max'
def parse_expression(expression):
    operators = ['protectedDiv','Max', 'Min', '+', '-', '*', '/', 'max', 'min', 'neg', 'add', 'sub', 'mul', 'div']
    variables = ['NIQ', 'WIQ', 'MRT', 'TTIQ', 'UT', 'DT', 'PT', 'TWT', 'TIS', 'NTR', 'MWT', 'OWT', 'WRK']

    tokens = expression.replace('(', ' ( ').replace(')', ' ) ').split()

    output = []  # 用于后缀表达式tokens
    ops = []  # 用于操作符和括号
    num1=0
    # 这部分是处理中缀表达式并将其转换为后缀表达式
    for token in tokens:
        if token in variables:
            if token in output:
                output.append(token)
                num1+=1
            else:
                output.append(token)
        elif token == '(':
            ops.append(token)
        elif token == ')':
            while ops[-1] != '(':
                output.append(ops.pop())
            ops.pop()  # 删除'('
        elif token in operators:
            while ops and (ops[-1] in operators) and operators.index(ops[-1]) >= operators.index(token):
                output.append(ops.pop())
            ops.append(token)
        else:
            print(f"Unexpected token {token}")

    while ops:
        output.append(ops.pop())
    print(output)
    OutDict={}
    for i in range(len(output)):
        OutDict[i] = output[i]
        output[i] = i
    print(OutDict)
    length=len(output)
    return output,OutDict,length

def create_binary_tree(postfix_tokens,Dict):
    stack = []

    for token in postfix_tokens:
        if Dict[token] not in ['Max', 'Min', '+', '-', '*', '/']:
            stack.append(TreeNode(token))
        else:
            right = stack.pop()
            left = stack.pop()
            stack.append(TreeNode(token, left, right))

    return stack[0]


expression = input()
postfix_tokens,OutDict,length = parse_expression(expression)
root = create_binary_tree(postfix_tokens,OutDict)


import pygraphviz as pgv


def visualize_tree(node,OutDict,length):
    # 初始化一个空的图
    graph = pgv.AGraph(directed=True, strict=True, rankdir='TB')

    # 递归地遍历二叉树并向图中添加节点和边
    def traverse_tree(node, graph):
        if not node:
            return
        graph.add_node(node.val,label=OutDict[node.val])
        if node.left:
            graph.add_node(node.left.val,label=OutDict[node.left.val])
            graph.add_edge(node.val, node.left.val)
            traverse_tree(node.left, graph)
        if node.right:
            graph.add_node(node.right.val,label=OutDict[node.right.val])
            graph.add_edge(node.val, node.right.val)
            traverse_tree(node.right, graph)

    traverse_tree(node, graph)

    # 将图绘制并保存为文件，然后显示它
    graph.layout(prog='dot')
    graph.draw('tree.png', prog='dot', format='png')
    plt.imshow(plt.imread('tree.png'))
    plt.axis('off')


    #*申必的替换操作*

    plt.show()

# 示范如何调用这个函数
visualize_tree(root,OutDict,length)



