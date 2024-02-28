import simpy
import random

class Proceso:
    def __init__(self, env, nombre, memoria, instrucciones, ram):
        self.env = env
        self.nombre = nombre
        self.memoria = memoria
        self.instrucciones = instrucciones
        self.estado = None
        self.ram = ram
        self.action = env.process(self.proceso())

    def proceso(self):
        # Estado new
        with self.ram.get(self.memoria) as req:
            yield req
            self.estado = 'ready'
            print(f'{self.env.now}: Proceso {self.nombre} asignado {self.memoria} MB de memoria RAM.')

        # Estado ready
        while self.instrucciones > 0:
            self.estado = 'running'
            print(f'{self.env.now}: Proceso {self.nombre} corriendo con {self.instrucciones} instrucciones restantes.')

            # Simular ejecución de instrucciones
            yield self.env.timeout(1)  # Supongamos que cada instrucción toma 1 unidad de tiempo
            self.instrucciones -= 1

            if self.instrucciones == 0:
                self.estado = 'terminated'
                print(f'{self.env.now}: Proceso {self.nombre} terminado.')
                self.ram.put(self.memoria)  # Liberar memoria al finalizar el proceso
                break

            # Simular waiting o ready al dejar el CPU
            random_number = random.randint(1, 21)
            if random_number == 1:
                self.estado = 'waiting'
                print(f'{self.env.now}: Proceso {self.nombre} esperando I/O.')
                yield self.env.timeout(1)  # Simulamos operación de I/O
                print(f'{self.env.now}: Proceso {self.nombre} I/O completado.')
                self.estado = 'ready'
            elif random_number == 2:
                self.estado = 'ready'
                print(f'{self.env.now}: Proceso {self.nombre} regresando a ready.')

# Función para generar procesos
def generar_procesos(env, ram):
    for i in range(10):  # Generamos 10 procesos para la demostración
        memoria = random.randint(1, 10)
        instrucciones = random.randint(1, 10)
        if ram.level >= memoria:  # Verificar si hay suficiente memoria RAM disponible
            Proceso(env, f'Proceso_{i}', memoria, instrucciones, ram)
            yield env.timeout(1)  # Esperar un tiempo entre la llegada de cada proceso
        else:
            print(f'{env.now}: No hay suficiente memoria RAM disponible para el proceso {i}.')

# Configuración de la simulación
env = simpy.Environment()
ram = simpy.Container(env, init=100, capacity=100)  # Capacidad total de la RAM

# Ejecutar la simulación
env.process(generar_procesos(env, ram))
env.run(until=20)  # Simulamos 20 unidades de tiempo