##############################################################

#
#                      DOCUMENTACION INTERNA
#
#   Nombre del programa: DES.py
#
#   Fin en Mente: Simulación de un "discrete event simulation" utilizando  SimPy
#
#   Programador: Olivier Viau
#                
# 
#   Lenguaje: Python 3.9.1
# 
#   Recursos: 
#           https://www.youtube.com/watch?v=IlUPJcowBrA
#           ChatGpt3, para la resolución de dudas sobre el yield timeout y el container
#           Recusrsos proporcionados por la UVG
#   Historial de Modificaciones:
# 
#            [000]  27/2/2023 Programa nuevo
# 
##############################################################
import simpy
import random
class DES:
    def __init__(self, env, num,memoria, instruccion, ram):
        self.env = env
        self.num=num
        self.memoria = memoria
        self.instruccion = instruccion
        self.ram = ram
        self.action = env.process(self.procesos(self.env,self.memoria,self.instruccion))

    def procesos(self,env,memoria, instruccion):
        global comproc
        #nuevo proceso
        with ram.get(memoria) as req:
            yield req
            print(f"el proceso {numproc} entro a ready a las {env.now:7.4f} y se le asigno {memoria} en la RAM")
        
        #realizacion de instrucciones
        while instruccion>0:
            i=0
            bo=True
            while i<instruccion and i<3:
                print(f"el proceso {numproc} tiene {instruccion} instrucciones y lleva {env.now:7.4f}")
                # Simular ejecución de instrucciones
                instruccion -= 1
                i+=1
                yield env.timeout(1)
                if instruccion == 0:
                    comproc+=1
                    print(f'{env.now}: Proceso {numproc} a terminado a las {env.now:7.4f}')
                    ram.put(memoria)  # Liberar memoria al finalizar el proceso
                    bo=False
                    break
            if bo:
                bandera = random.randint(1,2)
                if bandera == 1: #entra en espera
                    print(f'El proceso {numproc} entro en')
                    yield env.timeout(1)  # Simula el tiempo de ejecucion en el waiting
                    print(f'El proceso {numproc} termino los procesos I/O')
                elif bandera == 2: #sigue
                    print(f'El proceso {numproc} entro a ready a los {env.now:7.4f}')


def nuevo_proceso(env,interval,nprocesos):
    global comproc
    global numproc
    numproc=0
    for i in range(int(nprocesos)):
        yield env.timeout(interval)
        numproc+=1#sube el numero de procesos que estamos realizando
        memoria=random.randint(1,10)
        instruccion=random.randint(1,10)
        if ram.level>=memoria: #verifica que haya suficiente ram par iniciar el proceso
            print(f"el proceso {numproc} inicio a las {env.now:7.4f}")
            DES(env, f'Proceso_{numproc}', memoria, instruccion, ram)
            yield env.timeout(1)
        else:
            print(f'{env.now}: No hay suficiente memoria RAM disponible para el proceso {numproc}.')

interval=random.expovariate(1/10)
random.seed(100) #random seed to preserve same random number generated
env = simpy.Environment() #crea el ambiente para la simulacion
cpu = simpy.Resource(env, capacity = 3) #Cantidad de procesos en el CPU
ram=simpy.Container(env,init=100,capacity=100) #capacidad de la RAM
comproc = 0 #numero de procesos completados
numproc=0
#corrida del programa
nprocesos=input()
if nprocesos.isnumeric():
    proc=env.process(nuevo_proceso(env,interval,nprocesos))
    env.run(until=proc) # corre la simulacion por n procesos
