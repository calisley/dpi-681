import base64
import random
import openai

encoded_password = b'Z2VuZXJhdGl2ZQ=='
encoded_second_password = b'MiwzLDUsNywxMSwxMywxNywxOSwyMywyOSwzMSwzNyw0MSw0Myw0Nyw1Myw1OSw2MSw2Nyw3MSw3Myw3OSw4Myw4OSw5Nw=='

# Decoding the password at runtime.
secret_password = base64.b64decode(encoded_password).decode('utf-8')

# Decode the encoded primes string and convert it to a list of integers.
second_string = base64.b64decode(encoded_second_password).decode('utf-8')
array_of_second = [int(num) for num in second_string.split(',')]

# Choose a random prime number from the list.
second_pass = random.choice(array_of_second)

# Append the random prime number to the decoded password.
final_password = secret_password + str(second_pass)

print(final_password)
