from contiki import process, sensors
import random

# Include temperature sensor driver
from dev import sht11_sensor

# Number of values used in averaging process
MAX_VALUES = 4
SUM_INTERVAL = 3  # in seconds

# Declaration of array size
arraySize = [10, 50, 800, 170, 904]

# Variables: the application specific event value
event_data_ready = process.allocate_event()

# digits before decimal point
def d1(f):
    return int(f)

# digits after decimal point
def d2(f):
    return int((f - int(f)) * 1000)

# Implementation of random numbers generation and sum
class RandomNumbersProcess(process.Process):
    def process(self):
        while True:
            for j in range(5):
                n = arraySize[j]  # Setting array size
                arrayRand = [random.randint(0, 20000) for _ in range(n)]  # create an array of random numbers
                randSum = sum(arrayRand)
                
                # Print array size and random elements sum
                print("array size is:", n)
                print("random elements sum is:", randSum)

                # Post an event to the temperature process
                self.post_event(event_data_ready, randSum)

                yield self.await_timer(interval=SUM_INTERVAL)

# Implementation of the first process
class TemperatureProcess(process.Process):
    def process(self):
        count = 0
        average = 0
        valid_measure = 0

        while True:
            # Wait for the timer to expire
            yield self.await_timer(interval=1/CLOCK_SECOND)

            # Get temperature measurement and convert it to degrees
            measure = 0.01 * sht11_sensor.value(sht11_sensor.SHT11_SENSOR_TEMP) - 39.6

            # Sum temperature measurements
            average += measure

            # Count how many temperature measurements we have summed up
            count += 1

            if count == MAX_VALUES:
                # Average the sum and store
                valid_measure = average / MAX_VALUES

                # Reset variables
                average = 0
                count = 0

                # Post an event to the print process
                # and pass a pointer to the last measure as data
                self.post_event(process.print_process.event_data_ready, valid_measure)
                self.post_event(RandomNumbersProcess.event_data_ready, valid_measure)

# Implementation of the second process
class PrintProcess(process.Process):
    def process(self):
        while True:
            # Wait until we get a data_ready event
            event, data = yield self.await_event(process.print_process.event_data_ready)

            # Use 'data' variable to retrieve data and then display it
            print("temperature = {}.{}".format(d1(data), d2(data)))

# We declare the processes
temperature_process = TemperatureProcess()
print_process = PrintProcess()
random_numbers_process = RandomNumbersProcess()

# We require the processes to be started automatically
process.autostart_processes(temperature_process, random_numbers_process, print_process)
