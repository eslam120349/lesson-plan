import random
import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize

# Download NLTK data
nltk.download('punkt')

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

def generate_objectives(grade_level, topic, strategy):
    """Generate learning objectives based on grade level, topic and teaching strategy"""
    grade_info = GRADE_VOCABULARY.get(grade_level, GRADE_VOCABULARY['5'])  # Default to 5th grade if not found
    
    # Generate 3-4 objectives using appropriate vocabulary for the grade level
    objectives = []
    verbs = grade_info['verbs']
    
    # Create topic-related objectives
    objectives.append(f"• {random.choice(verbs).capitalize()} the key concepts related to {topic}")
    objectives.append(f"• {random.choice(verbs).capitalize()} how {topic} connects to real-world applications")
    
    # Create strategy-related objective
    strategy_info = TEACHING_STRATEGIES.get(strategy, TEACHING_STRATEGIES['direct_instruction'])
    objectives.append(f"• {random.choice(verbs).capitalize()} through {strategy_info['description'].lower()}")
    
    # Add a skill-based objective
    skill_objective = f"• {random.choice(verbs).capitalize()} skills in critical thinking and problem-solving related to {topic}"
    objectives.append(skill_objective)
    
    # Format the objectives section
    return f"{random.choice(OBJECTIVES_TEMPLATES)}\n" + "\n".join(objectives)

def generate_introduction(grade_level, topic, strategy):
    """Generate lesson introduction"""
    grade_info = GRADE_VOCABULARY.get(grade_level, GRADE_VOCABULARY['5'])
    strategy_info = TEACHING_STRATEGIES.get(strategy, TEACHING_STRATEGIES['direct_instruction'])
    
    intro_template = random.choice(INTRODUCTION_TEMPLATES).format(topic=topic)
    
    # Create hook based on teaching strategy
    if strategy == 'brainstorming':
        hook = f"• Begin with a provocative question about {topic} to spark curiosity"
    elif strategy == 'discovery_learning':
        hook = f"• Present a puzzling phenomenon related to {topic} for students to explore"
    elif strategy == 'game_based':
        hook = f"• Start with a quick energizing game that introduces concepts of {topic}"
    else:
        hook = f"• Engage students with an interesting fact or story about {topic}"
    
    # Create context and relevance
    context = f"• Connect {topic} to students' prior knowledge and experiences"
    relevance = f"• Explain why understanding {topic} is important in real-world contexts"
    
    # Outline lesson structure
    structure = f"• Preview the {strategy_info['description'].lower()} activities students will participate in"
    
    return f"{intro_template}\n{hook}\n{context}\n{relevance}\n{structure}"

def generate_main_activities(grade_level, topic, strategy):
    """Generate main lesson activities"""
    grade_info = GRADE_VOCABULARY.get(grade_level, GRADE_VOCABULARY['5'])
    strategy_info = TEACHING_STRATEGIES.get(strategy, TEACHING_STRATEGIES['direct_instruction'])
    
    main_template = random.choice(MAIN_ACTIVITY_TEMPLATES)
    
    # Select 3 appropriate activities for the teaching strategy
    selected_activities = random.sample(strategy_info['activities'], min(3, len(strategy_info['activities'])))
    
    # Format activities to include topic
    formatted_activities = []
    for i, activity in enumerate(selected_activities, 1):
        # Replace generic terms with specific topic
        specific_activity = activity.replace("content", topic).replace("concept", topic)
        formatted_activities.append(f"• Activity {i}: {specific_activity}")
    
    # Add time consideration
    time_note = f"• Each activity is designed to last approximately {grade_info['duration']} based on {grade_info['complexity']} complexity level"
    
    # Add differentiation note
    differentiation = f"• Differentiation: Provide additional support for struggling students and extension activities for advanced students"
    
    return f"{main_template}\n" + "\n".join(formatted_activities) + f"\n{time_note}\n{differentiation}"

def generate_assessment(grade_level, topic, strategy):
    """Generate assessment strategies"""
    strategy_info = TEACHING_STRATEGIES.get(strategy, TEACHING_STRATEGIES['direct_instruction'])
    
    assessment_template = random.choice(ASSESSMENT_TEMPLATES)
    
    # Select 2-3 assessment strategies appropriate for the teaching strategy
    selected_assessments = random.sample(strategy_info['assessment'], min(3, len(strategy_info['assessment'])))
    
    # Format assessments to include topic
    formatted_assessments = []
    for assessment in selected_assessments:
        specific_assessment = assessment.replace("concepts", topic).replace("content", topic)
        formatted_assessments.append(f"• {specific_assessment}")
    
    # Add a formative and summative assessment note
    formative = f"• Formative: Monitor student understanding through observations and quick checks during activities"
    summative = f"• Summative: Evaluate final student work products that demonstrate understanding of {topic}"
    
    return f"{assessment_template}\n" + "\n".join(formatted_assessments) + f"\n{formative}\n{summative}"

def generate_conclusion(grade_level, topic, strategy):
    """Generate lesson conclusion"""
    conclusion_template = random.choice(CONCLUSION_TEMPLATES).format(topic=topic)
    
    # Create conclusion elements
    summary = f"• Guide students in summarizing key points about {topic}"
    reflection = f"• Ask students to reflect on what they learned and how they learned it"
    connection = f"• Connect learning to upcoming content or real-world applications"
    next_steps = f"• Preview future lessons that will build on this understanding of {topic}"
    
    return f"{conclusion_template}\n{summary}\n{reflection}\n{connection}\n{next_steps}"

def generate_materials(grade_level, topic, strategy):
    """Generate materials list"""
    strategy_info = TEACHING_STRATEGIES.get(strategy, TEACHING_STRATEGIES['direct_instruction'])
    
    # Base materials most lessons would need
    materials = ["• Whiteboard/blackboard and markers/chalk", "• Student notebooks and writing utensils"]
    
    # Strategy-specific materials
    if strategy == 'cooperative_learning':
        materials.extend(["• Group role cards", "• Shared workspace materials", "• Collaboration rubrics"])
    elif strategy == 'brainstorming':
        materials.extend(["• Sticky notes", "• Chart paper", "• Colored markers"])
    elif strategy == 'discovery_learning':
        materials.extend(["• Investigation materials related to topic", "• Data collection sheets", "• Safety equipment if needed"])
    elif strategy == 'project_based':
        materials.extend(["• Project planning templates", "• Research resources", "• Presentation materials"])
    elif strategy == 'game_based':
        materials.extend(["• Game materials or digital devices", "• Score tracking system", "• Prize or recognition items"])
    
    # Add topic-specific material
    materials.append(f"• Content resources about {topic} (books, handouts, digital resources)")
    
    # Add technology if appropriate
    if strategy in ['flipped_classroom', 'project_based', 'game_based']:
        materials.append("• Digital devices (computers, tablets, etc.)")
    
    return "Materials needed:\n" + "\n".join(materials)

def generate_lesson_plan(grade_level, topic, strategy):
    """Generate a complete lesson plan"""
    # Clean inputs to remove any problematic characters
    topic = re.sub(r'[^a-zA-Z0-9\s]', '', topic).strip()
    
    # Create lesson plan sections
    title = f"# Lesson Plan: {topic}\n\n"
    overview = f"**Grade Level:** {grade_level}\n**Topic:** {topic}\n**Teaching Strategy:** {strategy.replace('_', ' ').title()}\n\n"
    
    materials_section = generate_materials(grade_level, topic, strategy) + "\n\n"
    objectives_section = generate_objectives(grade_level, topic, strategy) + "\n\n"
    intro_section = generate_introduction(grade_level, topic, strategy) + "\n\n"
    activities_section = generate_main_activities(grade_level, topic, strategy) + "\n\n"
    assessment_section = generate_assessment(grade_level, topic, strategy) + "\n\n"
    conclusion_section = generate_conclusion(grade_level, topic, strategy)
    
    # Combine all sections
    lesson_plan = (
        title + 
        overview + 
        "## Materials\n" + materials_section +
        "## Objectives\n" + objectives_section +
        "## Introduction\n" + intro_section +
        "## Main Activities\n" + activities_section +
        "## Assessment\n" + assessment_section +
        "## Conclusion\n" + conclusion_section
    )
    
    return lesson_plan
