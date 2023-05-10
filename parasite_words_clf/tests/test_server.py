import unittest
import re
import requests
from unittest import mock
from fastapi.testclient import TestClient

TOTAL_TRUE_SENTS_PROP = 0.7

test_cases_koroche = {
    "У нас получились довольно неплохие результаты": [],
    "Ну короче, у нас получились довольно неплохие результаты": [0, 1],
    "Короче, у нас получилось, что первый короче, чем второй": [0],
    "Первый провод короче второго.": [],
    "Перерыв короче матча.": [],
    "Короче, я не знаю, что с этим делать.": [0],
    "Ну, короче, это было неприятно.": [0, 1],
    "Короче говоря, я не согласен с тобой.": [0],
    "Я был на вечеринке, короче, там было весело.": [4],
    "Я не знаю, короче, как это работает.": [3],
    "Короче, это все, что я могу сказать на эту тему.": [0],
}

test_cases_tipa = {
    "Ну у нас типа неплохо получилось": [0, 3],
    "он полупроводникового типа": [],
    "они довольно умные типа": [3],
    "формат бинарного типа": [],
    "Ну типа": [0, 1],
    "Типа я шел и думал": [0],
    "Типа, я подумал, что это не так уж и важно, и решил пробежаться в своих обычных кедах.": [0],
}

test_cases_common = {
    "Ну он, короче, шел по улице и типа понял что правая рука короче левой": [0, 2, 7],
    "Карандаши квадратного типа короче круглого типа": [],
    "Короче, типа, я собирался пойти на вечеринку, но потом передумал.": [0, 1],
    "Типа, короче, я не знаю, что делать с этой проблемой, она меня уже достала.": [0, 1],
    "Короче, типа, я думаю, что это не так уж и важно, как все говорят.": [0, 1],
}

TEST_DATA = [
    "Добрый день! Расскажите, как прошел ваш вчерашний вечер? Короче, типа я был на вечеринке " \
    "у своего друга, там было много народу, типа и все были очень веселые. Мы пили пиво, короче, и " \
    "слушали музыку. Типа было так много людей, что я даже не помню всех имен. Короче, мы провели там " \
    "всю ночь, типа и ушли утром. Это была очень крутая вечеринка, типа и ушли только утром. Это была " \
    "крутая вечеринка и я надеюсь, что... Ещё раз попаду на неё. Короче, это был один из лучших вечеров моей жизни типа.",
    "Короче, я вчера был на вечеринке у своих друзей, типа там было очень весело. " \
    "Постараюсь рассказать как можно короче. Потом мы решили пойти в кино, типа на новый фильм. " \
    "Было два типа фильма, Ужастик и Боевик. Ужастик был короче, поэтому мы пошли на него." \
    " Ну короче, фильм оказался не очень интересным, типа сюжет был скучный."]

TEST_LONG_SENT = (
    'В 1800-х годах, в те времена, когда не было еще ни железных, ни шоссейных дорог, ни газового, ' \
    'ни стеаринового света, ни пружинных низких диванов, ни мебели без лаку, ни разочарованных юношей ' \
    'со стеклышками, ни либеральных философов-женщин, ни милых дам-камелий, которых так много развелось ' \
    'в наше время, - в те наивные времена, когда из Москвы, выезжая в Петербург в повозке или карете, ' \
    'брали с собой целую кухню домашнего приготовления, ехали восемь суток по мягкой, пыльной или грязной ' \
    'дороге и верили в пожарские котлеты, в валдайские колокольчики и бублики, - когда в длинные осенние ' \
    'вечера нагорали сальные свечи, освещая семейные кружки из двадцати и тридцати человек, на балах в ' \
    'канделябры вставлялись восковые и спермацетовые свечи, когда мебель ставили симметрично, когда наши ' \
    'отцы были еще молоды не одним отсутствием морщин и седых волос, а стрелялись за женщин и из другого ' \
    'угла комнаты бросались поднимать нечаянно и не нечаянно уроненные платочки, наши матери носили ' \
    'коротенькие талии и огромные рукава и решали семейные дела выниманием билетиков, когда прелестные ' \
    'дамы-камелии прятались от дневного света, - в наивные времена масонских лож, мартинистов, тугендбунда, ' \
    'во времена Милорадовичей, Давыдовых, Пушкиных, - в губернском городе К. был съезд помещиков, и кончались ' \
    'дворянские выборы.'
)


def show_context(text, word_idx):
    words_in_sent = re.split('\W+', text)
    return " ".join(words_in_sent[max(word_idx - 2, 0):word_idx + 3])


class TestInferenceModelServer(unittest.TestCase):

    def setUp(self):
        host = "0.0.0.0"
        port = "8000"
        self.url = f"http://{host}:{port}"

    def test_health(self):
        response = requests.get(self.url + "/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Model is ready")

    def test_prediction_big_text(self):

        for test_case in TEST_DATA:
            response = requests.post(
                self.url + f"/predict/",
                json={'text': test_case}
                # json={"data": [DATA], "features": FEATURES}
            )
            # predicts = response.json()
            self.assertEqual(response.status_code, 200)
            # words_in_sent = re.split('\W+', test_case)
            #
            # print("predicts: ", predicts)
            # for val in predicts:
            #     print(show_context(test_case, val))

    def test_prediction_koroche(self):
        counter = 0
        total_cases = len(test_cases_koroche)
        for test_case, labels in test_cases_koroche.items():
            response = requests.post(
                self.url + f"/predict/",
                json={'text': test_case}
            )
            self.assertEqual(response.status_code, 200)
            predicts = response.json()
            counter += int(predicts == labels)
        self.assertTrue(counter / total_cases >= TOTAL_TRUE_SENTS_PROP)

    def test_prediction_tipa(self):
        counter = 0
        total_cases = len(test_cases_tipa)
        for test_case, labels in test_cases_tipa.items():
            response = requests.post(
                self.url + f"/predict/",
                json={'text': test_case}
            )
            self.assertEqual(response.status_code, 200)
            predicts = response.json()
            counter += int(predicts == labels)

        self.assertTrue(counter / total_cases >= TOTAL_TRUE_SENTS_PROP)
        # print("Test: ", test_case, "labels:", labels, "predict:", predicts)
        # self.assertEqual(predicts, labels)
        # if predicts != labels:
        #     print('BAD RESULT!', "Test: ", test_case, "labels:", labels, "predict:", predicts)

    def test_prediction_common(self):

        for test_case, labels in test_cases_common.items():
            response = requests.post(
                self.url + f"/predict/",
                json={'text': test_case}
            )
            self.assertEqual(response.status_code, 200)
            # predicts = response.json()
            # print("Test: ", test_case, "labels:", labels, "predict:", predicts)
            # self.assertEqual(predicts, labels)
            # if predicts != labels:
            #     print('BAD RESULT!', "Test: ", test_case, "labels:", labels, "predict:", predicts)

    def test_root_page(self):
        response = requests.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Parasite words classifier online")

    def test_empty_input(self):
        response = requests.post(
            self.url + f"/predict/",
            json={'text': ''}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

        response = requests.post(
            self.url + f"/predict/",
            json={'text': None}
        )
        self.assertEqual(response.status_code, 422)
        # print("response with empty input: ", response.json())

    def test_long_sent(self):
        response = requests.post(
            self.url + f"/predict/",
            json={'text': TEST_LONG_SENT}
        )
        self.assertEqual(response.status_code, 200)
        # print("response with long input: ", response.json())


if __name__ == "__main__":
    unittest.main()
