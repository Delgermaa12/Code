# SmartStack жишээ програмууд
# Хэрэглэх: python cli.py run examples/demo.ss

# Жишээ 1: Энгийн арифметик
3 4 + .          # Output: 7
10 dup * .       # Output: 100

# Жишээ 2: Word тодорхойлолт
: square dup * ;
: cube dup dup * * ;
: double 2 * ;

5 square .       # Output: 25
3 cube .         # Output: 27
7 double .       # Output: 14

# Жишээ 3: Named Storage
100 "x" store
"x" load 20 + .  # Output: 120

# Жишээ 4: Нөхцөлт логик
1500 1000 > { "Их байна" } { "Бага байна" } if .

# Жишээ 5: Нэгдсэн жишээ
: square dup * ;
9 square "ans" store "ans" load 10 > { "large" } { "small" } if .            
 # Output: "large"

# Жишээ 6: Map (Phase 2)
[ 10 20 30 ] { 2 * } map .    # Output: [ 20 40 60 ]

# Жишээ 7: Filter (Phase 2)
[ 1 5 10 15 20 ] { 10 > } filter .   # Output: [ 15 20 ]


# Жишээ 8: Word-уудыг давхар ашиглаж томъёо хийх
: square dup * ;
: quad square square ;
: eighth quad double ;

2 quad .                 # Output: 16
3 eighth .               # Output: 24



# Sales analytics pipeline

100 "threshold" store
: high-sale "threshold" load >;
: tax 10 * 100 / ;
: add-tax dup tax + ;
[ 50 120 200 80 300 40 ] { high-sale } filter { add-tax } map .

# Output: [ 132 220 330 ]




# Shopping cart system

: tax 10 * 100 / ;
: total dup tax + ;
[ 100 200 300 ] { total } map .


# Output: [ 110 220 330 ]