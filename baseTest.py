def decimalToAlphabeticLabel(n):
    if n == 0:
        return "0"
    
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    result = []
    
    while n > 0:
        n, remainder = divmod(n, 26)
        result.append(alphabet[remainder])
    
    return ''.join(reversed(result))

# Example usage
number = 703
base = 26
converted_number = decimalToAlphabeticLabel(number)
print(f"Number {number} in base 26 is {converted_number}")
