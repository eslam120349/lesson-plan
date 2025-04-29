
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="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",
)

# Download NLTK data
#nltk.download('punkt')

# Templates for lesson plan sections
OBJECTIVES_TEMPLATES = [
    "By the end of this lesson, students will be able to:",
    "Lesson objectives:",
    "Learning goals for this lesson:"
]

INTRODUCTION_TEMPLATES = [
    "To begin this lesson on {topic}, the teacher will:",
    "Introduction to {topic}:",
    "The lesson will start with:"
]

MAIN_ACTIVITY_TEMPLATES = [
    "Main learning activities:",
    "Core teaching activities:",
    "The main part of the lesson will consist of:"
]

ASSESSMENT_TEMPLATES = [
    "Assessment strategies:",
    "To assess student understanding, the teacher will:",
    "Evaluation methods:"
]

CONCLUSION_TEMPLATES = [
    "To conclude the lesson on {topic}, the teacher will:",
    "Lesson conclusion:",
    "The lesson will end with:"
]

# Educational vocabulary by grade level
GRADE_VOCABULARY = {
    'K': {
        'verbs': ['identify', 'recognize', 'match', 'sort', 'describe', 'draw', 'tell'],
        'concepts': ['colors', 'shapes', 'numbers', 'letters', 'patterns', 'sounds', 'feelings'],
        'complexity': 'simple',
        'duration': '15-20 minutes'
    },
    '1': {
        'verbs': ['read', 'write', 'count', 'compare', 'classify', 'explain', 'demonstrate'],
        'concepts': ['sight words', 'addition', 'subtraction', 'time', 'plants', 'animals', 'community'],
        'complexity': 'simple',
        'duration': '20-25 minutes'
    },
    '2': {
        'verbs': ['summarize', 'predict', 'measure', 'solve', 'create', 'retell', 'illustrate'],
        'concepts': ['place value', 'life cycles', 'habitats', 'maps', 'folktales', 'weather', 'states of matter'],
        'complexity': 'foundational',
        'duration': '25-30 minutes'
    },
    '3': {
        'verbs': ['analyze', 'infer', 'estimate', 'research', 'compose', 'categorize', 'evaluate'],
        'concepts': ['multiplication', 'division', 'ecosystems', 'communities', 'government', 'fractions', 'plot'],
        'complexity': 'developing',
        'duration': '30-35 minutes'
    },
    '4': {
        'verbs': ['distinguish', 'interpret', 'examine', 'organize', 'formulate', 'assess', 'construct'],
        'concepts': ['decimals', 'fractions', 'ecosystems', 'energy', 'government', 'geography', 'literary elements'],
        'complexity': 'intermediate',
        'duration': '35-40 minutes'
    },
    '5': {
        'verbs': ['investigate', 'debate', 'design', 'develop', 'critique', 'justify', 'synthesize'],
        'concepts': ['variables', 'scientific method', 'operations', 'systems', 'historical events', 'conflicts', 'themes'],
        'complexity': 'intermediate',
        'duration': '40-45 minutes'
    },
    '6': {
        'verbs': ['hypothesize', 'experiment', 'calculate', 'argue', 'revise', 'compose', 'differentiate'],
        'concepts': ['ratios', 'proportions', 'cells', 'ancient civilizations', 'economics', 'statistics', 'evidence'],
        'complexity': 'advanced',
        'duration': '45-50 minutes'
    },
    '7': {
        'verbs': ['evaluate', 'formulate', 'interpret', 'analyze', 'critique', 'investigate', 'synthesize'],
        'concepts': ['algebra', 'scientific inquiry', 'historical contexts', 'literary analysis', 'geographic systems', 'functions', 'probability'],
        'complexity': 'advanced',
        'duration': '45-50 minutes'
    },
    '8': {
        'verbs': ['critique', 'debate', 'assess', 'defend', 'validate', 'deconstruct', 'elaborate'],
        'concepts': ['linear equations', 'chemical reactions', 'civic engagement', 'constitutional principles', 'text structures', 'global issues', 'scientific theories'],
        'complexity': 'advanced',
        'duration': '50-55 minutes'
    },
    '9': {
        'verbs': ['analyze', 'evaluate', 'synthesize', 'critique', 'interpret', 'develop', 'argue'],
        'concepts': ['functions', 'cellular processes', 'historical themes', 'literary devices', 'global systems', 'quadratics', 'ethics'],
        'complexity': 'high school',
        'duration': '55-60 minutes'
    },
    '10': {
        'verbs': ['investigate', 'formulate', 'theorize', 'assess', 'critique', 'validate', 'deconstruct'],
        'concepts': ['geometric proofs', 'molecular biology', 'economic systems', 'rhetorical strategies', 'thematic development', 'cultural contexts', 'scientific models'],
        'complexity': 'high school',
        'duration': '55-60 minutes'
    },
    '11': {
        'verbs': ['hypothesize', 'synthesize', 'evaluate', 'analyze', 'interpret', 'critique', 'develop'],
        'concepts': ['statistical analysis', 'historical perspectives', 'literary criticism', 'biochemistry', 'calculus concepts', 'societal structures', 'philosophical arguments'],
        'complexity': 'high school',
        'duration': '55-60 minutes'
    },
    '12': {
        'verbs': ['theorize', 'integrate', 'deconstruct', 'evaluate', 'synthesize', 'critique', 'innovate'],
        'concepts': ['calculus', 'advanced biology', 'political theory', 'literary movements', 'research methodologies', 'philosophical frameworks', 'global perspectives'],
        'complexity': 'high school',
        'duration': '55-60 minutes'
    }
}

# Teaching strategy implementations
TEACHING_STRATEGIES = {
    'cooperative_learning': {
        'description': 'Students work in groups to complete tasks collectively toward academic goals',
        'activities': [
            'Think-Pair-Share: Students think individually, discuss with a partner, then share with class',
            'Jigsaw: Students become experts on one part of content then teach others',
            'Roundtable: Students take turns responding to a prompt by writing on a shared paper',
            'Numbered Heads Together: Groups work together to answer questions, then one number is called to answer',
            'Circle the Sage: Students who understand concept teach small groups'
        ],
        'assessment': [
            'Group presentation rubrics',
            'Peer evaluation forms',
            'Individual accountability checks',
            'Observation of group dynamics',
            'Group project completion'
        ]
    },
    'brainstorming': {
        'description': 'Students generate a large number of ideas without judgment or criticism',
        'activities': [
            'Mind mapping: Create visual representations of related ideas',
            'Round-robin brainstorming: Each student contributes one idea at a time',
            'Silent brainstorming: Write ideas on sticky notes then organize',
            'Reverse brainstorming: Identify what would make something fail',
            'Role-play brainstorming: Generate ideas from perspective of different roles'
        ],
        'assessment': [
            'Quantity of ideas generated',
            'Quality and relevance of ideas',
            'Participation level',
            'Application of ideas to solve problems',
            'Reflection on process'
        ]
    },
    'discovery_learning': {
        'description': 'Students discover facts and relationships for themselves through exploration',
        'activities': [
            'Guided inquiry: Explore materials with teacher facilitation',
            'Problem-based learning: Solve authentic problems',
            'Simulation activities: Model real-world scenarios',
            'Exploratory experiments: Test hypotheses with minimal guidance',
            'Field investigations: Collect and analyze data from environment'
        ],
        'assessment': [
            'Process journal documentation',
            'Lab reports or field notes',
            'Concept explanation interviews',
            'Application of discoveries to new contexts',
            'Student-created learning artifacts'
        ]
    },
    'direct_instruction': {
        'description': 'Teacher-led explicit instruction with clear explanations and demonstrations',
        'activities': [
            'Interactive lecture with visual aids',
            'Step-by-step modeling of procedures',
            'Worked examples with explanation',
            'Guided practice with immediate feedback',
            'Checking for understanding through questioning'
        ],
        'assessment': [
            'Exit tickets',
            'Quick quizzes',
            'Guided practice completion',
            'Student summarization',
            'Application exercises'
        ]
    },
    'project_based': {
        'description': 'Students work on complex projects over extended time periods',
        'activities': [
            'Driving question exploration',
            'Research and information gathering',
            'Creation of artifacts or products',
            'Regular critique and revision sessions',
            'Public presentation of final work'
        ],
        'assessment': [
            'Project rubrics',
            'Progress check-ins',
            'Learning portfolios',
            'Self and peer evaluations',
            'Final product quality assessment'
        ]
    },
    'flipped_classroom': {
        'description': 'Students gain first exposure to content at home and practice in class',
        'activities': [
            'Pre-recorded instructional videos',
            'Interactive reading assignments',
            'In-class problem-solving workshops',
            'Collaborative application activities',
            'Teacher-guided practice sessions'
        ],
        'assessment': [
            'Pre-class content checks',
            'In-class participation',
            'Application activity completion',
            'Individual mastery checks',
            'Peer teaching effectiveness'
        ]
    },
    'inquiry_based': {
        'description': 'Learning driven by student questions, ideas, and analyses',
        'activities': [
            'Question formulation technique',
            'Investigation planning',
            'Data collection and analysis',
            'Constructing explanations',
            'Communicating findings'
        ],
        'assessment': [
            'Question quality rubrics',
            'Investigation process documentation',
            'Evidence-based conclusions',
            'Presentation of findings',
            'Self-reflection on learning'
        ]
    },
    'differentiated_instruction': {
        'description': 'Tailoring instruction to meet individual student needs',
        'activities': [
            'Tiered assignments based on readiness',
            'Learning stations with varied approaches',
            'Choice boards offering multiple paths',
            'Flexible grouping based on needs',
            'Varied scaffolding and supports'
        ],
        'assessment': [
            'Pre-assessments',
            'Goal-based evaluations',
            'Portfolio assessments',
            'Student choice in demonstrating learning',
            'Growth-focused assessments'
        ]
    },
    'game_based': {
        'description': 'Using games to engage students in learning content and skills',
        'activities': [
            'Educational digital games',
            'Strategy board games for content review',
            'Role-playing scenarios',
            'Competitive review activities',
            'Game design by students to demonstrate understanding'
        ],
        'assessment': [
            'Game performance metrics',
            'Strategic thinking evaluation',
            'Content knowledge quizzes',
            'Game design rubrics',
            'Reflection on learning through gameplay'
        ]
    }
}

def generate_lesson_plan(grade_level, topic, strategy,language):
    language_ = str(language)
    grade_level_ = str(grade_level)
    topic_ = str(topic)
    strategy_ = str(strategy)
    completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  extra_body={},
  model="deepseek/deepseek-r1:free",
  messages=[
    {
      "role": "user",
      "content": f"Create an engaging and detailed lesson plan in  {language_}  for grade {grade_level_} on the topic {topic_}  , using the strategy {strategy_} . Make sure the plan includes clear learning objectives, interactive activities, and effective ways to assess student understanding."
    }
  ]
)
    return (completion.choices[0].message.content)

def gpt_plans(grade_level, topic, strategy, language):
    language_ = str(language)
    grade_level_ = str(grade_level)
    topic_ = str(topic)
    strategy_ = str(strategy)
    return f"Create an engaging and detailed lesson plan in  {language_}  for grade {grade_level_} on the topic {topic_}  , using the strategy {strategy_} . Make sure the plan includes clear learning objectives, interactive activities, and effective ways to assess student understanding."
