import random, os

W, H = os.get_terminal_size()
chars = "!@#$%^&*()_+-=[]{}|;':\",./<>?\\`~ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

for _ in range(H - 1):
    print(''.join(random.choice(chars) for _ in range(W)))
