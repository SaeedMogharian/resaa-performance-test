import math

def find_closest_factors(n):
    # Start with the square root of n and look for factors around it
    sqrt_n = int(math.sqrt(n))
    
    # Iterate downwards from sqrt_n to find the closest factor pair
    for x in range(sqrt_n, 0, -1):
        if n % x == 0:
            y = n // x
            return x, y

# Get the input from the user
n = int(input("Enter a natural number: "))

# Find the closest factors
x, y = find_closest_factors(n)

# Output the result
print(f"The two natural numbers are: x = {x}, y = {y}")
