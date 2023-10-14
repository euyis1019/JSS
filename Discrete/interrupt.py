import simpy
import random
env = simpy.Environment()

class Charge:
    def __init__(self, env):
        self.env = env
        self.drive_proc = env.process(self.drive(env))

    def drive(self, env):
        while True:
            yield env.timeout(random.randint(20, 40))  # 1.骑行20-40min
            print('start parking at:{}mins'.format(env.now))  # 2.停车
            charging = env.process(self.bat_ctrl(env))  # 3.创建充电进程（事件）

            parking = env.timeout(60)  # 4.创建停车事件
            yield charging | parking  # 5.停车结束就可离开
            print("it has finished")
            if not charging.triggered:  # 6.charging还没有结束执行干扰
                charging.interrupt('need to go')
            print('stop parking at:{}'.format(env.now))  # 7.停车结束

    def bat_ctrl(self, env):
        print('bat start at:{}mins'.format(env.now))  # 8.开始充电点
        try:
            yield env.timeout(random.randint(50,70))  # 9.充电60-90min
            print('bat done at:', env.now)  # 10.充电结束
        except simpy.Interrupt as i:
            print('bat interrupt at:', env.now, 'mes', i.cause)  # 11.充电被干扰

ev = Charge(env)
env.run(until=100)
