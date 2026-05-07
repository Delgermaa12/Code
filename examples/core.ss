"===== SALARY SYSTEM =====" .

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

"Gross salary:" .
"gross_salary" load .

"Social insurance:" .
"social_insurance" load .

"Income tax:" .
"income_tax" load .

"Penalty:" .
"penalty" load .

"Net salary:" .
"net_salary" load .

"penalty" load
0
>
{ "Penalty applied" . }
{ "No penalty" . }
if

"===== END =====" .