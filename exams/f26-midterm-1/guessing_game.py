def guessing_game():
    secret_number = 42
    attempts = 1
    print("Try to guess the secret number between 1 and 100.")
    while True:
        if attempts == 5:
            hint = secret_number % 10
            print("Hint: the last digit is", hint)
        guess = int(input("Enter your guess: "))
        if guess < secret_number:
            print("Too low!")
            attempts += 1
        elif guess > secret_number:
            print("Too high!")
            attempts += 1
        else:
            break
    print("Correct! You guessed it in", attempts, "attempts.")

guessing_game()
