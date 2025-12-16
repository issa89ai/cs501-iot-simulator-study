/*
 * Broadcast PingPong 
 */
//#include <time.h> // Removed as it's not found or necessary in Contiki environment
#include <stdint.h>
#include "contiki.h"
#include "lib/random.h"
#include "net/rime.h"
#include "etimer.h"
#include <stdio.h>

#define SEND_INTERVAL (20 * CLOCK_SECOND)
#define TIMESTAMP_CACHE_SIZE 16  // Size of the timestamp cache

static struct broadcast_conn broadcast;
static clock_time_t last_timestamp = 0; // Use clock_time_t for Contiki time representation
static clock_time_t timestamp_cache[TIMESTAMP_CACHE_SIZE] = {0}; // Adjusted to clock_time_t

PROCESS(pingpong, "Ping Pong Process");
AUTOSTART_PROCESSES(&pingpong);

static void broadcast_recv(struct broadcast_conn *c, const rimeaddr_t *from) {
    clock_time_t received_timestamp = *((clock_time_t *)packetbuf_dataptr()); // Use clock_time_t
    int i, cache_index = -1;

    // Check if the received timestamp is already in the cache
    for (i=0; i<TIMESTAMP_CACHE_SIZE; i++) {
        if (timestamp_cache[i] == received_timestamp) {
            cache_index = i;
            break;
        }
    }

    if (cache_index == -1) {
        // New timestamp, add it to the cache
        clock_time_t oldest_timestamp = ~0;
        for (i = 0; i < TIMESTAMP_CACHE_SIZE; i++) {
            if (timestamp_cache[i] < oldest_timestamp) {
                oldest_timestamp = timestamp_cache[i];
                cache_index = i;
            }
        }
        timestamp_cache[cache_index] = received_timestamp;

        printf("Broadcast received from %d.%d: '%s'\n",
               from->u8[0], from->u8[1], (char *)&packetbuf_dataptr()[sizeof(clock_time_t)]);
        packetbuf_copyfrom(&received_timestamp, sizeof(clock_time_t));
        broadcast_send(&broadcast);
    }
}

static const struct broadcast_callbacks broadcast_call = {broadcast_recv};

PROCESS_THREAD(pingpong, ev, data) {
    static struct etimer et;

    PROCESS_EXITHANDLER(broadcast_close(&broadcast);)

    PROCESS_BEGIN();

    broadcast_open(&broadcast, 129, &broadcast_call);

    while (1) {
        etimer_set(&et, SEND_INTERVAL);
        PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));

        last_timestamp = clock_time(); // Use clock_time() from Contiki
        packetbuf_copyfrom(&last_timestamp, sizeof(clock_time_t));
        packetbuf_copyfrom("Pong", 5);
        broadcast_send(&broadcast);
        printf("Ping\n");
    }

    PROCESS_END();
}

