import nltk
from nltk.corpus import words as nltk_words
from nltk.corpus import brown as nltk_brown

# Ensure required NLTK datasets are downloaded
nltk.download('words')
nltk.download('brown')

def print_inline(*args, **kwargs):
    """Prints the arguments on the same line by default, unless specified otherwise."""
    # Set 'end' to an empty string if it is not provided
    if 'end' not in kwargs:
        kwargs['end'] = ''
    # Call the built-in print function with the updated kwargs
    print(*args, **kwargs)

def safe_integer_input(prompt):
    """Requests and validates integer input from the user."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print_inline("\t\tInvalid input. Please enter a valid integer. ")

def update_constraints(constraints, guess, feedback):
    for i, char in enumerate(guess):
        index = ord(char) - ord('a')  # Convert char to index, 'a' -> 0, 'b' -> 1, ..., 'z' -> 25

        if feedback[i] == 1:
            # Set only the ith position to 1, indicating this letter must be at this position
            constraints[index] = [-1]*5  # Assume it's not anywhere else
            constraints[index][i] = 1
        elif feedback[i] == 0:
            # Set the ith position to -1, indicating this letter must not be at this position
            constraints[index][i] = -1
        elif feedback[i] == -1:
            # Set all positions to -1 for this letter, as it's not in the word at all
            if guess.count(char) == 1:
                constraints[index] = [-1]*5
            else:
                constraints[index][i] = -1
    return constraints

# retrieve all words from ``words`` that don't contain ``letter``
def filter_words_by_excluding_letter(words, letter):
    # Normalize the excluded letter to ensure it matches the case of the words
    letter = letter.lower()
    # Filter the list to exclude words containing the specified letter
    words = [word for word in words if letter not in word]
    return words

# retrieve all words from ``words`` that contain ``letter`` at ``positions``
def filter_words_by_positional_constraints(words, letter, positions):
    # Normalize the letter to ensure case consistency
    letter = letter.lower()
    # Iterate over each position and its corresponding constraint
    for i, constraint in enumerate(positions):
        if constraint == 0:
            # Keep only words that contain the letter anywhere
            words = [word for word in words if letter in word]
        elif constraint == -1:
            # Exclude words that have the letter at this position
            words = [word for word in words if word[i] != letter]
        elif constraint == 1:
            # Include only words that have the letter at this position
            words = [word for word in words if word[i] == letter]
    return words

def filter_words(constraints, words):
    # Iterate over all constraints, which are indexed by letter
    for index, constraint in enumerate(constraints):
        letter = chr(index + ord('a'))  # Convert index back to a letter
        
        if constraint == [-1, -1, -1, -1, -1]:
            # If the constraint is to exclude this letter completely
            words = filter_words_by_excluding_letter(words, letter)
        elif constraint != [0, 0, 0, 0, 0]:
            # There are specific positional constraints to apply
            words = filter_words_by_positional_constraints(words, letter, constraint)

    return words

def print_constraints(constraints):
    print("Updated constraints for all letters:")
    for i, constraint in enumerate(constraints):
        if constraint != 5*[0]:
            letter = chr(i + ord('a')).upper()  # Convert index to uppercase letter
            print(f"{letter}: {constraint}")

def find_most_common_words(filtered_words):
    if not filtered_words:
        return ["No valid words found."]

    print_inline("\tHow many of the most probable words would you like to see? ")
    k = safe_integer_input("")
    brown_words = [word.lower() for word in nltk_brown.words()]
    fdist = nltk.FreqDist(brown_words)

    unique_filtered_words = list(set(filtered_words))
    most_common_words = sorted(unique_filtered_words, key=lambda w: fdist[w], reverse=True)[:k]

    return most_common_words if most_common_words else ["No valid words found."]

def find_words_with_most_unique_letters(filtered_words):
    if not filtered_words:
        return ["No valid words found."]
    
    print_inline("\tHow many of the most diverse words (words with most unique letters) would you like to see? ")
    k = safe_integer_input("")
    
    filtered_words = list(set(word.lower() for word in filtered_words))
    brown_words = [word.lower() for word in nltk_brown.words()]
    fdist = nltk.FreqDist(brown_words)

    word_scores = [(word, len(set(word)), fdist[word]) for word in filtered_words]
    word_scores.sort(key=lambda x: (x[1], x[2]), reverse=True)
    most_suitable_words = [word for word, _, _ in word_scores[:k]]
    
    return most_suitable_words if most_suitable_words else ["No valid words found."]

def process_guesses():
    constraints = [[0]*5 for _ in range(26)]
    all_possible_words = [word.lower() for word in nltk_words.words() if len(word) == 5]

    print("\nWelcome to the Wordle Helper!\n")
    print("Please enter your guesses and feedback based on Wordle's color coding:")
    print("  Enter '1' if the letter is green (correct position).")
    print("  Enter '0' if the letter is yellow (wrong position).")
    print("  Enter '-1' if the letter is grey (not in the word).\n")

    while True:
        guess = input("\nEnter your guess (5-letter word): ").lower()
        if len(guess) == 5 and guess.isalpha():
            feedback = []
            for i in range(5):
                response = input(f"\tEnter feedback for letter '{guess[i]}' at position {i+1} (-1, 0, 1): ")
                while response not in ['-1', '0', '1']:
                    print_inline("\t\tInvalid input. Please enter -1, 0, or 1. ")
                    response = input(f"\tEnter feedback for letter '{guess[i]}' at position {i+1} (-1, 0, 1): ")
                feedback.append(int(response))

            constraints = update_constraints(constraints, guess, feedback)
            #print_constraints(constraints)
            
            all_possible_words = filter_words(constraints, all_possible_words)
            print(f"\n\tThere are {len(all_possible_words)} words to search.")

            most_common_words = find_most_common_words(all_possible_words)
            most_unique_words = find_words_with_most_unique_letters(all_possible_words)
            
            print("\tMost probable next guesses based on frequency:", most_common_words)
            print("\tWords with the most unique letters:", most_unique_words)

            continue_response = input("\n\tContinue guessing? (y/n): ").lower()
            while continue_response not in ['y', 'n']:
                print_inline("\t\tInvalid input. Please enter 'y' for yes or 'n' for no. ")
                continue_response = input("Continue guessing? (y/n): ").lower()

            if continue_response == 'n':
                break
        else:
            print_inline("\t\tInvalid input. Please enter a 5-letter word consisting only of letters. ")
    print()

process_guesses()
