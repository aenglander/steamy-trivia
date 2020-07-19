from random import random
from time import sleep, time
from typing import List

import click

from .open_trivia import Client, NoMoreEntriesException, BooleanQuestion


def run():
    total = 0
    correct = 0
    skipped = 0
    questions_to_ask = 30
    client = Client()
    try:
        click.echo("All trivia is provided via the Open Trivia Database")
        click.echo("under Creative Commons Attribution-ShareAlike"
                   " 4.0 International License")
        click.echo("(https://creativecommons.org/licenses/by-sa/4.0/).")
        start = time()
        questions = client.get_questions()
        elapsed = time() - start
        if elapsed < 3.0:
            sleep(3.0 - elapsed)
        while total < questions_to_ask:

            while questions:
                question = questions.pop(0)
                click.clear()
                if isinstance(question, BooleanQuestion):
                    answers = {"True", "False"}
                    correct_answer = 0 if question.correct_answer else 1
                else:
                    responses = question.incorrect_answers.copy()
                    responses.add(question.correct_answer)
                    answers = sorted(responses, key=lambda _: random())
                    correct_answer = answers.index(question.correct_answer)

                response = __get_response(question.question, answers)
                valid_responses = range(1, len(answers) + 1)
                while response not in valid_responses:
                    click.echo(f"{response} is not a valid response",
                               color="yellow")
                    response = __get_response(question.question, answers)

                if response - 1 == correct_answer:
                    correct += 1
                    click.echo("Correct!", color="green")
                else:
                    click.echo(f"Incorrect. The correct answer was: "
                               f"{question.correct_answer}", color="red")
                total += 1

                click.echo(f"You have answered {correct}"
                           f" out of {total} correctly")

                start = time()
                if not questions:
                    questions += client.get_questions()
                elapsed = time() - start
                if elapsed < 1.0:
                    sleep(1.0 - elapsed)

    except (NoMoreEntriesException, KeyboardInterrupt):
        click.echo(f"Your final score is {correct}"
                   f" out of {total} questions answered correctly.")


def __get_response(question: str, answers: List[str]):
    click.echo(question)
    answer_number = 0
    for answer in answers:
        answer_number += 1
        click.echo(f"     ({answer_number}) {answer}")
    try:
        key = int(click.getchar())
    except ValueError:
        key = None
    return key


if __name__ == "__main__":
    run()