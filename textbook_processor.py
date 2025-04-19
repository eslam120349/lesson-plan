import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
import re
import random

# تأكد من تنزيل الموارد اللازمة
nltk.download('punkt')

def clean_text(text):
    """تنظيف النص من الرموز والأحرف غير المرغوبة"""
    # إزالة علامات HTML إذا وجدت
    text = re.sub('<.*?>', '', text)
    # إزالة علامات الترقيم الزائدة
    text = re.sub(r'[^\w\s\.\,\?\!\:\;\-]', '', text)
    # إزالة المسافات المتعددة
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_paragraphs(text):
    """تقسيم النص إلى فقرات"""
    paragraphs = text.split('\n\n')
    return [p.strip() for p in paragraphs if p.strip()]

def extract_sentences(text):
    """تقسيم النص إلى جمل"""
    return sent_tokenize(text)

def identify_main_concepts(text, num_concepts=5):
    """تحديد المفاهيم الرئيسية في النص"""
    # تنظيف النص
    clean = clean_text(text)
    
    # تقسيم إلى كلمات
    words = word_tokenize(clean)
    
    # إزالة الكلمات القصيرة والكلمات الشائعة
    words = [word.lower() for word in words if len(word) > 3]
    
    # حساب تكرار الكلمات
    word_freq = {}
    for word in words:
        if word in word_freq:
            word_freq[word] += 1
        else:
            word_freq[word] = 1
    
    # استخراج الكلمات الأكثر تكرارًا
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
    top_concepts = [word for word, freq in sorted_words[:num_concepts]]
    
    return top_concepts

def generate_objectives(grade_level, concepts):
    """توليد أهداف التعلم بناءً على المفاهيم المستخرجة"""
    objectives = []
    
    # قوالب للأهداف التعليمية
    templates = [
        "فهم المفهوم الأساسي لـ {concept}",
        "شرح العلاقة بين {concept} والمفاهيم الأخرى",
        "تطبيق مبادئ {concept} في حل المشكلات",
        "تحليل خصائص {concept} وتأثيرها",
        "تقييم أهمية {concept} في السياق المناسب"
    ]
    
    # توليد هدف لكل مفهوم رئيسي
    for concept in concepts:
        template = random.choice(templates)
        objective = template.format(concept=concept)
        objectives.append(objective)
    
    return objectives

def generate_introduction(grade_level, topic, concepts):
    """توليد مقدمة للدرس"""
    intro_template = """مقدمة عن {topic}:
    
سيتعرف الطلاب في هذا الدرس على {concept1} و{concept2}. سيتم استكشاف العلاقات بين هذه المفاهيم وأهميتها في فهم {topic}. يهدف هذا الدرس إلى تعزيز فهم الطلاب وقدرتهم على تطبيق هذه المفاهيم في سياقات مختلفة."""
    
    if len(concepts) >= 2:
        return intro_template.format(
            topic=topic,
            concept1=concepts[0],
            concept2=concepts[1]
        )
    elif len(concepts) == 1:
        return intro_template.format(
            topic=topic,
            concept1=concepts[0],
            concept2="المفاهيم المرتبطة به"
        )
    else:
        return "مقدمة عن " + topic

def generate_main_activities(grade_level, topic, concepts, text):
    """توليد أنشطة رئيسية للدرس"""
    # استخراج الفقرات والجمل المهمة
    paragraphs = extract_paragraphs(text)
    important_sentences = []
    
    for para in paragraphs[:3]:  # استخدام أول 3 فقرات
        sentences = extract_sentences(para)
        if sentences:
            important_sentences.append(sentences[0])  # أخذ أول جملة من كل فقرة
    
    # توليد الأنشطة
    activities = []
    
    # نشاط 1: مناقشة المفاهيم الرئيسية
    activity1 = f"""نشاط 1: مناقشة حول {topic}
    
الوقت: 15 دقيقة
الهدف: فهم المفاهيم الرئيسية المتعلقة بـ {topic}
الإجراءات:
1. يقسم المعلم الطلاب إلى مجموعات صغيرة
2. تقوم كل مجموعة بمناقشة النقاط الرئيسية:
   - {concepts[0] if concepts else 'المفهوم الأول'}
   - {concepts[1] if len(concepts) > 1 else 'المفهوم الثاني'}
3. تشارك المجموعات ما توصلت إليه مع الصف"""
    
    # نشاط 2: تحليل النص
    activity2 = f"""نشاط 2: تحليل النص
    
الوقت: 20 دقيقة
الهدف: استخراج المعلومات المهمة من النص
الإجراءات:
1. يقرأ الطلاب النص التالي:
   "{important_sentences[0] if important_sentences else 'النص المقدم'}"
2. يستخرج الطلاب المعلومات المهمة
3. يقوم الطلاب بتلخيص الأفكار الرئيسية"""
    
    # نشاط 3: تطبيق المفاهيم
    activity3 = f"""نشاط 3: تطبيق المفاهيم
    
الوقت: 25 دقيقة
الهدف: تطبيق المفاهيم المتعلقة بـ {topic}
الإجراءات:
1. يعمل الطلاب في أزواج لحل المشكلات المتعلقة بـ {topic}
2. يقوم الطلاب بإنشاء عروض تقديمية قصيرة
3. يعرض الطلاب عملهم أمام الصف للمناقشة والتغذية الراجعة"""
    
    activities.extend([activity1, activity2, activity3])
    return "\n\n".join(activities)

def generate_assessment(grade_level, topic, concepts):
    """توليد استراتيجيات التقييم"""
    assessment_text = f"""التقييم:
    
1. تقييم تكويني:
   - ملاحظة مشاركة الطلاب في الأنشطة
   - أسئلة شفهية أثناء الدرس لقياس الفهم
   - مناقشات في المجموعات الصغيرة

2. تقييم ختامي:
   - اطلب من الطلاب كتابة فقرة تلخص المفاهيم الرئيسية في {topic}
   - حل تمارين في كتاب الطالب المتعلقة بـ {concepts[0] if concepts else topic}
   - إنشاء خريطة مفاهيم توضح العلاقات بين {concepts[0] if concepts else ''} و{concepts[1] if len(concepts) > 1 else ''} والمفاهيم الأخرى"""
    
    return assessment_text

def generate_conclusion(grade_level, topic, concepts):
    """توليد خاتمة للدرس"""
    conclusion_text = f"""الخاتمة:
    
- مراجعة سريعة للمفاهيم الرئيسية التي تم تغطيتها في الدرس
- التأكيد على أهمية {topic} في سياق المادة بشكل عام
- توجيه الطلاب إلى الموارد الإضافية للمزيد من التعلم
- الإعلان عن الواجب المنزلي والأنشطة التالية"""
    
    return conclusion_text

def generate_materials(grade_level, topic, concepts):
    """توليد قائمة المواد المطلوبة"""
    materials_text = f"""المواد المطلوبة:
    
- كتاب الطالب
- أوراق عمل حول {topic}
- سبورة ذكية أو تقليدية
- أقلام وأوراق للمجموعات
- موارد بصرية توضح {concepts[0] if concepts else topic}
- أجهزة حاسوب (اختياري للبحث عن معلومات إضافية)"""
    
    return materials_text

def process_textbook_content(grade_level, topic, teaching_strategy, textbook_content):
    """معالجة محتوى الكتاب المدرسي وتوليد خطة درس كاملة"""
    # تنظيف النص
    cleaned_text = clean_text(textbook_content)
    
    # استخراج المفاهيم الرئيسية
    main_concepts = identify_main_concepts(cleaned_text)
    
    # توليد أهداف التعلم
    objectives = generate_objectives(grade_level, main_concepts)
    objectives_text = "الأهداف التعليمية:\n\n" + "\n".join([f"- {obj}" for obj in objectives])
    
    # توليد عناصر خطة الدرس
    introduction = generate_introduction(grade_level, topic, main_concepts)
    main_activities = generate_main_activities(grade_level, topic, main_concepts, cleaned_text)
    assessment = generate_assessment(grade_level, topic, main_concepts)
    conclusion = generate_conclusion(grade_level, topic, main_concepts)
    materials = generate_materials(grade_level, topic, main_concepts)
    
    # تجميع خطة الدرس
    lesson_plan = f"""# خطة درس: {topic}
## المستوى: الصف {grade_level}
## استراتيجية التدريس: {teaching_strategy}

{objectives_text}

{introduction}

{main_activities}

{assessment}

{conclusion}

{materials}
"""
    
    return lesson_plan