import random
import time
from collections import deque

from contiki import broadcast, clock_time, process, packetbuf, rimeaddr, etimer

SEND_INTERVAL = 20 * clock_time.CLOCK_SECOND
TIMESTAMP_CACHE_SIZE = 16

broadcast_conn = broadcast.broadcast
last_timestamp = 0
timestamp_cache = deque([0] * TIMESTAMP_CACHE_SIZE, maxlen=TIMESTAMP_CACHE_SIZE)

def broadcast_recv(c, from_addr):
    global last_timestamp
    received_timestamp = packetbuf.decode(packetbuf.data())
    cache_index = -1

    # Check if the received timestamp is already in the cache
    for i, timestamp in enumerate(timestamp_cache):
        if timestamp == received_timestamp:
            cache_index = i
            break

    if cache_index == -1:
        # New timestamp, add it to the cache
        oldest_timestamp = float("inf")
        for i, timestamp in enumerate(timestamp_cache):
            if timestamp < oldest_timestamp:
                oldest_timestamp = timestamp
                cache_index = i
        timestamp_cache[cache_index] = received_timestamp

        print(f"Broadcast received from {from_addr.u8[0]}.{from_addr.u8[1]}: '{packetbuf.decode(packetbuf.data()[8:])}'")
        packetbuf.clear()
        packetbuf.encode(received_timestamp)
        broadcast.send(broadcast_conn)
        last_timestamp = clock_time.now()

process.pingpong = process.Process("Ping Pong Process")

def pingpong_thread():
    global last_timestamp
    broadcast.open(broadcast_conn, 129, broadcast_recv)
    et = etimer.ETimer()

    while True:
        et.set(20 * clock_time.CLOCK_SECOND)
        yield etimer.ETimer.wait_for_expired(et)

        last_timestamp = clock_time.now()
        packetbuf.clear()
        packetbuf.encode(last_timestamp)
        packetbuf.encode("Pong")
        broadcast.send(broadcast_conn)
        print("Ping")

process.pingpong.set_autostart(True)
process.pingpong.stack_size = 512
process.pingpong.start(pingpong_thread)
