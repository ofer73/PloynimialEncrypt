import numpy as np
import random
from itertools import cycle
import json

import decimal
decimal.getcontext().prec = 5000



def primes2(n):
    """ Input n>=6, Returns a list of primes, 2 <= p < n """
    n, correction = n-n%6+6, 2-(n%6>1)
    sieve = [True] * (n//3)
    for i in range(1,int(n**0.5)//3+1):
      if sieve[i]:
        k=3*i+1|1
        sieve[      k*k//3      ::2*k] = [False] * ((n//6-k*k//6-1)//k+1)
        sieve[k*(k-2*(i&1)+4)//3::2*k] = [False] * ((n//6-k*(k-2*(i&1)+4)//6-1)//k+1)
    return [2,3] + [3*i+1|1 for i in range(1,n//3-correction) if sieve[i]]



def lagrange_interpool (points, x,prime):
    #points is and array of points (y);
    sum = decimal.Decimal(0)
    for i in range(len(points)):
        yi = points[i]
        def lagrange_form(i):
            formVal = decimal.Decimal(1)
            for j in range(len(points)):
                if j==i:
                    continue
                yj = points[j]
                formVal = (formVal * (decimal.Decimal(x - (j+1)) / decimal.Decimal((i+1) - (j+1))))
            return formVal

        sum = (sum+ (decimal.Decimal(yi) * decimal.Decimal(lagrange_form(i)))%prime) %prime
    return sum



def encrypt_msg(msg,p1FreeCo,p2FreeCo):
    # receive a string msg and two integers , and return the result of performing XOR between msg and both numbers
    cyphered = ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(msg, cycle(str(p1FreeCo))))
    cyphered = ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(cyphered, cycle(str(p2FreeCo))))
    return cyphered

def decrypt_msg(msg,p1FreeCo,p2FreeCo):
    message = ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(msg, cycle(str(p2FreeCo))))
    message = ''.join(chr(ord(c) ^ ord(k)) for c, k in zip(message, cycle(str(p1FreeCo))))
    return message

def p_val (x,p,prime):
    return (sum([(p[i]*(x**i)%prime)%prime for i in range(0,len(p))]))%prime

def mix_list(list, perm):
    # func recieves a list and a dictionary perm , and mixes the list according to the dictionary
    temp = list.copy()
    for key in perm.keys():
        list[int(key) -1 ] = temp[int(perm[key]) -1]

def restore_list(list,perm):
    # func recieves a mixed list and a dictionary perm , and restores the list according to the dictionary
    temp = list.copy()
    for key in perm.keys():
        list[int(perm[key]) - 1] = temp[int(key)-1]

def Alice(N):
    q1 = input("insert top range for prime number p (random numbers will be within Fp )") #all polynom coefficients will be randon within a field of some primary number q
    primes = primes2(int(q1)) #get a list of all primes <= q1
    prime = random.choice(primes)  #randomly choose a prime from primes list
    p1 = [random.randrange(0,prime)  for i in range(0,int(N/2))] #first polynom
    p2 = [random.randrange(0,prime)  for i in range(0,N - int(N/2))] #second polynom
    msg = input("insert msg to be encrypted")
    encrypted = encrypt_msg(msg,p1[0],p2[0]) #encrypt the msg using XOR with both free co-efficients
    with open('perm.json') as f:
        permutaion = json.load(f)   # read agreed secret permutaion from shared json file
    list = [p_val(i, p1,prime) for i in range(1,(int(N/2))+2)] + [p_val(i,p2,prime) for i in range(1,int( N-int(N / 2))+2)]
        # create list of p1(x) vals  followed by p2(x) vals for x=1,2,... n/2 +2 (for each poylnom (len(pi)+1) points)
    mix_list(list,permutaion) # perform permutation on list before sending
    print(f"ALICE: enrypted msg is {encrypted}")
    Bob(list,N,encrypted,prime) #bob recieves the mixed list and encrypted msg


def Bob(mixed_list,N,encrypted_msg,prime):
    with open('perm.json') as f:
        permutaion = json.load(f)   # read agreed secret permutaion from shared json file
    restore_list(mixed_list,permutaion) # restore order of polynom values according to agreed permutation
    p1 = mixed_list[:int(N/2)+1]
    p2 = mixed_list[int(N/2)+1:]
    free_1 = round(lagrange_interpool(p1,0,prime))%prime #restore free coefficient of first polynom by largrange's interpool
    free_2 = round(lagrange_interpool(p2,0,prime))%prime#restore free coefficient of second polynom by largrange's interpool
    msg = decrypt_msg(encrypted_msg,free_1,free_2) #bob decrypts the msg by performing XOR again with both free co-efficients
    print(f"BOB: decrypted msg is {msg}")


if __name__ == "__main__":
    N = int(input("enter N (size of both random polynom's combined) ")) #enter N for the size of both random polynoms combined
    perm = np.random.permutation(N+2) # get a random permutation which will be known to both alice and bob
    dict= {i+1:str(perm[i]+1) for i in range(0,N+2)} # create a dictionary representing the permutation which will be written to a JSON file

    json_object = json.dumps(dict, indent=4)

    # Writing to sample.json
    with open("perm.json", "w") as outfile:
        outfile.write(json_object)
    Alice(N) #activate Alice