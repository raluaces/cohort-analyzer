**Cohort analyser**

This script is made to make customer cohorts of varying lengths and sample their order behavior.
It will determine the percent of orders placed in windows of varying size from customer signup.
As well as the percent of those orders which are first time orders.


To run this script 2 csv files are expected as arguments.  
CSV Format for customers  
customer_id,created_date

CSV Format for orders  
id,order_number,user_id,created


Simple execution of this script would be as follows:
```
./analyze.py --customers customers.csv --orders orders.csv
```  

Sample Execution of the script with increased cohorts plus html output
```aidl
./analyze.py --customers customers.csv --orders orders.csv --cohorts 10 --html-output output.html
```
  
Sample help output from script:
```
$ ./analyze.py -h
usage: analyze.py [-h] --customers CUSTOMERS --orders ORDERS
                  [--cohort-length COHORT_LENGTH] [--cohorts COHORTS]
                  [--bucket-length BUCKET_LENGTH] [--html-output HTML_OUTPUT]

Perform customer order cohort analysis.

optional arguments:
  -h, --help            show this help message and exit
  --customers CUSTOMERS
                        customer csv file path
  --orders ORDERS       orders csv file path
  --cohort-length COHORT_LENGTH
                        cohort lengths in days (default 7 days)
  --cohorts COHORTS     number of corhorts to analyze (default 8)
  --bucket-length BUCKET_LENGTH
                        bucket length in days(default 6 days)
  --html-output HTML_OUTPUT
                        html file to output results table to)

```
