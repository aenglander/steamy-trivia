from random import random
from time import sleep

import click

from .open_trivia import Client, NoMoreEntriesException, BooleanQuestion


def run():
    total = 0
    correct = 0
    skipped = 0
    questions_to_ask = 10
    client = Client()
    try:
        while total < questions_to_ask:
            click.echo("Gathering some questions...")
            for question in client.get_questions():
                click.clear()
                if isinstance(question, BooleanQuestion):
                    answers = {"True", "False"}
                    correct_answer = 0 if question.correct_answer else 1
                else:
                    responses = question.incorrect_answers.copy()
                    responses.add(question.correct_answer)
                    answers = sorted(responses, key=lambda _: random())
                    correct_answer = answers.index(question.correct_answer)

                click.echo(question.question)
                response = __get_response(answers)
                valid_responses = range(1, len(answers) + 1)
                while response not in valid_responses:
                    click.echo(f"{response} is not a valid response",
                               color="yellow")
                    response = __get_response(answers)

                if response - 1 == correct_answer:
                    correct += 1
                    click.echo("Correct!", color="green")
                else:
                    click.echo(f"Incorrect. The correct answer was: "
                               f"{question.correct_answer}", color="red")
                total += 1

                click.echo(f"You have answered {correct}"
                           f" out of {total} correctly")
                sleep(5)

    except (NoMoreEntriesException, KeyboardInterrupt):
        click.echo(f"You'r final score is {correct}"
                   f" out of {total} questions answered correctly.")


def __get_response(answers):
    answer_number = 0
    for answer in answers:
        answer_number += 1
        click.echo(f"     ({answer_number}) {answer}")
    try:
        key = int(click.getchar())
    except ValueError:
        key = None
    return key
