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
    type=int,
    default=8
)
parser.add_argument(
    '--bucket-length',
    help='bucket length in days(default 6 days)',
    type=int,
    default=6
)
parser.add_argument(
    '--html-output',
    help='html file to output results table to)'
)

args = parser.parse_args()
customer_csv_file = args.customers
order_csv_file = args.orders
cohort_length = timedelta(days=args.cohort_length)
number_of_cohorts = args.cohorts
bucket_length = timedelta(days=args.bucket_length)
html_output_file = args.html_output


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


if html_output_file:
    html_file = open(html_output_file, 'w')


# our table printer for giving the user tables
def table_printer(array_of_row_arrays, column_title_list, column_length=20):
    # unify spaces for stdout table
    def unify_spaces(value):
        if html_output_file:
            return value
        string = str(value)
        chars = len(string)
        if chars < column_length:
            spaces = column_length - chars
            string += ' ' * spaces
        return string

    # function for logic of printing rows
    def row_printer(row_string, second_row=False):
        if html_output_file:
            html_file.write('<tr>{}<tr>'.format(row_string))
            return
        print(row_string)
        if second_row:
            print(second_row)
        print(table_row_line)

    if html_output_file:
        html_file.write('<html><table>')
        cells = ''
        for title in column_title_array:
            cells += '<th>{}</th>'.format(title)
        row_printer(cells)
        for row in array_of_row_arrays:
            if html_output_file:
                html_row = '<tr>{}</tr>'
            cells = ''
            for cell in row:
                cells += '<td>{}</td>'.format(cell)
            row_printer(html_row.format(cells))
        html_file.write('</table></html>')
        html_file.close()
        return
    else:
        # handle logic for printing a table to cli if wanted
        # get our number of columns
        num_of_columns = len(column_title_list)
        table_row_line = '|'
        # build a line and print the line
        for i in range(num_of_columns):
            table_row_line += '-' * column_length
            table_row_line += '|'
        print(table_row_line)

        first_row = '|'
        for title in column_title_list:
            first_row += unify_spaces(title) + '|'
        row_printer(first_row)
        for row in array_of_row_arrays:
            second_row_bool = False
            printable_row = '|'
            second_row = '|'
            for cell in row:
                if ',' in cell:
                    second_row_bool = True
                    cell = cell.split(',')
                    second_row += unify_spaces(cell[1]) + '|'
                    printable_row += unify_spaces(cell[0]) + '|'
                else:
                    printable_row += unify_spaces(cell) + '|'
                    second_row += unify_spaces(' ') + '|'
            if second_row_bool:
                row_printer(printable_row, second_row)
            else:
                row_printer(printable_row)



# get some totals for later
total_orders = len(orders)
total_customers = len(customers)

first_order = orders[min(orders, key=lambda x: orders[x]['created'])]['created']
last_order = orders[max(orders, key=lambda x: orders[x]['created'])]['created']

# get the start and end dates for our data for laters
first_customer = customers[
    min(
        customers,
        key=lambda x: customers[x]['created']
    )
]['created'].replace(hour=0, minute=0, second=0, microsecond=0)
last_customer = customers[
    max(
        customers,
        key=lambda x: customers[x]['created']
    )
]['created']

# establish counter for customers, will use later for calculations
customer_count = 0

# establish how many cohorts we have to work with in the data sample
sample_length = (last_customer - first_customer).days
number_of_cohorts_in_data = sample_length / cohort_length.days
print('Analyzing {} customers with {} orders'.format(total_orders, total_customers))
print('There are {}  {} day cohorts in this data'.format(number_of_cohorts_in_data, cohort_length.days))
# let the user know how many cohorts from data start we want to analyse
print('We are analyzing {} cohorts.'.format(number_of_cohorts))

# start are array of column titles
column_title_array = ['Cohort', 'Customers']

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
    cohort_name = start_date.strftime('%m/%d-') + end_date.strftime('%m/%d')
    # get all the customers in this cohort
    for customer_id, customer_data in customers.items():
        if customer_data['created'] < end_date and customer_data['created'] > start_date:
            customer_count += 1
            cohort_customer_ids.append(customer_id)


    # prep a table row for this cohort
    row = [cohort_name, '{} customers'.format(customer_count)]

    # determine how many buckets are in this cohort loop iteration
    number_of_buckets = int((((first_customer + number_of_cohorts * cohort_length) - start_date) / bucket_length))

    # loop through each bucket
    for x in range(number_of_buckets):
        #  set our date range for bucket
        if x == 0:
            bucket_start_day = start_date + (x * bucket_length)
        else:
            bucket_start_day = start_date + (x * bucket_length) + timedelta(days=x)
        # handle our bucket titles
        bucket_end_day = bucket_start_day + bucket_length
        bucket_name = '{}-{} days'.format((bucket_start_day - start_date).days, (bucket_end_day - start_date).days)
        if cohort_count == 0:
            column_title_array.append(bucket_name)
        # cycle through our order data and find orders relevant to this cohort and bucket
        orderers_array = []
        orderers = 0
        first_timers = 0
        for order_id, order_data in orders.items():
            if order_data['user_id'] in cohort_customer_ids and order_data['user_id'] not in orderers_array:
                if order_data['created'] > bucket_start_day:
                    if order_data['created'] < bucket_end_day:
                        orderers_array.append(order_data['user_id'])
                        orderers += 1
                        if order_data['order_number'] == "1":
                            first_timers += 1
        percent_orderers = int(orderers * (100 / len(cohort_customer_ids)))
        percent_first_time = int(first_timers * (100 / len(cohort_customer_ids)))
        if html_output_file:
            delim = '<br/>'
        else:
            delim = ','
        row.append('{}% orderers ({}){}{}% 1st time ({})'.format(
            percent_orderers,
            orderers,
            delim,
            percent_first_time,
            first_timers
        ))
    table_rows.append(row)
table_printer(table_rows, column_title_array)
