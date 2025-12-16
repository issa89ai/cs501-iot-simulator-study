from contiki import process

class HelloWorldProcess(process.Process):
    def __init__(self):
        super().__init__()

    def process(self):
        print("Hello, world")

hello_world_process = HelloWorldProcess()

if __name__ == "__main__":
    hello_world_process.start()
