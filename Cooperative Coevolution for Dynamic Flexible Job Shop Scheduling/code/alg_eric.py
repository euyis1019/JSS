import operator
import random
import test
import numpy
from deap import gp, creator, tools
from deap.base import Fitness, Toolbox
from deap.gp import PrimitiveSet, PrimitiveTree
from deap import base
from thesis.alg1.alg1 import Alg1
from thesis.alg1.common import get_random_config
from thesis.job_shop_simulator import Instance, Config


def Div(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 1


# 定义评估函数
def eva_ind(individual, context_vector, config, x):
        if x: #routing cvs
            sequencing = toolbox.compile(expr=context_vector)
            routing= toolbox.compile(expr=individual)
            instance = Instance(config, Alg1(routing, sequencing))
            instance.run()  # 用makespantime做fitness
            return instance.now,
        else:
            sequencing = toolbox.compile(expr=individual)
            routing = toolbox.compile(expr=context_vector)
            instance = Instance(config, Alg1(routing, sequencing))
            instance.run()
            return  instance.now,

def ramped_half_and_half(pset, min_depth, max_depth):
    """
    Ramped Half-and-Half initialization method.
    :param pset: Primitive set.
    :param min_depth: Minimum depth of the trees.
    :param max_depth: Maximum depth of the trees.
    :return: A generated tree.
    """
    # Choose a random depth between min_depth and max_depth
    depth = random.randint(min_depth, max_depth)

    if random.random() < 0.5:
        return gp.genFull(pset, min_=depth, max_=depth)
    else:
        return gp.genGrow(pset, min_=min_depth, max_=depth)

# 定义初始化函数
def initialize_population(toolbox, n):
    population = []
    for _ in range(n):
        individual = toolbox.individual()
        population.append(individual)
    return population


# 定义交叉、变异和选择操作
def evolve_population(toolbox, population, n_offspring):
    offspring = []
    for _ in range(n_offspring):
        op_choice = random.random()
        if op_choice < 0.5:  # crossover
            ind1, ind2 = map(toolbox.clone, random.sample(population, 2))
            ind1, ind2 = toolbox.mate(ind1, ind2)
            del ind1.fitness.values
            del ind2.fitness.values
            offspring.append(ind1)
            offspring.append(ind2)
        else:  # mutation
            ind = toolbox.clone(random.choice(population))
            ind, = toolbox.mutate(ind)
            del ind.fitness.values
            offspring.append(ind)
    return offspring


POP_SIZE = 100
N_GEN = 50
N_OFFSPRING = 50

pset = PrimitiveSet("main", 6)
pset.addPrimitive(max, 2)
pset.addPrimitive(min, 2)
pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(Div, 2)
pset.addPrimitive(operator.neg, 1)
pset.renameArguments(ARG0="MWT")
pset.renameArguments(ARG1="PT")
pset.renameArguments(ARG2="OWT")
pset.renameArguments(ARG3="WRK")
pset.renameArguments(ARG4="NOR")
pset.renameArguments(ARG5="TIS")
# 创建类型
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", gp.PrimitiveTree, fitness=creator.FitnessMin)

# 初始化工具箱
toolbox = base.Toolbox()
toolbox.register("expr", ramped_half_and_half, pset=pset, min_depth=3, max_depth=5)
toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.expr)
toolbox.register("population", initialize_population, toolbox, n=POP_SIZE)
toolbox.register("compile", gp.compile, pset=pset)
toolbox.register("evaluate", eva_ind)
toolbox.register("select", tools.selBest)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))

# 初始化种群
Pr = toolbox.population(n=POP_SIZE)
Ps = toolbox.population(n=POP_SIZE)
stats = tools.Statistics(lambda ind: ind.fitness.values)
mstats = tools.MultiStatistics(fitness=stats)
mstats.register("avg", numpy.mean)  # 平均适应度。
mstats.register("std", numpy.std)  # 适应度的标准偏差。
mstats.register("min", numpy.min)  # 最小适应度。
mstats.register("max", numpy.max)  # 最大适应度。
logbook = tools.Logbook()
logbook.header = ['gen', 'nevals', 'avg', 'std', 'min', 'max']
# 初始化上下文向量
cvr = Pr[0]
cvs = Ps[0]
config = get_random_config(100, 5, 10, 10, 1, 10, 0.95)
# 主循环
for gen in range(N_GEN):
    # 评估种群
    for ind in Pr:
        ind.fitness.values = toolbox.evaluate(ind, cvs,config, True)
    for ind in Ps:
        ind.fitness.values = toolbox.evaluate(ind, cvr,config, False)

    # 选择精英个体
    elite_Pr = toolbox.select(Pr, 1)[0]
    elite_Ps = toolbox.select(Ps, 1)[0]

    # 生成后代
    offspring_Pr = evolve_population(toolbox, Pr, N_OFFSPRING)
    offspring_Ps = evolve_population(toolbox, Ps, N_OFFSPRING)

    # 评估后代
    for ind in offspring_Pr:
        ind.fitness.values = toolbox.evaluate(ind, cvs,config, True)
    for ind in offspring_Ps:
        ind.fitness.values = toolbox.evaluate(ind, cvr,config, False)
    # 更新种群
    Pr[:] = offspring_Pr
    Ps[:] = offspring_Ps

    # 更新上下文向量
    if elite_Pr.fitness.values < cvr.fitness.values:
        cvr = elite_Pr
    if elite_Ps.fitness.values < cvs.fitness.values:
        cvs = elite_Ps
    # 记录本代的统计信息
    # 记录本代的统计信息
    record = stats.compile(Pr + Ps) if stats else {}
    logbook.record(gen=gen, nevals=len(Pr) + len(Ps), **record)
    print(logbook.stream)  # 输出本代的统计信息
    print(f"Generation {gen}:")
    print(f"Best Pr: {(elite_Pr)}")
    print(f"Best Ps: {(elite_Ps)}")
    print("gen	nevals	avg    	std    	min   	max ")

# 返回上下文向量
cv = (cvr, cvs)


