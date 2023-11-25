# pipe-client-server-communication
* The Airline Reservation System is a client-server application implemented in Python utilizing socket communication for interaction. 

* The server uses a mutex (lock) to ensure mutual exclusion when processing reservation and cancellation requests, preventing conflicts between multiple clients.

* The server manages flight details, transaction history, and invoices, storing data in text files. 
* The client allows agencies to perform actions like consulting flights, viewing transaction history, and checking invoices. Communication is established through a simple protocol, with the client sending requests specifying actions and parameters, and the server responding accordingly. The server employs a mutex for mutual exclusion during reservation and cancellation processes to prevent conflicts. 
* The system demonstrates a basic distributed application, providing a command-line interface for user interaction.