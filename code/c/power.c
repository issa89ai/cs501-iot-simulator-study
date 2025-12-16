#include "contiki.h"
#include "net/rime.h"
#include "random.h"

#include "powertrace.h"

#include "dev/button-sensor.h"

#include "dev/leds.h"
#include "dev/sht11-sensor.h"

#include <stdio.h>
/*---------------------------------------------------------------------------*/
PROCESS(process1, "powertrace example");
AUTOSTART_PROCESSES(&process1);
/*---------------------------------------------------------------------------*/
PROCESS_THREAD(process1, ev, data)
{
  static struct etimer et;
  char twinsSmile[] = "(*_*)_(*_*)";
  int i=0, a=0;

  PROCESS_BEGIN();
	

  /* Start powertracing, once every second. */
  powertrace_start(CLOCK_SECOND * 1);
  

  while(1) {
    /* Delay 2-4 seconds */
    etimer_set(&et, CLOCK_SECOND * 4 + random_rand() % (CLOCK_SECOND * 4));

    PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));

    for(i=0;i<15;++i){
	for(a=1;a<i+1;++a){
	  printf("%s", twinsSmile); //Printing i twinsSmile	
	}
	printf("\n");
	PROCESS_WAIT_EVENT_UNTIL(etimer_expired(&et));
    }

  }

  PROCESS_END();
}
/*---------------------------------------------------------------------------*/
