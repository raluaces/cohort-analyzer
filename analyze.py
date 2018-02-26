#!/usr/bin/env python
from datetime import datetime
from datetime import timedelta
import argparse
import csv

parser = argparse.ArgumentParser(description='Perform customer order cohort analysis.')
parser.add_argument(
    '--customers',
    help='customer csv file path',
    required=True
)
parser.add_argument(
    '--orders',
    help='orders csv file path',
    required=True
)
parser.add_argument(
    '--cohort-length',
    help='cohort lengths in days (default 7 days)',
    default=7
)
parser.add_argument(
    '--cohorts',
    help='number of corhorts to analyze (default 8)',
    default=8
)
parser.add_argument(
    '--bucket-length',
    help='bucket length in days(default 6 days)',
    default=6
)

args = parser.parse_args()
customer_csv_file = args.customers
order_csv_file = args.orders
cohort_length = timedelta(days=args.cohort_length)
number_of_cohorts = args.cohorts
bucket_length = timedelta(days=args.bucket_length)

# set our date format for parsing dates
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# establish our customer dict
customers = {}

# establish our order dict
orders = {}

# Parse our customer csv into customer dict
with open(customer_csv_file, 'r') as csvfile:
    customer_csv = csv.reader(csvfile, delimiter=',')
    for row in customer_csv:
        if row[0] == 'id':
            continue
        customers[row[0]] = {
            'created': datetime.strptime(
                row[1],
                DATE_FORMAT
            )
        }

#  Parse orders into order dict
with open(order_csv_file, 'r') as csvfile:
    order_csv = csv.reader(csvfile, delimiter=',')
    for row in order_csv:
        if row[0] == 'id':
            continue
        orders[row[0]] = {
            'order_number': row[1],
            'user_id': row[2],
            'created': datetime.strptime(
                row[3],
                DATE_FORMAT
            )
        }


# our table printer for giving the user tables
def table_printer(array_of_row_arrays, column_title_list, column_length=16):
    def unify_spaces(value):
        string = str(value)
        chars = len(string)
        if chars < column_length:
            spaces = column_length - chars
            string += ' ' * spaces
        return string
    num_of_columns = len(column_title_list)
    first_row = '|'
    for title in column_title_list:
        first_row += unify_spaces(title) + '|'
    table_row_line = '|'
    for i in range(num_of_columns):
        table_row_line += '-' * column_length
        table_row_line += '|'
    print(table_row_line)
    print(first_row)
    print(table_row_line)
    for row in array_of_row_arrays:
        printable_row = '|'
        for cell in row:
            printable_row += unify_spaces(cell) + '|'
        print(printable_row)
        print(table_row_line)


# get some totals for later
total_orders = len(orders)
total_customers = len(customers)

first_order = orders[min(orders, key=lambda x: orders[x]['created'])]['created']
last_order = orders[max(orders, key=lambda x: orders[x]['created'])]['created']

first_customer = customers[min(customers, key=lambda x: customers[x]['created'])]['created']
last_customer = customers[max(customers, key=lambda x: customers[x]['created'])]['created']

# get the earliest order
# get the elapsed time of the data we have

customer_count = 0

sample_length = (last_customer - first_customer).days
number_of_cohorts_in_data = sample_length / cohort_length.days
print('Analyzing {} customers with {} orders'.format(total_orders, total_customers))
print('There are {}  {} day cohorts in this data'.format(number_of_cohorts_in_data, cohort_length.days))
print('We are analyzing {} cohorts.'.format(number_of_cohorts))

table_rows = []
# Loop through our cohorts of customers
for cohort_count in range(number_of_cohorts):
    cohort_customer_ids = []
    # get our end and start dates for the cohort, if this is second or later run, add a day to start date
    if cohort_count != 0:
        prevent_overlap = 1
    else:
        prevent_overlap = 0
    start_date = first_customer + (cohort_count * cohort_length) + timedelta(days=prevent_overlap)
    end_date = first_customer + (cohort_count * cohort_length) + cohort_length
    cohort_name = start_date.strftime('%m/%d -')
    cohort_name += end_date.strftime(' %m/%d')
    print('cohort # {}     {}'.format(cohort_count, cohort_name))
    print('cohort start date:  {}'.format(start_date))
    print('cohort end date: {}'.format(end_date))
    # get all the customers in this cohort
    for customer_id, customer_data in customers.items():
        if customer_data['created'] < end_date and customer_data['created'] > start_date:
            customer_count += 1
            cohort_customer_ids.append(customer_id)
    # cycle through our order data and find orders relevant to this cohort
    orderers = []
    for order_id, order_data in orders.items():
        if order_data['user_id'] in cohort_customer_ids and order_data['user_id'] not in orderers:
            orderers.append(order_data['user_id'])
    # calculate percent of these customers that are orderers
    orderers_percent = len(orderers) / (len(cohort_customer_ids)/ 100)
    print('{} customers are in this cohort'.format(customer_count))

    column_title_array = ['Cohort', 'Customers']
    # determine how many buckets are in this cohort loop iteration
    number_of_buckets = int(((end_date - first_customer) / bucket_length))
    # loop through each bucket
    for x in range(number_of_buckets):
        if x == 0:
            bucket_start_day = first_customer + (x * bucket_length)
        else:
            bucket_start_day = first_customer + (x * bucket_length) + timedelta(days=x)
        bucket_end_day = bucket_start_day + bucket_length
        bucket_name = '{}-{} days'.format((bucket_start_day - first_customer).days, (bucket_end_day - first_customer).days)
        column_title_array.append(bucket_name)
        number_of_columns = 2 + x
        print(bucket_name)
        # cycle through our order data and find orders relevant to this cohort and bucket
        #orderers = []
        #for order_id, order_data in orders.items():
        #    if order_data['user_id'] in cohort_customer_ids and order_data['user_id'] not in orderers:
        #
        #        orderers.append(order_data['user_id'])
        # calculate percent of these customers that are orderers
        #orderers_percent = len(orderers) / (len(cohort_customer_ids)/ 100)
    # get the % of orderers in this bucket for this cohort
    # get the % of first time orderers from this cohort in this bucket
    print(number_of_columns, column_title_array)


