import streamlit as st

def parse_poly_string(poly_str):
    """Converts a polynomial string (e.g., x4+x2+1) into a GF(2) integer representation."""
    if not poly_str or poly_str.strip() == '0':
        return 0
        
    val = 0
    poly_str = poly_str.lower().replace(' ', '').replace('^', '')
    terms = poly_str.split('+')
    
    for term in terms:
        if term == '1':
            val ^= 1
        elif term == 'x':
            val ^= 2
        elif term.startswith('x'):
            try:
                power = int(term[1:])
                val ^= (1 << power)
            except ValueError:
                raise ValueError(f"Error parsing term: '{term}'. Make sure the format is xN (e.g., x4)")
        else:
            raise ValueError(f"Unrecognized term: '{term}'. Use 1, x, or xN.")
            
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
        new_t = t1 ^ poly_mult(q, t2)
        t1, t2 = t2, new_t

    if r1 != 1:
        return None 
        
    return t1

# ==========================================
# Streamlit User Interface
# ==========================================
st.set_page_config(page_title="GF(2) Inverse Calculator", layout="centered")

st.title("Polynomial Multiplicative Inverse Calculator")
st.markdown("**Applied Cryptography — GF(2) Galois Field**")

st.info("💡 **Format Instructions:** Type powers as `xN` or `x^N`. Use `x` for degree 1, and `1` for constants.\n\n*Example:* `x8 + x4 + x3 + x + 1`")

# Input fields 
mod_input = st.text_input("1. Enter the modulus (irreducible polynomial):", value="x8 + x4 + x3 + x + 1")
poly_input = st.text_input("2. Enter the polynomial to invert:", value="x6 + x4 + x + 1")

if st.button("Calculate Inverse", type="primary"):
    if not mod_input or not poly_input:
        st.warning("Please enter both polynomials.")
    else:
        try:
            # Parse inputs
            modulus = parse_poly_string(mod_input)
            poly = parse_poly_string(poly_input)
            
            st.divider()
            st.subheader("Calculation Details")
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Modulus:**")
                st.code(to_poly_string(modulus))
                st.caption(f"Binary: {bin(modulus)}")
                
            with col2:
                st.markdown("**Target Polynomial:**")
                st.code(to_poly_string(poly))
                st.caption(f"Binary: {bin(poly)}")
            
            # Compute inverse
            inverse = extended_euclidean_gf2(poly, modulus)
            
            st.divider()
            if inverse is not None:
                st.success("### >>> Multiplicative Inverse Found <<<")
                
                # Display result prominently
                st.markdown(f"**Polynomial Equation:** `{to_poly_string(inverse)}`")
                st.markdown(f"**Binary Equivalent:** `{bin(inverse)}`")
                
                # Verification
                check_mult = poly_mult(poly, inverse)
                _, remainder = poly_divmod(check_mult, modulus)
                
                with st.expander("Show Mathematical Verification"):
                    st.write("To verify, (Target × Inverse) mod Modulus must equal 1.")
                    st.code(f"Remainder = {remainder}")
                    if remainder == 1:
                        st.write("✅ Verification passed.")
            else:
                st.error("### >>> No Inverse Exists <<<")
                st.write("The polynomials are not coprime (they share a common factor).")
                
        except ValueError as e:
            st.error(str(e))
        except ZeroDivisionError as e:
            st.error(str(e))
            