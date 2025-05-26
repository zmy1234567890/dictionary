#quiz.py
import random

def start_quiz_EC(dictionary, marked_words, total_questions=10):
    """
    英译中测试：从已标记的英文单词中选出对应中文翻译，
    干扰选项从整个词典随机抽取释义（不包括正确答案）。
    """
    results = []
    words = list(marked_words)
    random.shuffle(words)
    # 选取题库中最多total_questions个单词
    questions_pool = words[:min(total_questions, len(words))]

    # 词典里所有单词
    all_words = list(dictionary.dictionary.keys()) 

    for correct_word in questions_pool:
        # 获取正确单词对应的中文翻译
        correct_translation = dictionary.lookup(correct_word).get('translation')
        if not correct_translation:
            # 没有对应翻译则跳过此题
            continue

        # 从词典所有单词中随机抽释义作为干扰选项，排除正确释义
        incorrect_translations = set()
        while len(incorrect_translations) < 3:
            w = random.choice(all_words)
            t = dictionary.lookup(w).get('translation')
            if t and t != correct_translation:
                incorrect_translations.add(t)
        # 组成选项列表并打乱顺序
        options = [correct_translation] + list(incorrect_translations)
        random.shuffle(options)

        results.append({
            'word': correct_word,  
            'question': correct_word,
            'options': options,
            'answer': correct_translation
        })

    return results

def start_quiz_CE(dictionary, marked_words, total_questions=10):
    """
       中译英测试（Chinese to English quiz）：
       题干为中文翻译，选项为英文单词，正确答案为对应的英文单词。
       干扰选项为词典中随机选择的其他英文单词（不包括正确答案）。
    """
    results = []
    words = list(marked_words)
    random.shuffle(words)
    # 选取题库中最多total_questions个单词
    questions_pool = words[:min(total_questions, len(words))]

    # 词典里所有单词
    all_words = list(dictionary.dictionary.keys()) 

    for correct_word in questions_pool:
        # 获取正确单词对应的中文翻译
        correct_translation = dictionary.lookup(correct_word).get('translation')
        if not correct_translation:
            # 无翻译则跳过
            continue
        # 从词典随机抽取3个错误英文单词作为干扰选项，不包含正确答案
        distractors = set()
        while len(distractors) < 3:
            w = random.choice(all_words)
            if w != correct_word:
                distractors.add(w)
        # 组成选项列表并打乱顺序
        options = [correct_word] + list(distractors)
        random.shuffle(options)

        results.append({
            'word': correct_word,  
            'question': correct_translation,
            'options': options,
            'answer': correct_word
        })

    return results

