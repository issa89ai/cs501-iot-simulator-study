from contiki import process, etimer
from random import randrange
from time import sleep

# Function to generate a random delay between 2 and 4 seconds
def random_delay():
    return randrange(2, 5)

# Function to print the twinsSmile pattern
def print_twins_smile(smile, count):
    for i in range(count):
        print(smile * (i + 1))  # Printing i twinsSmile

# Implementation of the process
class Process1(process.Process):
    def process(self):
        twins_smile = "(*_*)_(*_*)"
        
        while True:
            # Delay 2-4 seconds
            delay = random_delay()
            sleep(delay)

            for i in range(15):
                print_twins_smile(twins_smile, i + 1)
                delay = random_delay()
                sleep(delay)

# Declare the process
process1 = Process1()

# Autostart the process
process.autostart_processes(process1)
