from openai import OpenAI
import logging

client = OpenAI()
logger = logging.getLogger(__name__)

def run_openai_for_making_sentence(script):
    logger.info("+ get sentence from words")

    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You're an english app maker, skilled in making setence very well using given words. You can give me sentences naturally"},
        {"role": "user", "content": "I will give you word and start, end for staring time and end time of the word. If the sentence's time is more than 10s, you should give me separate the sentence. Could you make some sentences with completed sentence and star timestamp, end timestamp and during time (end time - start time) without any other mention that you want to say? And could you translate the sentence to Korean with very naturally like born in Korea? ?For example, If you got (Word : I, Start : 0.00 seconds, End : 1 seconds / Word : need, Start : 1 seconds, End : 2 seconds / Word : to, Start : 2 seconds, End : 3 seconds / Word : work, Start : 3 seconds, End : 4 seconds / Word : hard, Start : 4 seconds, End : 5 seconds / Word : because, Start : 5 seconds, End : 5.5 seconds / Word : I'm, Start : 5.5 seconds, End : 6 seconds / Word : Elon Musk, Start : 6 seconds, End : 6.6 seconds / Word : Sorry, Start : 6.6 seconds, End : 6.8 seconds / Word : Just, Start : 6.8 seconds, End : 6.9 seconds / Word : a, Start : 6.9 seconds, End : 7 seconds / Word : kidding, Start : 7 seconds, End : 7.1 seconds.) Then, you should give with the json format (text : I need to work hard because I'm Elon Musk, start : 0.00 seconds, end : 6.6 seconds, dur : 6.6 seconds, kor: 나는 일론 머스크이기 떄문에, 일을 열심히 해야한다. / text : Just a kidding, start : 6.6 seconds, end : 7.1 seconds, dur: 0.5 seconds, kor: 농담이야.) below are the scripts." + script}
    ])

    logger.info("get sentence from words +")

    return completion.choices[0].message.content