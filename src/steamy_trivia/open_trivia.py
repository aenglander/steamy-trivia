from enum import Enum, IntEnum
from html import unescape
from typing import NamedTuple, Set, Dict, Union, Any, List
from urllib.parse import unquote

import requests


class Difficulty(Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ResponseCode(IntEnum):
    SUCCESS = 0
    NO_RESULTS = 1
    INVALID_PARAMETER = 2
    TOKEN_NOT_FOUND = 3
    TOKEN_EMPTY_SESSION = 4


class NoResultsException(Exception):
    pass


class InvalidParameterException(Exception):
    pass


class TokenNotFoundException(Exception):
    pass


class NoMoreEntriesException(Exception):
    pass


class UnknownDataException(Exception):
    pass


class Category(NamedTuple):
    id: int
    name: str


class MultipleChoiceQuestion(NamedTuple):
    category: str
    difficulty: Difficulty
    question: str
    correct_answer: str
    incorrect_answers: Set[str]


class BooleanQuestion(NamedTuple):
    category: str
    difficulty: Difficulty
    question: str
    correct_answer: bool


Question = Union[MultipleChoiceQuestion, BooleanQuestion]


class Client:

    def __init__(self) -> None:
        self.__token = None

    @property
    def token(self):
        if self.__token is None:
            response = self.__api_request("/api_token.php",
                                          {"command": "request"},
                                          add_token=False)
            self.__token = response["token"]
        return self.__token

    def get_categories(self) -> Set[Category]:
        response = self.__api_request("/api_category.php", None)
        categories = set()
        for category in response["trivia_categories"]:
            categories.add(Category(category["id"], category["name"]))
        return categories

    def get_questions(self, category: int = None,
                      difficulty: Difficulty = Difficulty.MEDIUM,
                      limit: int = 10) -> List[Question]:
        params = {"difficulty": difficulty.value, "amount": limit,
                  "encoding": "url3986"}
        if category:
            params["category"] = category
        response = self.__api_request("/api.php", params)
        try:
            results = self.__decode(response)["results"]
            questions: List[Question] = []
            for result in results:
                if result["type"] == "boolean":
                    question = BooleanQuestion(
                        result["category"],
                        Difficulty(result["difficulty"]),
                        result["question"],
                        result["correct_answer"] == "True"
                    )
                elif result["type"] == "multiple":
                    question = MultipleChoiceQuestion(
                        result["category"],
                        Difficulty(result["difficulty"]),
                        result["question"],
                        result["correct_answer"],
                        set(result["incorrect_answers"])
                    )
                else:
                    raise UnknownDataException(
                        f"Unknown question type \"{result['type']}\"")
                questions.append(question)
        except KeyError:
            raise UnknownDataException(
                f"Unexpected response: {response}")
        return questions

    def __api_request(self, path: str, params: Union[Dict, None], *,
                      add_token=True) -> Dict:
        if add_token:
            params["token"] = self.token
        response = requests.get(f"https://opentdb.com{path}", params=params)
        response.raise_for_status()
        response_data = response.json()
        response_code = ResponseCode(response_data["response_code"])
        if response_code == ResponseCode.NO_RESULTS:
            raise NoResultsException()
        elif response_code == ResponseCode.INVALID_PARAMETER:
            raise InvalidParameterException()
        elif response_code == ResponseCode.TOKEN_NOT_FOUND:
            raise TokenNotFoundException()
        elif response_code == ResponseCode.TOKEN_EMPTY_SESSION:
            raise NoMoreEntriesException()

        return response_data

    def __decode(self, encoded: Any) -> Dict[str, Any]:
        if isinstance(encoded, dict):
            decoded = {}
            for key, encoded_value in encoded.items():
                if key == "response_message":
                    decoded[key] = encoded_value
                else:
                    decoded[key] = self.__decode(encoded_value)
        elif isinstance(encoded, List):
            decoded = []
            for encoded_item in encoded:
                decoded.append(self.__decode(encoded_item))
        elif isinstance(encoded, str):
            decoded = unescape(unquote(encoded))
        else:
            decoded = encoded

        return decoded
