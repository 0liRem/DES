import simpy

def my_proc(env):
    i=0
    while i<10:
        yield env.timeout(1)
        print("a")
        i+=1
    return 'Monty Python’s Flying Circus'

env = simpy.Environment()
proc = env.process(my_proc(env))
env.run(until=proc)
