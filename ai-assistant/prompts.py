"""
prompts.py

All LLM prompt templates used by the AI Assistant, organized by function.
Each function has THREE distinct prompt variants that differ in one of:
length/specificity, tone/style, or complexity/context, as required by the
project brief. These are kept separate from app logic so they can be
inspected, explained, and swapped independently.
"""

# ============================================================
# FUNCTION 1: ANSWER QUESTIONS
# ============================================================

# Variant "direct": minimal, short, no extra fluff.
# Differs by: length/specificity (shortest, most constrained).
ANSWER_PROMPT_DIRECT = (
    "Answer this question in one or two clear sentences. "
    "Do not add extra commentary.\n\nQuestion: {question}"
)

# Variant "detailed": asks for structured, multi-part output.
# Differs by: complexity/context (adds a requirement for extra related facts).
ANSWER_PROMPT_DETAILED = (
    "Answer the following question clearly and accurately. "
    "After the answer, list two additional related facts as bullet points.\n\n"
    "Question: {question}"
)

# Variant "casual": conversational tone, as if explaining to a friend.
# Differs by: tone/style (informal, friendly voice).
ANSWER_PROMPT_CASUAL = (
    "Someone just asked: \"{question}\" "
    "Explain the answer to them like you're chatting casually with a friend, "
    "keep it warm and simple."
)

ANSWER_PROMPTS = {
    "direct": {
        "label": "Direct & Concise",
        "template": ANSWER_PROMPT_DIRECT,
    },
    "detailed": {
        "label": "Detailed & Structured",
        "template": ANSWER_PROMPT_DETAILED,
    },
    "casual": {
        "label": "Casual & Conversational",
        "template": ANSWER_PROMPT_CASUAL,
    },
}


# ============================================================
# FUNCTION 2: SUMMARIZE TEXT
# ============================================================

# Variant "brief": very short summary, tight length constraint.
# Differs by: length/specificity (forces brevity).
SUMMARY_PROMPT_BRIEF = (
    "Summarize the following text in no more than 3 sentences. "
    "Capture only the single most important idea.\n\nText:\n{text}"
)

# Variant "bullets": structured bullet-point summary.
# Differs by: complexity/context (asks for structured breakdown of main points).
SUMMARY_PROMPT_BULLETS = (
    "Read the following text and list its main points as 3-5 bullet points. "
    "Each bullet should be a single clear idea.\n\nText:\n{text}"
)

# Variant "plain_language": explain simply, as if to someone unfamiliar with the topic.
# Differs by: tone/style (simplified, accessible language).
SUMMARY_PROMPT_PLAIN = (
    "Summarize the following text in plain, simple language, as if explaining "
    "it to someone with no background in the topic.\n\nText:\n{text}"
)

SUMMARY_PROMPTS = {
    "brief": {
        "label": "Brief (3 sentences)",
        "template": SUMMARY_PROMPT_BRIEF,
    },
    "bullets": {
        "label": "Bullet Points",
        "template": SUMMARY_PROMPT_BULLETS,
    },
    "plain_language": {
        "label": "Plain Language",
        "template": SUMMARY_PROMPT_PLAIN,
    },
}


# ============================================================
# FUNCTION 3: GENERATE CREATIVE CONTENT
# ============================================================

# Variant "short_story": a compact narrative with a clear arc.
# Differs by: length/specificity (short, bounded story length).
CREATIVE_PROMPT_SHORT_STORY = (
    "Write a short story (under 200 words) based on this idea: {brief}. "
    "Give it a clear beginning, middle, and end."
)

# Variant "poem": asks specifically for a poem, a different content type entirely.
# Differs by: complexity/context (different creative format/constraints).
CREATIVE_PROMPT_POEM = (
    "Write a short poem (4-8 lines) inspired by this idea: {brief}. "
    "Use vivid imagery and a consistent rhythm."
)

# Variant "playful": encourages a fun, imaginative, humorous take.
# Differs by: tone/style (playful/humorous voice vs neutral narrative).
CREATIVE_PROMPT_PLAYFUL = (
    "Write a fun, imaginative, slightly humorous piece based on this idea: {brief}. "
    "Feel free to be a little silly and surprising."
)

CREATIVE_PROMPTS = {
    "short_story": {
        "label": "Short Story",
        "template": CREATIVE_PROMPT_SHORT_STORY,
    },
    "poem": {
        "label": "Poem",
        "template": CREATIVE_PROMPT_POEM,
    },
    "playful": {
        "label": "Playful & Humorous",
        "template": CREATIVE_PROMPT_PLAYFUL,
    },
}


# ============================================================
# OPTIONAL FUNCTION 4: GIVE ADVICE
# ============================================================

ADVICE_PROMPT_PRACTICAL = (
    "Give 3 practical, actionable tips about: {topic}. "
    "Keep each tip to one sentence."
)

ADVICE_PROMPT_MOTIVATIONAL = (
    "Give encouraging, motivational advice about: {topic}. "
    "Keep it warm and supportive, around 3-4 sentences."
)

ADVICE_PROMPT_EXPERT = (
    "As an expert, give detailed, thoughtful advice about: {topic}. "
    "Include reasoning for why each suggestion helps."
)

ADVICE_PROMPTS = {
    "practical": {
        "label": "Practical Tips",
        "template": ADVICE_PROMPT_PRACTICAL,
    },
    "motivational": {
        "label": "Motivational",
        "template": ADVICE_PROMPT_MOTIVATIONAL,
    },
    "expert": {
        "label": "Expert & Detailed",
        "template": ADVICE_PROMPT_EXPERT,
    },
}


# ============================================================
# Registry: maps function key -> (prompt dict, input field name)
# ============================================================

FUNCTIONS = {
    "answer": {
        "label": "Answer Questions",
        "prompts": ANSWER_PROMPTS,
        "field_name": "question",
        "field_placeholder": "e.g. What is the capital of France?",
        "field_type": "text",
    },
    "summarize": {
        "label": "Summarize Text",
        "prompts": SUMMARY_PROMPTS,
        "field_name": "text",
        "field_placeholder": "Paste the article or text you want summarized...",
        "field_type": "textarea",
    },
    "creative": {
        "label": "Generate Creative Content",
        "prompts": CREATIVE_PROMPTS,
        "field_name": "brief",
        "field_placeholder": "e.g. a story about a dragon and a princess",
        "field_type": "text",
    },
    "advice": {
        "label": "Give Advice",
        "prompts": ADVICE_PROMPTS,
        "field_name": "topic",
        "field_placeholder": "e.g. tips for studying effectively",
        "field_type": "text",
    },
}
