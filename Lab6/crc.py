import random


def crc_encode(message: str, generator: str) -> str:
    """Encodes the message using the CRC algorithm."""
    k = len(generator) - 1
    binary_message = ''.join(format(ord(c), '07b') for c in message)
    padded_message = binary_message + "0" * k
    remainder = modulo2_division(padded_message, generator)
    return binary_message + remainder

def crc_validate(encoded_message: str, generator: str) -> bool:
    """Validates the encoded message using the CRC algorithm."""
    remainder = modulo2_division(encoded_message, generator)
    return "1" not in remainder

def modulo2_division(dividend: str, divisor: str) -> str:
    """Performs modulo-2 division."""
    dividend = list(dividend)
    divisor_length = len(divisor)
    
    for i in range(len(dividend) - divisor_length + 1):
        if dividend[i] == "1":
            for j in range(divisor_length):
                dividend[i + j] = str(int(dividend[i + j]) ^ int(divisor[j]))
    
    return "".join(dividend[-(divisor_length - 1):])

def introduce_error(data: str, error_rate: float = 0.5) -> str:
    """Introduces random errors into the binary string at a specified error rate."""
    
    
    if random.random() < error_rate:
            
        index_error = random.randint(0, len(data) -1)
        old_data = list(data)
    
        new_value = old_data[index_error] = '1' if data[index_error] == '0' else '0'
        
        old_data[index_error] = new_value
        
        return "".join(old_data)
    
    return data
