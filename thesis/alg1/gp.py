import operator
import random

import numpy
from deap import gp, creator, tools
from deap.base import Fitness, Toolbox
from deap.gp import PrimitiveSet, PrimitiveTree

from thesis.alg1.alg1 import Alg1
from thesis.alg1.common import get_random_config
from thesis.job_shop_simulator import Instance, Config

def protectedDiv(left, right):
    try:
        return left / right
    except ZeroDivisionError:
        return 1


class Individual:
    def __init__(self, routing, sequencing):
        self.routing = PrimitiveTree(routing)
        self.sequencing = PrimitiveTree(sequencing)

    @staticmethod
    def generator():
        return creator.Individual(toolbox.express(), toolbox.express())


class Population:
    def __init__(self, upper_pop, down_pops):
        self.upper_pop = upper_pop
        self.down_pops = down_pops

    @classmethod
    def generator(cls, u_pop, d_num, d_pop):
        return cls(toolbox.sub_population(u_pop), [toolbox.sub_population(d_pop) for _ in range(d_num)])


# define individual
creator.create("FitnessMin", Fitness, weights=(-1.0,))
creator.create("Individual", Individual, fitness=creator.FitnessMin)#注册个体长什么样
# generate primitive set
pset = PrimitiveSet("main", 6)
pset.addPrimitive(max, 2)
pset.addPrimitive(min, 2)
pset.addPrimitive(operator.add, 2)
pset.addPrimitive(operator.sub, 2)
pset.addPrimitive(operator.mul, 2)
pset.addPrimitive(protectedDiv, 2)
pset.addPrimitive(operator.neg, 1)
pset.renameArguments(ARG0="MWT")
pset.renameArguments(ARG1="PT")
pset.renameArguments(ARG2="OWT")
pset.renameArguments(ARG3="WRK")
pset.renameArguments(ARG4="NOR")
pset.renameArguments(ARG5="TIS")


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
# define func
toolbox = Toolbox()
toolbox.register("express", ramped_half_and_half, pset=pset, min_depth=3, max_depth=5)
#toolbox.register("express", gp.genHalfAndHalf, pset=pset, min_=3, max_=5)#定义初始化

toolbox.register("individual", Individual.generator)
toolbox.register("sub_population", tools.initRepeat, list, toolbox.individual)#用一个容器（这里是list）承载
toolbox.register("population", Population.generator)
toolbox.register("compile", gp.compile, pset=pset)


# define program
def eval_ind(individual, config):
    routing = toolbox.compile(expr=individual.routing)#这里张啥用
    sequencing = toolbox.compile(expr=individual.sequencing)
    instance = Instance(config, Alg1(routing, sequencing))
    instance.run()#用makespantime做fitness
    return instance.now,


def up(population: Population, u_num, config):
    for d_pop in population.down_pops:
        d_pop.sort(key=lambda ind: ind.fitness, reverse=True)
        up_inds, d_pop[:] = [toolbox.clone(ind) for ind in d_pop[:u_num]], d_pop[u_num:]
        fitnesses = toolbox.map(lambda ind: toolbox.evaluate(ind, config), up_inds)
        for ind, fit in zip(up_inds, fitnesses):
            ind.fitness.values = fit
        population.upper_pop.extend(up_inds)


def down(population: Population, d_num, configs):
    population.upper_pop.sort(key=lambda ind: ind.fitness)
    down_ind_num = len(population.down_pops) * d_num
    down_inds, population.upper_pop[:] = ([toolbox.clone(ind) for ind in population.upper_pop[:down_ind_num]],
                                          population.upper_pop[down_ind_num:])
    random.shuffle(down_inds)
    down_inds = [down_inds[i * d_num:(i + 1) * d_num] for i in range(len(population.down_pops))]
    for inds, config, down_pop in zip(down_inds, configs, population.down_pops):
        fitnesses = toolbox.map(lambda ind: toolbox.evaluate(ind, config), inds)
        for ind, fit in zip(inds, fitnesses):
            ind.fitness.values = fit
        down_pop.extend(inds)


def up_down(population: Population, ud_num, configs):
    toolbox.up(population, ud_num, configs[0])
    toolbox.down(population, ud_num, configs[1:])
    random.shuffle(population.upper_pop)


toolbox.register("evaluate", eval_ind)
toolbox.register("select", tools.selTournament, tournsize=3)
toolbox.register("mate", gp.cxOnePoint)
toolbox.register("expr_mut", gp.genFull, min_=0, max_=2)
toolbox.register("mutate", gp.mutUniform, expr=toolbox.expr_mut, pset=pset)
toolbox.register("up", up)
toolbox.register("down", down)
toolbox.register("up_down", up_down)

toolbox.decorate("mate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))
toolbox.decorate("mutate", gp.staticLimit(key=operator.attrgetter("height"), max_value=17))


def get_configs(split_num) -> list[Config]:
    config = get_random_config(100, 5, 10, 10, 1, 10, 0.95)
    return [config] + split_config(config, split_num)


def split_config(config: Config, num) -> list[Config]:
    job_num = len(config.jobs)
    sub_jobs = job_num // num
    job_ids = list(config.jobs)
    return [config.sub_config(job_ids[job_pos:job_pos + sub_jobs])
            for job_pos in range(0, sub_jobs * num, sub_jobs)]


# test
def main():
    # 设置随机数生成器的种子以确保结果的可重复性。
    random.seed(42)

    # 定义遗传算法的常量。
    SUBUP = 20  # 上层个体的大小。
    SUBDN = 5  # 下层种群的数量。
    SUBDP = 50  # 下层每个个体的大小。
    UDNUM = 5  # 在上下操作中移动的个体数量。

    # 使用定义的工具箱生成初始种群。
    pop = toolbox.population(u_pop=SUBUP, d_num=SUBDN, d_pop=SUBDP)

    # 初始化名人堂，以跟踪找到的最佳个体。
    hof = tools.HallOfFame(1)

    # 为问题实例生成配置。分成了5个子配置，每个子配置100个个体。为什么是100个？
    configs = get_configs(SUBDN)

    # 定义进化过程中要记录的统计信息。Statistics对象用于在进化算法的运行过程中收集关于种群的统计信息。
    stats_fit = tools.Statistics(lambda ind: ind.fitness.values)
    mstats = tools.MultiStatistics(fitness=stats_fit)
    mstats.register("avg", numpy.mean)  # 平均适应度。
    mstats.register("std", numpy.std)  # 适应度的标准偏差。
    mstats.register("min", numpy.min)  # 最小适应度。
    mstats.register("max", numpy.max)  # 最大适应度。

    # 运行自定义的进化算法并获取最终种群和日志簿。
    pop, log = my_ea(
        pop, toolbox,
        cxpb=0.5, mutpb=0.1, ngen=5,  # 交叉概率、变异概率和代数。
        configs=configs, ud_num=UDNUM,
        stats=mstats, halloffame=hof,
        verbose=True  # 启用详细日志记录。
    )

    # 返回最终种群、日志簿和名人堂。
    return pop, log, hof


def my_varAnd(population, toolbox, cxpb, mutpb):
    offspring = [toolbox.clone(ind) for ind in population]

    # Apply crossover and mutation on the offspring
    for i in range(1, len(offspring), 2):
        if random.random() < cxpb:
            offspring[i - 1].routing, offspring[i].routing = toolbox.mate(offspring[i - 1].routing,
                                                                          offspring[i].routing)
            offspring[i - 1].sequencing, offspring[i].sequencing = toolbox.mate(offspring[i - 1].sequencing,
                                                                                offspring[i].sequencing)
            del offspring[i - 1].fitness.values, offspring[i].fitness.values

    for i in range(len(offspring)):
        if random.random() < mutpb:
            offspring[i].routing, = toolbox.mutate(offspring[i].routing)
            offspring[i].sequencing, = toolbox.mutate(offspring[i].sequencing)
            del offspring[i].fitness.values

    return offspring


def my_ea(population: Population, toolbox, cxpb, mutpb, ngen, configs, ud_num, stats, halloffame, verbose=False):
    # 创建一个日志簿来记录进化过程中的统计信息。
    logbook = tools.Logbook()
    logbook.header = ['gen', 'nevals'] + (stats.fields if stats else [])

    # 评估所有无效适应度的个体。
    nevals = 0
    for config, pop in zip(configs, [population.upper_pop] + population.down_pops):
        invalid_ind:list = [ind for ind in pop if not ind.fitness.valid]
        nevals += len(invalid_ind)
        fitnesses = toolbox.map(lambda ind: toolbox.evaluate(ind, config), invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

    # 如果提供了名人堂对象，则更新名人堂。
    if halloffame is not None:
        halloffame.update(population.upper_pop)

    # 记录初始种群的统计信息，并在verbose为True时打印它。
    record = stats.compile(population.upper_pop) if stats else {}
    logbook.record(gen=0, nevals=nevals, **record)
    if verbose:
        print(logbook.stream)

    # stopping criteria 具体先跑5代
    for gen in range(1, ngen + 1):
        # 执行上下层操作。
        toolbox.up_down(population, ud_num, configs)
        first = True
        nevals = 0
        for config, pop in zip(configs, [population.upper_pop] + population.down_pops):
            # 对上层和下层种群进行选择操作，但跳过第一个种群（上层种群）。
            if first:
                first = False
            else:
                pop[:] = toolbox.select(pop, len(pop))

            # 应用变异和交叉操作来生成下一代种群。
            pop[:] = my_varAnd(pop, toolbox, cxpb, mutpb)

            # 再次评估所有无效适应度的个体。
            invalid_ind = [ind for ind in pop if not ind.fitness.valid]
            fitnesses = toolbox.map(lambda ind: toolbox.evaluate(ind, config), invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            nevals += len(invalid_ind)

        # 再次更新名人堂。
        if halloffame is not None:
            halloffame.update(population.upper_pop)

        # 记录并可能打印这一代的统计信息。
        record = stats.compile(population.upper_pop) if stats else {}
        logbook.record(gen=gen, nevals=nevals, **record)
        if verbose:
            print(logbook.stream)

    # 返回最终的种群和日志簿。
    return population, logbook


if __name__ == "__main__":
    pop, log, hof = main()
    print(f"fitness of the best: {hof[0].fitness.values}")
