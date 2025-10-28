# Rahul vs Caleb investment comparison

# Given values
principal = 1100        # dollars
time = 8                # years

# Rahul: 3 3/8% = 3.375%, compounded quarterly
rahul_rate = 3 + 3/8
rahul_rate /= 100
rahul_compounds = 4

rahul_amount = principal * (1 + rahul_rate / rahul_compounds) ** (rahul_compounds * time)

# Caleb: 3 1/4% = 3.25%, compounded daily
caleb_rate = 3 + 1/4
caleb_rate /= 100
caleb_compounds = 365

caleb_amount = principal * (1 + caleb_rate / caleb_compounds) ** (caleb_compounds * time)

# Difference between Rahul and Caleb
difference = rahul_amount - caleb_amount

# Round to nearest dollar
rounded_difference = round(difference)

print(f"After {time} years, Rahul has about ${rounded_difference} more than Caleb.")
