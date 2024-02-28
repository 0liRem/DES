# NOTE: time units interpreted across the notebook are in MINUTES

import simpy
import random

inter_arrival_time = random.expovariate(1/5) #customer arriving in every 5 minutes

processing_time = {
  "till_process": random.uniform(1,3), #till process duration is uniformly distributed from a minute through 3 minutes per customer
  "coffee_process": random.gauss(1,0.5), #coffee making process duration is normally distributed averaging one minute with 0.5 min as standard deviation
  "pizza_process": random.gauss(5,1),
  "dining_in": random.gauss(15,5)
}
def customer_arrival(env, inter_arrival_time):
    global customer
    global customer_served
    customer = 0 #represent the customer ID
    while True: #while the simulation is still in condition to be run
        yield env.timeout(inter_arrival_time)
        customer += 1 #customer ID added
        customer_type = random.choices([1,2,3,4], [0.4,0.3,0.2,0.1])[0]
        print(f"customer {customer} arrives at {env.now:7.4f}")

        next_process = till_activity(env, processing_time, customer, customer_type)
        env.process(next_process) #next process 


def till_activity(env, processing_time, customer, customer_type):
        with staff.request() as till_request: #requesting staff to service at the till
            yield till_request #waiting until the staff available
            yield env.timeout(processing_time["till_process"]) #elapsed time of till activity, staff resource is automatically released after it
            print(f"till complete at {env.now:7.4f} for customer {customer}")

            order_type = random.randint(1,3) #random assignment for customer ordering type
            dining_in = random.randint(0,1) #random assignment for whether customer intend to dine in or take away

            order_coffee = coffee_activity(env, processing_time, customer, customer_type, dining_in)
            order_pizza = pizza_activity(env, processing_time, customer, customer_type, dining_in)
            order_all = coffee_pizza_activity(env, processing_time, customer, customer_type, dining_in)

            if order_type == 1: # if customer order type is only ordering coffee, then proceed to order coffee process
                env.process(order_coffee)
            elif order_type == 2: # same logic with above
                env.process(order_pizza)
            else: env.process(order_all) # if neither only coffee nor only pizza, then they must order both!

def coffee_activity(env, processing_time, customer, customer_type, dining_in):
    global customer_served
    with staff.request() as coffee_request:
        yield coffee_request
        yield env.timeout(processing_time["coffee_process"])
        print(f"order complete at {env.now:7.4f} for customer {customer}")

        dining_process = dining_activity(env, processing_time, customer, customer_type)
        if dining_in == 1:
            env.process(dining_process) #if customer intend to dine in, proceed to dine in process
        else:
            customer_served += 1 #customer is successfully served
            print(f"Customer {customer} leaves at {env.now:7.4f}") #if customer intend to take away, they leave

def pizza_activity(env, processing_time, customer, customer_type, dining_in):
    global customer_served
    with staff.request() as coffee_request:
        yield coffee_request
        yield env.timeout(processing_time["coffee_process"])
        print(f"order complete at {env.now:7.4f} for customer {customer}")

        dining_process = dining_activity(env, processing_time, customer, customer_type)
        if dining_in == 1:
            env.process(dining_process) #if customer intend to dine in, proceed to dine in process
        else:
            customer_served += 1 #customer is successfully served
            print(f"Customer {customer} leaves at {env.now:7.4f}") #if customer intend to take away, they leave

def coffee_pizza_activity(env, processing_time, customer, customer_type, dining_in):
    global customer_served
    with staff.request() as coffee_request:
        yield coffee_request
        yield env.timeout(processing_time["coffee_process"])
        print(f"order complete at {env.now:7.4f} for customer {customer}")

        dining_process = dining_activity(env, processing_time, customer, customer_type)
        if dining_in == 1:
            env.process(dining_process) #if customer intend to dine in, proceed to dine in process
        else:
            customer_served += 1 #customer is successfully served
            print(f"Customer {customer} leaves at {env.now:7.4f}") #if customer intend to take away, they leave

def dining_activity(env, processing_time, customer, customer_type):
    global customer_served
    if customer_type <= 2:
        with two_seater.request() as twoseater_request:
            decision = yield twoseater_request | env.timeout(10/60) # the decision is whether there is available two seater or not

        if twoseater_request in decision:
            yield env.timeout(processing_time["dining_in"]) # customer found two seater and dining in
            customer_served += 1
            print(f"Dining in complete at {env.now:7.4f} for customer {customer}")
            print(f"Customer {customer} leaves at {env.now:7.4f}")
        else:
            print(f"Customer {customer} leaves at {env.now:7.4f}") # after 10 seconds check, customer found no seat available, hence take away
            customer_served += 1

    else:
        with four_seater.request() as fourseater_request:
            decision = yield fourseater_request | env.timeout(2) # same exact scenario for group of three or four looking for four seater

        if fourseater_request in decision:
            yield env.timeout(processing_time["dining_in"])
            print(f"Dining in complete at {env.now:7.4f} for customer {customer}")
            print(f"Customer {customer} leaves at {env.now:7.4f}")
            customer_served += 1
        else:
            print(f"Customer {customer} leaves at {env.now:7.4f}")
            customer_served += 1


random.seed(100) #random seed to preserve same random number generated

env = simpy.Environment() #create the essential simpy environment

staff = simpy.Resource(env, capacity = 2) #staff
two_seater = simpy.Resource(env, capacity = 4) #two seater for one or couple customer
four_seater = simpy.Resource(env, capacity = 1) #four seater for three or four group of customer

customer = 0 #set the initial customer id starting from 0
customer_served = 0 #number of customer served during the start of simulation is zero
env.process(customer_arrival(env, inter_arrival_time))


env.run(until=60*4) # run the simulation for 3 hours
print('\n')
print(f"TOTAL COMPLETE CUSTOMER:{customer_served}")
print(f"Customer in System:{customer - customer_served}")