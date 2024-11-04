prompt = ["""You are an expert cyber security threat intelligence analyst. This is a predicting task. Based on a sequence of  events, predict the attack type  for the 10th event.  There are events from IDS. 
          Each event contains information of timestamp, event description, IP address, host name,  the abbreviation for the event description, event class label.
          we want you to predict the event class label of the 10th events based on the sequences of ten events. The previous 9 events are treated as context information. 
          The event class labels are the following 11 types: 'false positive', 'cracking','dirb','dnsteal','network_scans','privilege_escalation','reverse_shell',
          'service_scans','service_stop','webshell','wpscan'. 
          
          I will give you some examples following format: event 1, event 2, event 3,...,event 10, label of the 10th event. 
           
           """ ]