/* temperature.csc */

#include "contiki.h"
#include <stdio.h>
#include "lib/random.h"
#include <stdlib.h>

#include "dev/sht11-sensor.h"

#define MAX_VALUES 4
#define SUM_INTERVAL (3 * CLOCK_SECOND)

static int arraySize[5] = {10, 50, 800, 170, 904};

static process_event_t event_data_ready;

unsigned short d1(float f)
{
  return((unsigned short)f);
}

unsigned short d2(float f)
{
  return(1000*(f-d1(f)));
}

PROCESS(temp_process, "Temperature process");
PROCESS(print_process, "Print process");
PROCESS(randomNumbers_process, "Inserting Random Numbers in an array");

AUTOSTART_PROCESSES(&temp_process, &randomNumbers_process, &print_process);

PROCESS_THREAD(randomNumbers_process, ev, data) {
    static struct etimer timer;
    static int i = 0, j = 0, randSum = 0, n = 0;

    PROCESS_BEGIN();

    i = 0;
    j = 0;
    randSum = 0;
    n = 0;

    etimer_set(&timer, SUM_INTERVAL);
    while (1) {
        for (j = 0; j < 5; j++) {
            PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&timer));

            n = arraySize[j];
            int arrayRand[n];

            for (i = 0; i < n; i++) {
                arrayRand[i] = random_rand() % 20000;
                randSum += arrayRand[i];
            }

            process_post(&temp_process, ev, data);
            etimer_reset(&timer);

            printf("array size is: %d \n", n);
            printf("random elements sum is: %d \n\n", randSum);
        }
    }

    PROCESS_END();
}

PROCESS_THREAD(temp_process, ev, data) {
    static struct etimer timer;
    static int count = 0;
    static float average = 0, valid_measure = 0;
    float measure;

    PROCESS_BEGIN();

    event_data_ready = process_alloc_event();
    SENSORS_ACTIVATE(sht11_sensor);

    count = 0;
    average = 0;
    valid_measure = 0;
    measure = 0;

    etimer_set(&timer, CLOCK_CONF_SECOND / 4);

    while (1) {
        PROCESS_WAIT_EVENT_UNTIL(ev == PROCESS_EVENT_TIMER);

        measure = 0.01 * sht11_sensor.value(SHT11_SENSOR_TEMP) - 39.6;
        average += measure;
        count++;

        if (count == MAX_VALUES) {
            valid_measure = average / MAX_VALUES;
            average = 0;
            count = 0;

            process_post(&print_process, event_data_ready, &valid_measure);
            process_post(&randomNumbers_process, event_data_ready, &valid_measure);
        }

        etimer_reset(&timer);
    }

    PROCESS_END();
}

PROCESS_THREAD(print_process, ev, data) {
    PROCESS_BEGIN();

    while (1) {
        PROCESS_WAIT_EVENT_UNTIL(ev == event_data_ready);
        printf("temperature = %u.%u\n", d1(*(float *)data), d2(*(float *)data));
    }

    PROCESS_END();
}
