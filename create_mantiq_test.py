"""
Ishlatish:
  python create_mantiq_test.py
  python create_mantiq_test.py --title "Mantiq testi №2"

Har ishlatilganda mantiq_savollar_100ta.md dan tasodifiy 10 ta savol olib,
yangi test yaratadi va test ID sini chiqaradi.
"""

import os
import re
import sys
import random
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, BASE_DIR)

import django
django.setup()

from quiz.models import Test, Question, Choice


def parse_questions(md_path):
    with open(md_path, encoding='utf-8') as f:
        content = f.read()

    questions = []
    blocks = re.split(r'\n---\n', content)

    for block in blocks:
        q_match = re.search(r'\*\*\d+\.\*\*\s+(.+)', block)
        if not q_match:
            continue

        q_text = q_match.group(1).strip()

        choices = []
        for m in re.finditer(r'-\s+[A-D]\)\s+(.+)', block):
            raw = m.group(1).strip()
            is_correct = '✅' in raw
            text = raw.replace('✅', '').strip()
            choices.append((text, is_correct))

        if q_text and len(choices) == 4 and any(c[1] for c in choices):
            questions.append({'text': q_text, 'choices': choices})

    return questions


def create_test(questions_data, title):
    test = Test.objects.create(
        title=title,
        description="12 yoshlilar uchun mantiq testi — tasodifiy 10 ta savol",
        duration_minutes=10,
        is_active=True,
    )
    for i, q_data in enumerate(questions_data, start=1):
        q = Question.objects.create(test=test, text=q_data['text'], order=i)
        for text, is_correct in q_data['choices']:
            Choice.objects.create(question=q, text=text, is_correct=is_correct)
    return test


def main():
    parser = argparse.ArgumentParser(description='Mantiq testini yaratish')
    parser.add_argument('--title', default='', help='Test nomi (ixtiyoriy)')
    args = parser.parse_args()

    md_path = os.path.join(BASE_DIR, 'mantiq_savollar_100ta.md')
    if not os.path.exists(md_path):
        print(f"Xato: {md_path} topilmadi!")
        sys.exit(1)

    all_questions = parse_questions(md_path)
    print(f"Fayldan o'qildi: {len(all_questions)} ta savol")

    if len(all_questions) < 10:
        print("Xato: kamida 10 ta savol kerak!")
        sys.exit(1)

    selected = random.sample(all_questions, 10)

    if args.title:
        title = args.title
    else:
        existing = Test.objects.filter(title__startswith='Mantiq testi').count()
        title = f"Mantiq testi №{existing + 1}"

    test = create_test(selected, title)
    print(f"✓ Test yaratildi!")
    print(f"  ID      : {test.id}")
    print(f"  Nomi    : {test.title}")
    print(f"  Savollar: {test.questions.count()} ta")
    print(f"  URL     : /enter/{test.id}/")


if __name__ == '__main__':
    main()
