import sys

def parse_poly_string(poly_str):
    """Converts a polynomial string (e.g., x4+x2+1) into a GF(2) integer representation."""
    if not poly_str or poly_str.strip() == '0':
        return 0
        
    val = 0
    
    # Clean the input: lowercase, remove all spaces, and remove any '^' symbols
    # This turns both 'x^4' and 'x4' into just 'x4'
    poly_str = poly_str.lower().replace(' ', '').replace('^', '')
    
    # Split the polynomial by the addition operator
    terms = poly_str.split('+')
    
    for term in terms:
        if term == '1':
            val ^= 1
        elif term == 'x':
            val ^= 2
        elif term.startswith('x'):
            try:
                # Extract whatever number immediately follows 'x'
                power = int(term[1:])
                val ^= (1 << power)
            except ValueError:
                print(f"Error parsing term: '{term}'. Make sure the format is xN (e.g., x4)")
                sys.exit(1)
        else:
            print(f"Unrecognized term: '{term}'. Use 1, x, or xN.")
            sys.exit(1)
            
    return val

def degree(poly):
    """Returns the degree of the polynomial (the highest bit position)."""
    return poly.bit_length() - 1

def to_poly_string(val):
    """Converts a GF(2) integer back to a readable polynomial string."""
    if val == 0: 
        return "0"
        
    terms = []
    deg = degree(val)
    
    for i in range(deg, -1, -1):
        if val & (1 << i):
            if i == 0: terms.append("1")
            elif i == 1: terms.append("x")
            else: terms.append(f"x^{i}")
            
    return " + ".join(terms)

def poly_mult(a, b):
    """Multiplies two polynomials in GF(2) using XOR for addition."""
    result = 0
    while b > 0:
        if b & 1:
            result ^= a
        a <<= 1
        b >>= 1
    return result

def poly_divmod(a, b):
    """Divides polynomial 'a' by 'b' in GF(2), returning (quotient, remainder)."""
    if b == 0:
        raise ZeroDivisionError("Cannot divide by a zero polynomial.")
        
    quotient = 0
    deg_b = degree(b)
    
    while degree(a) >= deg_b and a != 0:
        shift = degree(a) - deg_b
        quotient ^= (1 << shift)
        a ^= (b << shift)
        
    return quotient, a

def extended_euclidean_gf2(poly, mod_poly):
    """
    Finds the multiplicative inverse using the Extended Euclidean Algorithm.
    Returns the inverse polynomial integer, or None if no inverse exists.
    """
    t1, t2 = 0, 1
    r1, r2 = mod_poly, poly

    while r2 != 0:
        q, rem = poly_divmod(r1, r2)
        r1, r2 = r2, rem
        
        # new_t = t1 - (q * t2). Subtraction is XOR in GF(2).
        new_t = t1 ^ poly_mult(q, t2)
        t1, t2 = t2, new_t

    # If the greatest common divisor (last non-zero remainder) isn't 1, no inverse exists.
    if r1 != 1:
        return None 
        
    return t1

def main():
    print("=" * 60)
    print(" Polynomial Multiplicative Inverse Calculator (GF(2) Field) ")
    print("=" * 60)
    print("Format instructions:")
    print("- Use 'xN' for powers, 'x' for degree 1, and '1' for constants.")
    print("- Example: x8 + x4 + x3 + x + 1\n")

    try:
        mod_input = input("1. Enter the modulus (irreducible polynomial): ")
        poly_input = input("2. Enter the polynomial to invert: ")
        
        modulus = parse_poly_string(mod_input)
        poly = parse_poly_string(poly_input)
        
        print("\n" + "-" * 30)
        print("Calculating...")
        print(f"Modulus : {to_poly_string(modulus)}  (Binary: {bin(modulus)})")
        print(f"Target  : {to_poly_string(poly)}  (Binary: {bin(poly)})")
        print("-" * 30 + "\n")
        
        inverse = extended_euclidean_gf2(poly, modulus)
        
        if inverse is not None:
            print(">>> MULTIPLICATIVE INVERSE FOUND <<<")
            print(f"Polynomial equation : {to_poly_string(inverse)}")
            print(f"Binary equivalent   : {bin(inverse)}")
            
            # Proof/Verification
            check_mult = poly_mult(poly, inverse)
            _, remainder = poly_divmod(check_mult, modulus)
            
            print(f"\nVerification Check  : (Target * Inverse) mod Modulus = {remainder}")
            if remainder == 1:
                print("Status              : SUCCESS (Mathematically proven)")
        else:
            print(">>> NO INVERSE EXISTS <<<")
            print("The polynomials are not coprime (they share a common factor).")
            
    except KeyboardInterrupt:
        print("\nExiting program.")
        sys.exit(0)

if __name__ == "__main__":
    main()
    