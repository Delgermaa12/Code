"===== SALARY CALCULATION SYSTEM =====" .

"employee_name" input
"worked_hours" input
"hourly_rate" input
"penalty" input

"worked_hours" load
"hourly_rate" load
*
"gross_salary" store

"gross_salary" load
0.115
*
"social_insurance" store

"gross_salary" load
"social_insurance" load
-
"salary_after_social" store

"salary_after_social" load
0.10
*
"income_tax" store

"salary_after_social" load
"income_tax" load
-
"penalty" load
-
"net_salary" store

"===== RESULT =====" .
"Employee:" .
"employee_name" load .

"Gross salary:" .
"gross_salary" load .

"Social insurance 11.5%:" .
"social_insurance" load .

"Income tax 10%:" .
"income_tax" load .

"Penalty:" .
"penalty" load .

"Net salary:" .
"net_salary" load .