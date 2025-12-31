from app.database.db import SessionLocal
from app.models.guessing_game import CharacterGuessingGame


def play_game_simulation():
    db = SessionLocal()
    game = CharacterGuessingGame(db)

    print("\n" + "="*60)
    print("CHARACTER GUESSING GAME - SIMULATION")
    print("="*60)
    print("\nLet's pretend you're thinking of: NARUTO UZUMAKI")
    print("The game will ask questions and try to guess...\n")

    # Start game
    response = game.start_game()
    session_id = response['session_id']
    candidate_ids = None  # Will be set after first answer

    # Answer path for Naruto:
    # Q1: anime or actor? -> anime
    # Q2: gender? -> male
    # Q3: hero/villain? -> hero
    # Q4: trait? -> determined
    # Q5: genre? -> action

    answers = [
        ('anime', 'Naruto is from anime'),
        ('male', 'Naruto is male'),
        ('hero', 'Naruto is a hero'),
        ('determined', 'Naruto is very determined'),
        ('action', 'Naruto is action genre')
    ]

    question_num = 1

    for answer, reason in answers:
        print(f"\nQuestion {question_num}: {response['question']}")
        print(f"Options: {response['options']}")
        print(f"[USER ANSWER]: {answer} ({reason})")

        if response['status'] == 'guess':
            break

        # Get all candidates for first question
        if candidate_ids is None:
            # First question - get all character IDs
            all_chars = db.query(game.db.query(game.db).count())
            from app.database.models import Character
            all_characters = db.query(Character).all()
            candidate_ids = [c.id for c in all_characters]

        # Answer the question
        response = game.answer_question(
            session_id=session_id,
            question_number=question_num,
            answer=answer,
            candidate_ids=candidate_ids
        )

        if response['status'] == 'continue':
            candidate_ids = response['candidate_ids']
            print(f"[SYSTEM]: {response['remaining_candidates']} candidates remaining")
            question_num = response['question_number']
        else:
            # Game is making a guess
            break

    # Display final guess
    print("\n" + "="*60)
    print("FINAL GUESS")
    print("="*60 + "\n")

    if response['status'] == 'guess':
        print(f"After {response['total_questions']} questions, I think you're thinking of:\n")

        for i, guess in enumerate(response['guesses'], 1):
            print(f"{i}. {guess['name']} ({guess['type']})")
            print(f"   From: {guess['source']}")
            print(f"   Confidence: {guess['confidence']}%")
            print()

        # Check if correct
        if response['guesses'][0]['name'] == 'Naruto Uzumaki':
            print("[SUCCESS] Correct guess! The game works!")
        else:
            print(f"[INFO] Top guess was {response['guesses'][0]['name']}")
            print("[INFO] This might happen if multiple characters match the criteria")

    db.close()


def test_all_characters():
    from app.database.models import Character
    db = SessionLocal()

    characters = db.query(Character).order_by(Character.type, Character.name).all()

    print("\n" + "="*60)
    print("ALL CHARACTERS IN DATABASE")
    print("="*60 + "\n")

    print("ACTORS:")
    for char in characters:
        if char.type == 'actor':
            print(f"  - {char.name} ({char.source})")
            print(f"    Traits: {', '.join(char.traits)}")
            print(f"    Genres: {', '.join(char.genres)}")
            print()

    print("\nANIME CHARACTERS:")
    for char in characters:
        if char.type == 'anime':
            alignment = f" [{char.alignment}]" if char.alignment else ""
            print(f"  - {char.name}{alignment} ({char.source})")
            print(f"    Traits: {', '.join(char.traits)}")
            print(f"    Genres: {', '.join(char.genres)}")
            print()

    print(f"Total characters: {len(characters)}")

    db.close()


def interactive_game():
    db = SessionLocal()
    game = CharacterGuessingGame(db)

    print("\n" + "="*60)
    print("CHARACTER GUESSING GAME - INTERACTIVE MODE")
    print("="*60)
    print("\nThink of a character (actor or anime character) and I'll try to guess!")
    print("Answer the questions honestly.\n")

    input("Press Enter when you're ready...")

    # Start game
    response = game.start_game()
    session_id = response['session_id']

    # Get all character IDs for first call
    from app.database.models import Character
    all_characters = db.query(Character).all()
    candidate_ids = [c.id for c in all_characters]

    question_num = 1

    while True:
        print(f"\n--- Question {question_num} ---")
        print(response['question'])

        if isinstance(response['options'], list):
            for i, option in enumerate(response['options'], 1):
                print(f"  {i}. {option}")

            while True:
                choice = input("\nYour answer (enter number or text): ").strip()
                # Try to parse as number
                try:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(response['options']):
                        answer = response['options'][choice_num - 1]
                        break
                except ValueError:
                    # Check if text matches an option
                    if choice in response['options']:
                        answer = choice
                        break
                print("Invalid choice. Try again.")
        else:
            # Dictionary options (for ranges)
            for i, option in enumerate(response['options'].keys(), 1):
                print(f"  {i}. {option}")

            while True:
                choice = input("\nYour answer (enter number): ").strip()
                try:
                    choice_num = int(choice)
                    options_list = list(response['options'].keys())
                    if 1 <= choice_num <= len(options_list):
                        answer = options_list[choice_num - 1]
                        break
                except ValueError:
                    pass
                print("Invalid choice. Try again.")

        if response['status'] == 'guess':
            break

        # Answer the question
        response = game.answer_question(
            session_id=session_id,
            question_number=question_num,
            answer=answer,
            candidate_ids=candidate_ids
        )

        if response['status'] == 'continue':
            candidate_ids = response['candidate_ids']
            print(f"\n[{response['remaining_candidates']} possible characters remaining]")
            question_num = response['question_number']
        else:
            break

    # Final guess
    print("\n" + "="*60)
    print("MY GUESS")
    print("="*60 + "\n")

    print(f"After {response['total_questions']} questions, you're thinking of:\n")

    for i, guess in enumerate(response['guesses'], 1):
        print(f"{i}. {guess['name']} ({guess['type']})")
        print(f"   From: {guess['source']}")
        print(f"   Confidence: {guess['confidence']}%")
        print()

    correct = input("Was I correct? (yes/no): ").strip().lower()

    if correct == 'yes':
        print("\n[SUCCESS] Yay! I guessed correctly!")
    else:
        actual = input("Who were you thinking of? ").strip()
        print(f"\n[INFO] Ah, you were thinking of {actual}!")
        print("[INFO] We can add more characters and questions to improve accuracy.")

    db.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == 'play':
        # Interactive mode
        interactive_game()
    elif len(sys.argv) > 1 and sys.argv[1] == 'list':
        # List all characters
        test_all_characters()
    else:
        # Simulation mode (default)
        play_game_simulation()
