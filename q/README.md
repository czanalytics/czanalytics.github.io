# q 

Quantum optimization for logistics.

Using the cutting edge classical optimization as reference, we look into ways to solve pickup and delivery problems with quantum alqorithms.

Requirements: git and Docker desktop installed.

Installation steps:

1. Fetch code:
- $ git clone https://github.com/czanalytics/czanalytics.github.io
- $ cd czanalytics.github.io/q

2. Create the app image:
   - $ docker build -t q . -f Dockerfile.q

3. Launch the API server:
   - $ docker run -d -p 6666:6666 --name qapi q
