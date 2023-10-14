import simpy
class School:
    def __init__(self, env):
        self.env = env
        self.class_end = env.event()
        # 创建三个pupil进程和一个bell进程
        env.process(self.bell())

        [env.process(self.pupil(i)) for i in range(3)]

    def bell(self):
        print('bell')
        for i in range(3): # （1）bell循环
            yield self.env.timeout(45)  # （2）等待45
            print(env.now)
            self.class_end.succeed()  # （3）触发class_end标记成功
            self.class_end = self.env.event()  # （4）生成新的class_end事件
    def pupil(self, k):
        print(f'pupil{k} ', end='be added ')
        for i in range(5):# （5）pupil循环
            print(f'proccess{k} of{i}', end=' ')# （6）输出\0/
            yield self.class_end  #（7）中断处理class_end事件



env = simpy.Environment()
school = School(env)

env.run()
