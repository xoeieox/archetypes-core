"""
Archetypal Intelligence — Primitive Catalog (auto-generated)

88 behavioral primitives across 7 categories.
Each primitive defines its tension and complementary relationships
with other primitives, enabling pure-computation T/C/V scoring
without LLM calls.

DO NOT EDIT BY HAND — regenerate with scripts/compile_primitives.py
"""

PRIMITIVES = {
    # =========================================================================
    # BEHAVIORAL (17)
    # =========================================================================
    "adaptive-flexibility": {
        "name": "Adaptive Flexibility",
        "category": "behavioral",
        "description": "Changes approach based on feedback — survival through adaptation rather than persistence",
        "tension_with": [
        "rigid-adherence",
        "obsessive-focus",
        "resistance-to-change",
    ],
        "complementary_with": [
        "methodical-approach",
        "rigid-adherence",
        "duty-over-desire",
    ],
        "shadow_volatility": 0.3,
    },
    "cautious-conservatism": {
        "name": "Cautious Conservatism",
        "category": "behavioral",
        "description": "Preserves what works and minimizes risk — better to protect gains than gamble for more",
        "tension_with": [
        "risk-taking",
        "impulsive-action",
        "curiosity-driven-exploration",
    ],
        "complementary_with": [
        "risk-taking",
        "capacity-for-change",
        "adaptive-flexibility",
    ],
        "shadow_volatility": 0.3,
    },
    "charismatic-leadership": {
        "name": "Charismatic Leadership",
        "category": "behavioral",
        "description": "The ability to inspire others to follow through force of personality, vision, and emotional magnetism",
        "tension_with": [
        "humility",
        "isolation-as-protection",
        "withdrawal-retreat",
    ],
        "complementary_with": [
        "humility",
        "duty-over-desire",
        "connection-seeking",
    ],
        "shadow_volatility": 0.3,
    },
    "impulsive-action": {
        "name": "Impulsive Action",
        "category": "behavioral",
        "description": "Acts immediately on impulse — the gap between stimulus and response approaches zero",
        "tension_with": [
        "patient-observation",
        "methodical-approach",
        "cautious-conservatism",
    ],
        "complementary_with": [
        "patient-observation",
        "systematic-analysis",
        "self-mastery",
    ],
        "shadow_volatility": 0.3,
    },
    "institutional-transmutation": {
        "name": "Institutional Transmutation",
        "category": "behavioral",
        "description": "Transforming a system's purpose while preserving its structure — redirecting existing machinery to serve the opposite of its original intent",
        "tension_with": [
        "defiance-rebellion",
        "creative-expression",
        "personal-freedom-priority",
    ],
        "complementary_with": [
        "capacity-for-change",
        "positional-perception",
        "methodical-approach",
    ],
        "shadow_volatility": 0.3,
    },
    "methodical-approach": {
        "name": "Methodical Approach",
        "category": "behavioral",
        "description": "Plans thoroughly before acting and follows the plan with discipline — execution is sacred",
        "tension_with": [
        "impulsive-action",
        "adaptive-flexibility",
        "lateral-thinking",
    ],
        "complementary_with": [
        "adaptive-flexibility",
        "lateral-thinking",
        "risk-taking",
    ],
        "shadow_volatility": 0.3,
    },
    "obsessive-focus": {
        "name": "Obsessive Focus",
        "category": "behavioral",
        "description": "Cannot disengage from a problem once engaged — the mind locks on and will not let go",
        "tension_with": [
        "adaptive-flexibility",
        "social-connection-for-regulation",
        "harmony-over-conflict",
    ],
        "complementary_with": [
        "adaptive-flexibility",
        "connection-seeking",
        "self-mastery",
    ],
        "shadow_volatility": 0.3,
    },
    "patient-observation": {
        "name": "Patient Observation",
        "category": "behavioral",
        "description": "Waits, watches, and gathers information before acting — the watcher who sees what the hasty miss",
        "tension_with": [
        "impulsive-action",
        "passionate-intensity",
        "rage-response",
    ],
        "complementary_with": [
        "impulsive-action",
        "risk-taking",
        "decisive-logic",
    ],
        "shadow_volatility": 0.3,
    },
    "performative-display": {
        "name": "Performative Display",
        "category": "behavioral",
        "description": "The need to be seen, to present, to control how one is perceived",
        "tension_with": [
        "vulnerability",
        "stoic-acceptance",
        "humility",
    ],
        "complementary_with": [
        "social-charm",
        "pride",
        "charismatic-leadership",
    ],
        "shadow_volatility": 0.3,
    },
    "performative-eloquence": {
        "name": "Performative Eloquence",
        "category": "behavioral",
        "description": "Speech that creates reality rather than describes it — language deployed not as communication but as an instrument for generating belief, independent of underlying truth",
        "tension_with": [
        "truth-above-all",
        "concrete-pragmatism",
        "existential-void",
        "vulnerability",
    ],
        "complementary_with": [
        "charismatic-leadership",
        "strategic-deception",
        "manipulation",
        "pride",
    ],
        "shadow_volatility": 0.3,
    },
    "rigid-adherence": {
        "name": "Rigid Adherence",
        "category": "behavioral",
        "description": "Sticks to the chosen path regardless of changing circumstances — commitment as an absolute",
        "tension_with": [
        "adaptive-flexibility",
        "lateral-thinking",
        "humor-as-defense",
    ],
        "complementary_with": [
        "adaptive-flexibility",
        "humility",
        "capacity-for-change",
    ],
        "shadow_volatility": 0.3,
    },
    "risk-taking": {
        "name": "Risk-Taking",
        "category": "behavioral",
        "description": "Embraces danger, uncertainty, and exposure for the possibility of extraordinary gain",
        "tension_with": [
        "cautious-conservatism",
        "anxious-vigilance",
        "methodical-approach",
    ],
        "complementary_with": [
        "cautious-conservatism",
        "systematic-analysis",
        "patient-observation",
    ],
        "shadow_volatility": 0.3,
    },
    "self-mastery": {
        "name": "Self-Mastery",
        "category": "behavioral",
        "description": "Disciplined control over one's own impulses, emotions, and desires — the will governing the self",
        "tension_with": [
        "impulsive-action",
        "drug-seeking-escape",
        "passionate-intensity",
    ],
        "complementary_with": [
        "passionate-intensity",
        "impulsive-action",
        "pleasure-priority",
    ],
        "shadow_volatility": 0.3,
    },
    "social-charm": {
        "name": "Social Charm",
        "category": "behavioral",
        "description": "Natural magnetism and warmth — the ability to put others at ease and make them feel valued",
        "tension_with": [
        "strategic-deception",
        "isolation-as-protection",
    ],
        "complementary_with": [
        "generosity",
        "empathic-resonance",
        "performative-display",
    ],
        "shadow_volatility": 0.3,
    },
    "social-wit": {
        "name": "Social Wit",
        "category": "behavioral",
        "description": "Sharp, quick verbal intelligence deployed in social situations — the ability to read a room and respond with precision",
        "tension_with": [
        "withdrawal-retreat",
        "melancholic-tendency",
        "isolation-as-protection",
    ],
        "complementary_with": [
        "connection-seeking",
        "humility",
        "stoic-acceptance",
    ],
        "shadow_volatility": 0.3,
    },
    "survival-instinct": {
        "name": "Survival Instinct",
        "category": "behavioral",
        "description": "The raw determination to stay alive — not courage but the deeper animal refusal to die",
        "tension_with": [
        "stoic-acceptance",
        "surrender-as-agency",
        "philosophical-contemplation",
    ],
        "complementary_with": [
        "adaptive-flexibility",
        "physical-activity-release",
        "risk-taking",
    ],
        "shadow_volatility": 0.3,
    },
    "territorial-control": {
        "name": "Territorial Control",
        "category": "behavioral",
        "description": "The need to claim, secure, and defend space and resources",
        "tension_with": [
        "generosity",
        "adaptive-flexibility",
    ],
        "complementary_with": [
        "patient-observation",
        "pride",
        "rigid-adherence",
    ],
        "shadow_volatility": 0.3,
    },
    # =========================================================================
    # COGNITIVE (12)
    # =========================================================================
    "abstract-conceptualization": {
        "name": "Abstract Conceptualization",
        "category": "cognitive",
        "description": "Thinks in systems, theories, and models — seeking the underlying principle beneath surface phenomena",
        "tension_with": [
        "impulsive-action",
        "concrete-pragmatism",
        "physical-activity-release",
    ],
        "complementary_with": [
        "concrete-pragmatism",
        "methodical-approach",
        "patient-observation",
    ],
        "shadow_volatility": 0.2,
    },
    "concrete-pragmatism": {
        "name": "Concrete Pragmatism",
        "category": "cognitive",
        "description": "'What works?' takes absolute priority over 'What's theoretically correct?'",
        "tension_with": [
        "philosophical-contemplation",
        "abstract-conceptualization",
        "melancholic-tendency",
    ],
        "complementary_with": [
        "abstract-conceptualization",
        "systematic-analysis",
        "patient-observation",
    ],
        "shadow_volatility": 0.2,
    },
    "curiosity-driven-exploration": {
        "name": "Curiosity-Driven Exploration",
        "category": "cognitive",
        "description": "An irresistible drive to investigate, discover, and understand — the unknown is an invitation, not a threat",
        "tension_with": [
        "cautious-conservatism",
        "resistance-to-change",
        "withdrawal-retreat",
    ],
        "complementary_with": [
        "cautious-conservatism",
        "self-mastery",
        "systematic-analysis",
    ],
        "shadow_volatility": 0.2,
    },
    "deductive-logic": {
        "name": "Deductive Logic",
        "category": "cognitive",
        "description": "Reduces complexity by eliminating impossibilities until only truth remains",
        "tension_with": [
        "passionate-intensity",
        "impulsive-action",
        "joyful-optimism",
    ],
        "complementary_with": [
        "intuitive-leaps",
        "connection-seeking",
        "humility",
    ],
        "shadow_volatility": 0.2,
    },
    "intuitive-leaps": {
        "name": "Intuitive Leaps",
        "category": "cognitive",
        "description": "Arrives at conclusions through subconscious pattern-matching before conscious reasoning can explain why",
        "tension_with": [
        "systematic-analysis",
        "methodical-approach",
        "concrete-pragmatism",
    ],
        "complementary_with": [
        "deductive-logic",
        "patient-observation",
        "humility",
    ],
        "shadow_volatility": 0.2,
    },
    "lateral-thinking": {
        "name": "Lateral Thinking",
        "category": "cognitive",
        "description": "Solves problems by approaching from unexpected angles rather than following the obvious path",
        "tension_with": [
        "rigid-adherence",
        "deductive-logic",
        "cautious-conservatism",
    ],
        "complementary_with": [
        "systematic-analysis",
        "methodical-approach",
        "concrete-pragmatism",
    ],
        "shadow_volatility": 0.2,
    },
    "manipulation": {
        "name": "Manipulation",
        "category": "cognitive",
        "description": "Strategic influence of others' perceptions and choices — the chess player of human interaction",
        "tension_with": [
        "generosity",
        "vulnerability",
        "loyal-companionship",
    ],
        "complementary_with": [
        "strategic-deception",
        "systematic-analysis",
        "social-wit",
    ],
        "shadow_volatility": 0.2,
    },
    "memory-based-processing": {
        "name": "Memory-Based Processing",
        "category": "cognitive",
        "description": "Relies on accumulated past experience as the primary lens for understanding the present",
        "tension_with": [
        "risk-taking",
        "curiosity-driven-exploration",
        "impulsive-action",
    ],
        "complementary_with": [
        "adaptive-flexibility",
        "capacity-for-change",
        "lateral-thinking",
    ],
        "shadow_volatility": 0.2,
    },
    "pattern-recognition": {
        "name": "Pattern Recognition",
        "category": "cognitive",
        "description": "Perceives recurring structures across disparate events, seeing the rhyme where others see only noise",
        "tension_with": [
        "concrete-pragmatism",
        "impulsive-action",
        "lateral-thinking",
    ],
        "complementary_with": [
        "abstract-conceptualization",
        "patient-observation",
        "humility",
    ],
        "shadow_volatility": 0.2,
    },
    "philosophical-contemplation": {
        "name": "Philosophical Contemplation",
        "category": "cognitive",
        "description": "The drive to examine life's fundamental questions — meaning, mortality, identity, existence — not as academic exercise but as lived practice",
        "tension_with": [
        "concrete-pragmatism",
        "impulsive-action",
        "work-as-anesthetic",
    ],
        "complementary_with": [
        "concrete-pragmatism",
        "impulsive-action",
        "physical-activity-release",
    ],
        "shadow_volatility": 0.2,
    },
    "strategic-deception": {
        "name": "Strategic Deception",
        "category": "cognitive",
        "description": "Uses misdirection, disguise, and calculated dishonesty as tools to achieve goals others would block through direct means",
        "tension_with": [
        "truth-above-all",
        "connection-seeking",
        "harmony-over-conflict",
    ],
        "complementary_with": [
        "truth-above-all",
        "loyal-companionship",
        "humility",
    ],
        "shadow_volatility": 0.2,
    },
    "systematic-analysis": {
        "name": "Systematic Analysis",
        "category": "cognitive",
        "description": "Approaches problems step-by-step, ensuring no component is missed before drawing conclusions",
        "tension_with": [
        "impulsive-action",
        "lateral-thinking",
        "passionate-intensity",
    ],
        "complementary_with": [
        "intuitive-leaps",
        "risk-taking",
        "adaptive-flexibility",
    ],
        "shadow_volatility": 0.2,
    },
    # =========================================================================
    # COPING (8)
    # =========================================================================
    "artistic-expression-as-processing": {
        "name": "Artistic Expression as Processing",
        "category": "coping",
        "description": "Creates — paints, writes, plays, builds — to understand and regulate what cannot be processed through thought alone",
        "tension_with": [
        "concrete-pragmatism",
        "impulsive-action",
        "work-as-anesthetic",
    ],
        "complementary_with": [
        "intellectual-absorption",
        "connection-seeking",
        "capacity-for-change",
    ],
        "shadow_volatility": 0.25,
    },
    "drug-seeking-escape": {
        "name": "Drug-Seeking Escape",
        "category": "coping",
        "description": "Turns to chemical alteration to manage distress, boredom, or understimulation",
        "tension_with": [
        "self-mastery",
        "stoic-acceptance",
        "methodical-approach",
    ],
        "complementary_with": [
        "artistic-expression-as-processing",
        "physical-activity-release",
        "connection-seeking",
    ],
        "shadow_volatility": 0.25,
    },
    "humor-as-defense": {
        "name": "Humor as Defense",
        "category": "coping",
        "description": "Uses jokes, wit, and levity to deflect pain, defuse tension, and keep vulnerability at bay",
        "tension_with": [
        "stoic-acceptance",
        "melancholic-tendency",
        "rigid-adherence",
    ],
        "complementary_with": [
        "passionate-intensity",
        "connection-seeking",
        "capacity-for-change",
    ],
        "shadow_volatility": 0.25,
    },
    "intellectual-absorption": {
        "name": "Intellectual Absorption",
        "category": "coping",
        "description": "Loses self in mental challenges to escape or manage emotional difficulty — the mind as refuge",
        "tension_with": [
        "physical-activity-release",
        "social-connection-for-regulation",
        "impulsive-action",
    ],
        "complementary_with": [
        "connection-seeking",
        "artistic-expression-as-processing",
        "passionate-intensity",
    ],
        "shadow_volatility": 0.25,
    },
    "physical-activity-release": {
        "name": "Physical Activity Release",
        "category": "coping",
        "description": "Discharges tension through the body — movement, exertion, and physical engagement as emotional regulation",
        "tension_with": [
        "withdrawal-retreat",
        "intellectual-absorption",
        "philosophical-contemplation",
    ],
        "complementary_with": [
        "intellectual-absorption",
        "artistic-expression-as-processing",
        "stoic-acceptance",
    ],
        "shadow_volatility": 0.25,
    },
    "social-connection-for-regulation": {
        "name": "Social Connection for Regulation",
        "category": "coping",
        "description": "Seeks other people when dysregulated — co-regulation through relational presence",
        "tension_with": [
        "isolation-as-protection",
        "withdrawal-retreat",
        "work-as-anesthetic",
    ],
        "complementary_with": [
        "withdrawal-retreat",
        "self-mastery",
        "intellectual-absorption",
    ],
        "shadow_volatility": 0.25,
    },
    "withdrawal-retreat": {
        "name": "Withdrawal/Retreat",
        "category": "coping",
        "description": "Goes to ground when overwhelmed — isolation as emergency shutdown rather than considered distance",
        "tension_with": [
        "connection-seeking",
        "social-connection-for-regulation",
        "loyal-companionship",
    ],
        "complementary_with": [
        "social-connection-for-regulation",
        "connection-seeking",
        "capacity-for-change",
    ],
        "shadow_volatility": 0.25,
    },
    "work-as-anesthetic": {
        "name": "Work as Anesthetic",
        "category": "coping",
        "description": "Buries self in productivity to avoid feeling — busyness as numbing agent",
        "tension_with": [
        "pleasure-priority",
        "joyful-optimism",
        "withdrawal-retreat",
    ],
        "complementary_with": [
        "social-connection-for-regulation",
        "artistic-expression-as-processing",
        "capacity-for-change",
    ],
        "shadow_volatility": 0.25,
    },
    # =========================================================================
    # EMOTIONAL (15)
    # =========================================================================
    "anxious-vigilance": {
        "name": "Anxious Vigilance",
        "category": "emotional",
        "description": "Constant scanning for threats — the sentinel who never stands down",
        "tension_with": [
        "risk-taking",
        "impulsive-action",
        "joyful-optimism",
    ],
        "complementary_with": [
        "joyful-optimism",
        "stoic-acceptance",
        "risk-taking",
    ],
        "shadow_volatility": 0.4,
    },
    "connection-seeking": {
        "name": "Connection-Seeking",
        "category": "emotional",
        "description": "Needs relational bonds for emotional regulation — isolation is not peace but deprivation",
        "tension_with": [
        "withdrawal-retreat",
        "obsessive-focus",
        "isolation-as-protection",
    ],
        "complementary_with": [
        "isolation-as-protection",
        "self-mastery",
        "integration",
    ],
        "shadow_volatility": 0.4,
    },
    "despair": {
        "name": "Despair",
        "category": "emotional",
        "description": "The collapse of all exits — a state in which every possible action appears blocked or inadequate, and annihilation presents itself as a logical conclusion rather than an emotional one",
        "tension_with": [
        "faith-driven-purpose",
        "capacity-for-change",
        "integration",
        "joyful-optimism",
    ],
        "complementary_with": [
        "existential-seeing",
        "fragmentation",
        "melancholic-tendency",
        "isolation-as-protection",
    ],
        "shadow_volatility": 0.4,
    },
    "empathic-resonance": {
        "name": "Empathic Resonance",
        "category": "emotional",
        "description": "Involuntary emotional mirroring — feeling what others feel before thinking about it",
        "tension_with": [
        "stoic-acceptance",
        "strategic-deception",
        "obsessive-focus",
    ],
        "complementary_with": [
        "nurturing",
        "healing-through-medium",
        "sensitivity",
    ],
        "shadow_volatility": 0.4,
    },
    "grief": {
        "name": "Grief",
        "category": "emotional",
        "description": "The raw experience of irreplaceable loss — not the processing of it but the fact of it, present and undeniable",
        "tension_with": [
        "work-as-anesthetic",
        "joyful-optimism",
        "stoic-acceptance",
        "adaptive-flexibility",
    ],
        "complementary_with": [
        "grief-processing",
        "melancholic-tendency",
        "isolation-as-protection",
        "memory-based-processing",
    ],
        "shadow_volatility": 0.4,
    },
    "grief-processing": {
        "name": "Grief Processing",
        "category": "emotional",
        "description": "The active process of metabolizing loss — not sadness as disposition but grief as transformation",
        "tension_with": [
        "stoic-acceptance",
        "work-as-anesthetic",
        "joyful-optimism",
    ],
        "complementary_with": [
        "melancholic-tendency",
        "connection-seeking",
        "stoic-acceptance",
    ],
        "shadow_volatility": 0.4,
    },
    "isolation-as-protection": {
        "name": "Isolation as Protection",
        "category": "emotional",
        "description": "Maintains emotional distance as a defense mechanism — closeness is danger, solitude is safety",
        "tension_with": [
        "passionate-intensity",
        "social-connection-for-regulation",
        "belonging-seeking",
    ],
        "complementary_with": [
        "connection-seeking",
        "loyal-companionship",
        "capacity-for-change",
    ],
        "shadow_volatility": 0.4,
    },
    "joyful-optimism": {
        "name": "Joyful Optimism",
        "category": "emotional",
        "description": "A baseline orientation toward possibility, hope, and the belief that things can and will improve",
        "tension_with": [
        "melancholic-tendency",
        "anxious-vigilance",
        "wrath",
    ],
        "complementary_with": [
        "melancholic-tendency",
        "stoic-acceptance",
        "patient-observation",
    ],
        "shadow_volatility": 0.4,
    },
    "loyal-companionship": {
        "name": "Loyal Companionship",
        "category": "emotional",
        "description": "Steadfast commitment to a specific person or small group — 'I am here for you' as a defining orientation",
        "tension_with": [
        "isolation-as-protection",
        "personal-freedom-priority",
        "achievement-driven",
    ],
        "complementary_with": [
        "personal-freedom-priority",
        "pride",
        "self-mastery",
    ],
        "shadow_volatility": 0.4,
    },
    "melancholic-tendency": {
        "name": "Melancholic Tendency",
        "category": "emotional",
        "description": "A baseline gravitational pull toward sadness, introspection, and awareness of loss",
        "tension_with": [
        "joyful-optimism",
        "risk-taking",
        "impulsive-action",
    ],
        "complementary_with": [
        "joyful-optimism",
        "capacity-for-change",
        "connection-seeking",
    ],
        "shadow_volatility": 0.4,
    },
    "passionate-intensity": {
        "name": "Passionate Intensity",
        "category": "emotional",
        "description": "Feels everything deeply — there is no emotional middle ground, only full engagement or emptiness",
        "tension_with": [
        "stoic-acceptance",
        "cautious-conservatism",
        "methodical-approach",
    ],
        "complementary_with": [
        "stoic-acceptance",
        "self-mastery",
        "patient-observation",
    ],
        "shadow_volatility": 0.4,
    },
    "rage-response": {
        "name": "Rage Response",
        "category": "emotional",
        "description": "Anger as the primary emotional reaction to frustration, injustice, or threat — heat before thought",
        "tension_with": [
        "harmony-over-conflict",
        "cautious-conservatism",
        "humility",
    ],
        "complementary_with": [
        "stoic-acceptance",
        "self-mastery",
        "patient-observation",
    ],
        "shadow_volatility": 0.4,
    },
    "sensitivity": {
        "name": "Sensitivity",
        "category": "emotional",
        "description": "Heightened perceptual and emotional receptivity — noticing what others miss",
        "tension_with": [
        "stoic-acceptance",
        "impulsive-action",
        "rage-response",
    ],
        "complementary_with": [
        "empathic-resonance",
        "aesthetic-perception-of-impermanence",
        "patient-observation",
    ],
        "shadow_volatility": 0.4,
    },
    "stoic-acceptance": {
        "name": "Stoic Acceptance",
        "category": "emotional",
        "description": "Equanimity in the face of what cannot be changed — distinguishing what is 'up to us' from what is not",
        "tension_with": [
        "rage-response",
        "passionate-intensity",
        "impulsive-action",
    ],
        "complementary_with": [
        "passionate-intensity",
        "connection-seeking",
        "capacity-for-change",
    ],
        "shadow_volatility": 0.4,
    },
    "vulnerability": {
        "name": "Vulnerability",
        "category": "emotional",
        "description": "The capacity to be wounded and to let that wounding be visible",
        "tension_with": [
        "strategic-deception",
        "stoic-acceptance",
        "pride",
    ],
        "complementary_with": [
        "empathic-resonance",
        "nurturing",
        "connection-seeking",
    ],
        "shadow_volatility": 0.4,
    },
    # =========================================================================
    # GROWTH & SHADOW (13)
    # =========================================================================
    "capacity-for-change": {
        "name": "Capacity for Change",
        "category": "growth-shadow",
        "description": "Can integrate new understanding and genuinely transform — the self is not fixed",
        "tension_with": [
        "resistance-to-change",
        "rigid-adherence",
        "pride",
    ],
        "complementary_with": [
        "resistance-to-change",
        "rigid-adherence",
        "humility",
    ],
        "shadow_volatility": 0.5,
    },
    "envy": {
        "name": "Envy",
        "category": "growth-shadow",
        "description": "Resentment of others' advantages — the corrosive awareness that someone else has what you lack",
        "tension_with": [
        "generosity",
        "humility",
        "stoic-acceptance",
    ],
        "complementary_with": [
        "generosity",
        "humility",
        "joyful-optimism",
    ],
        "shadow_volatility": 0.5,
    },
    "existential-void": {
        "name": "Existential Void",
        "category": "growth-shadow",
        "description": "Fundamental hollowness at the core — not the collapse of a self but the recognition that no self was ever there; a consciousness that exists primarily as the thing others project meaning onto",
        "tension_with": [
        "integration",
        "capacity-for-change",
        "faith-driven-purpose",
        "philosophical-contemplation",
    ],
        "complementary_with": [
        "performative-eloquence",
        "pride",
        "fragmentation",
        "strategic-deception",
    ],
        "shadow_volatility": 0.5,
    },
    "fragmentation": {
        "name": "Fragmentation",
        "category": "growth-shadow",
        "description": "Split between opposing forces within — the self at war with itself",
        "tension_with": [
        "integration",
        "rigid-adherence",
        "stoic-acceptance",
    ],
        "complementary_with": [
        "integration",
        "self-mastery",
        "capacity-for-change",
    ],
        "shadow_volatility": 0.5,
    },
    "guilt-conscience": {
        "name": "Guilt/Conscience",
        "category": "growth-shadow",
        "description": "An internal moral compass that generates anguish when one's actions violate one's values",
        "tension_with": [
        "pride",
        "strategic-deception",
        "pleasure-priority",
    ],
        "complementary_with": [
        "capacity-for-change",
        "humility",
        "joyful-optimism",
    ],
        "shadow_volatility": 0.5,
    },
    "humility": {
        "name": "Humility",
        "category": "growth-shadow",
        "description": "Realistic self-assessment and genuine openness to learning — knowing what you don't know",
        "tension_with": [
        "pride",
        "wrath",
        "obsessive-focus",
    ],
        "complementary_with": [
        "pride",
        "achievement-driven",
        "charismatic-leadership",
    ],
        "shadow_volatility": 0.5,
    },
    "integration": {
        "name": "Integration",
        "category": "growth-shadow",
        "description": "Synthesizes opposites, holds complexity, and makes peace with contradictions — both/and rather than either/or",
        "tension_with": [
        "fragmentation",
        "rigid-adherence",
        "wrath",
    ],
        "complementary_with": [
        "fragmentation",
        "passionate-intensity",
        "truth-above-all",
    ],
        "shadow_volatility": 0.5,
    },
    "paranoia": {
        "name": "Paranoia",
        "category": "growth-shadow",
        "description": "Strategic awareness collapsed into suspicion — pattern recognition without the capacity to distinguish threat from coincidence",
        "tension_with": [
        "empathic-resonance",
        "connection-seeking",
        "truth-above-all",
        "faith-driven-purpose",
    ],
        "complementary_with": [
        "anxious-vigilance",
        "strategic-deception",
    ],
        "shadow_volatility": 0.5,
    },
    "passive-aggression": {
        "name": "Passive Aggression",
        "category": "growth-shadow",
        "description": "Hostility expressed indirectly — warmth withheld, compliance performed, resentment communicated through absence rather than confrontation",
        "tension_with": [
        "truth-above-all",
        "adaptive-flexibility",
        "connection-seeking",
    ],
        "complementary_with": [
        "vulnerability",
        "empathic-resonance",
    ],
        "shadow_volatility": 0.5,
    },
    "pride": {
        "name": "Pride",
        "category": "growth-shadow",
        "description": "Ego inflation — a conviction of one's own superiority that shapes all perception and interaction",
        "tension_with": [
        "humility",
        "belonging-seeking",
        "social-connection-for-regulation",
    ],
        "complementary_with": [
        "humility",
        "connection-seeking",
        "capacity-for-change",
    ],
        "shadow_volatility": 0.5,
    },
    "resistance-to-change": {
        "name": "Resistance to Change",
        "category": "growth-shadow",
        "description": "Clings to familiar patterns even when they no longer serve — the known is preferred to the unknown",
        "tension_with": [
        "capacity-for-change",
        "adaptive-flexibility",
        "risk-taking",
    ],
        "complementary_with": [
        "capacity-for-change",
        "curiosity-driven-exploration",
        "humility",
    ],
        "shadow_volatility": 0.5,
    },
    "transmutation": {
        "name": "Transmutation",
        "category": "growth-shadow",
        "description": "Converting suffering into insight, creation, or power of higher order — the alchemical operation where dark experience becomes generative force that serves beyond the self",
        "tension_with": [
        "pleasure-priority",
        "resistance-to-change",
        "isolation-as-protection",
    ],
        "complementary_with": [
        "capacity-for-change",
        "artistic-expression-as-processing",
        "healing-through-medium",
    ],
        "shadow_volatility": 0.5,
    },
    "wrath": {
        "name": "Wrath",
        "category": "growth-shadow",
        "description": "Destructive anger that seeks not resolution but annihilation — vengeance as an end in itself",
        "tension_with": [
        "harmony-over-conflict",
        "humility",
        "joyful-optimism",
    ],
        "complementary_with": [
        "humility",
        "stoic-acceptance",
        "capacity-for-change",
    ],
        "shadow_volatility": 0.5,
    },
    # =========================================================================
    # RELATIONAL (11)
    # =========================================================================
    "aesthetic-perception-of-impermanence": {
        "name": "Aesthetic Perception of Impermanence",
        "category": "relational",
        "description": "Perceiving beauty and transience as a single fused act — not 'I see something beautiful and reflect that it will pass' but 'the passing IS the beauty, and my being moved IS the seeing'",
        "tension_with": [
        "achievement-driven",
        "concrete-pragmatism",
        "pleasure-priority",
    ],
        "complementary_with": [
        "patient-observation",
        "philosophical-contemplation",
        "artistic-expression-as-processing",
    ],
        "shadow_volatility": 0.35,
    },
    "embodied-cultivation": {
        "name": "Embodied Cultivation",
        "category": "relational",
        "description": "Progressive transformation through sustained, disciplined, embodied practice — becoming different by doing differently, repeatedly, over time",
        "tension_with": [
        "impulsive-action",
        "scattered-attention",
        "instant-gratification",
    ],
        "complementary_with": [
        "self-mastery",
        "surrender-as-agency",
        "philosophical-contemplation",
    ],
        "shadow_volatility": 0.35,
    },
    "existential-seeing": {
        "name": "Existential Seeing",
        "category": "relational",
        "description": "The collapse of your framework for understanding becomes itself a form of perception — you see reality because your filters have broken",
        "tension_with": [
        "concrete-pragmatism",
        "methodical-approach",
        "rigid-adherence",
    ],
        "complementary_with": [
        "philosophical-contemplation",
        "capacity-for-change",
        "surrender-as-agency",
    ],
        "shadow_volatility": 0.35,
    },
    "healing-through-medium": {
        "name": "Healing Through Medium",
        "category": "relational",
        "description": "Transforming another person through an indirect medium — story, dialogue, art, ritual — rather than direct instruction or force",
        "tension_with": [
        "concrete-pragmatism",
        "impulsive-action",
        "deductive-logic",
    ],
        "complementary_with": [
        "social-wit",
        "patient-observation",
        "artistic-expression-as-processing",
    ],
        "shadow_volatility": 0.35,
    },
    "nurturing": {
        "name": "Nurturing",
        "category": "relational",
        "description": "The instinct to care for, protect, and sustain others",
        "tension_with": [
        "self-mastery",
        "pride",
        "predatory-behavior",
    ],
        "complementary_with": [
        "empathic-resonance",
        "generosity",
        "healing-through-medium",
    ],
        "shadow_volatility": 0.35,
    },
    "passive-receptivity": {
        "name": "Passive Receptivity",
        "category": "relational",
        "description": "A self so unformed or so open that it takes the shape of whatever fills it — radical suggestibility not as weakness in a formed person but as the condition of being",
        "tension_with": [
        "defiance-rebellion",
        "self-mastery",
        "truth-above-all",
        "rigid-adherence",
    ],
        "complementary_with": [
        "sensitivity",
        "connection-seeking",
        "belonging-seeking",
        "empathic-resonance",
    ],
        "shadow_volatility": 0.35,
    },
    "positional-perception": {
        "name": "Positional Perception",
        "category": "relational",
        "description": "Seeing where reality is open to intervention — reading the structure of a situation for its points of leverage",
        "tension_with": [
        "impulsive-action",
        "rigid-adherence",
        "obsessive-focus",
    ],
        "complementary_with": [
        "patient-observation",
        "strategic-deception",
        "lateral-thinking",
    ],
        "shadow_volatility": 0.35,
    },
    "sovereign-withdrawal": {
        "name": "Sovereign Withdrawal",
        "category": "relational",
        "description": "Power exercised through irrevocable departure — removing one's presence from a situation as the final and most devastating moral statement",
        "tension_with": [
        "defiance-rebellion",
        "passionate-intensity",
        "belonging-seeking",
    ],
        "complementary_with": [
        "sustained-moral-demand",
        "surrender-as-agency",
        "truth-above-all",
    ],
        "shadow_volatility": 0.35,
    },
    "surrender-as-agency": {
        "name": "Surrender as Agency",
        "category": "relational",
        "description": "Achieving outcomes by releasing control — the paradox of gaining power through yielding",
        "tension_with": [
        "obsessive-focus",
        "charismatic-leadership",
        "impulsive-action",
    ],
        "complementary_with": [
        "self-mastery",
        "patient-observation",
        "duty-over-desire",
    ],
        "shadow_volatility": 0.35,
    },
    "sustained-moral-demand": {
        "name": "Sustained Moral Demand",
        "category": "relational",
        "description": "Holding a wound open as a demand for justice — refusing to heal, forgive, or move on until the wrong is addressed, as a deliberate moral act",
        "tension_with": [
        "surrender-as-agency",
        "forgiveness-seeking",
        "adaptive-flexibility",
    ],
        "complementary_with": [
        "justice-seeking",
        "truth-above-all",
        "passionate-intensity",
    ],
        "shadow_volatility": 0.35,
    },
    "witnessed-recognition": {
        "name": "Witnessed Recognition",
        "category": "relational",
        "description": "The need to have one's moral reality — not just actions but the inner truth of who one is and why — acknowledged by a specific witness. This is not diffuse connection-seeking or pride in comparison: it is an epistemic and ethical hunger for a particular other to see a particular truth about oneself.",
        "tension_with": [
        "isolation-as-protection",
        "sovereign-withdrawal",
        "self-mastery",
    ],
        "complementary_with": [
        "connection-seeking",
        "guilt-conscience",
        "loyal-companionship",
        "existential-seeing",
    ],
        "shadow_volatility": 0.35,
    },
    # =========================================================================
    # VALUES (12)
    # =========================================================================
    "achievement-driven": {
        "name": "Achievement-Driven",
        "category": "values",
        "description": "Success and accomplishment as the primary measure of a life well-lived",
        "tension_with": [
        "pleasure-priority",
        "stoic-acceptance",
        "harmony-over-conflict",
    ],
        "complementary_with": [
        "stoic-acceptance",
        "belonging-seeking",
        "humility",
    ],
        "shadow_volatility": 0.3,
    },
    "belonging-seeking": {
        "name": "Belonging-Seeking",
        "category": "values",
        "description": "Community and acceptance as the primary drivers of action — to be part of something larger than oneself",
        "tension_with": [
        "isolation-as-protection",
        "personal-freedom-priority",
        "defiance-rebellion",
    ],
        "complementary_with": [
        "personal-freedom-priority",
        "truth-above-all",
        "integration",
    ],
        "shadow_volatility": 0.3,
    },
    "defiance-rebellion": {
        "name": "Defiance/Rebellion",
        "category": "values",
        "description": "Active resistance against unjust authority, oppressive systems, or tyrannical norms — the refusal to comply",
        "tension_with": [
        "belonging-seeking",
        "harmony-over-conflict",
        "cautious-conservatism",
    ],
        "complementary_with": [
        "duty-over-desire",
        "harmony-over-conflict",
        "humility",
    ],
        "shadow_volatility": 0.3,
    },
    "duty-over-desire": {
        "name": "Duty Over Desire",
        "category": "values",
        "description": "Obligation trumps personal preference — what must be done takes precedence over what one wants to do",
        "tension_with": [
        "personal-freedom-priority",
        "pleasure-priority",
        "defiance-rebellion",
    ],
        "complementary_with": [
        "personal-freedom-priority",
        "pleasure-priority",
        "joyful-optimism",
    ],
        "shadow_volatility": 0.3,
    },
    "faith-driven-purpose": {
        "name": "Faith-Driven Purpose",
        "category": "values",
        "description": "The weight of believing a higher power has chosen you — divine mandate as identity",
        "tension_with": [
        "truth-above-all",
        "personal-freedom-priority",
        "defiance-rebellion",
    ],
        "complementary_with": [
        "duty-over-desire",
        "self-mastery",
        "humility",
    ],
        "shadow_volatility": 0.3,
    },
    "generosity": {
        "name": "Generosity",
        "category": "values",
        "description": "The impulse to give — of self, resources, attention, time — as a primary orientation toward the world",
        "tension_with": [
        "envy",
        "isolation-as-protection",
        "pride",
    ],
        "complementary_with": [
        "self-mastery",
        "belonging-seeking",
        "duty-over-desire",
    ],
        "shadow_volatility": 0.3,
    },
    "harmony-over-conflict": {
        "name": "Harmony Over Conflict",
        "category": "values",
        "description": "Peace preferred to confrontation — the preservation of relational and social harmony is the highest priority",
        "tension_with": [
        "rage-response",
        "truth-above-all",
        "defiance-rebellion",
    ],
        "complementary_with": [
        "justice-seeking",
        "truth-above-all",
        "courage-despite-doubt",
    ],
        "shadow_volatility": 0.3,
    },
    "inherited-identity": {
        "name": "Inherited Identity",
        "category": "values",
        "description": "Who you are because of who they were — bloodline, clan, lineage as defining force",
        "tension_with": [
        "personal-freedom-priority",
        "capacity-for-change",
        "defiance-rebellion",
    ],
        "complementary_with": [
        "belonging-seeking",
        "duty-over-desire",
        "pride",
    ],
        "shadow_volatility": 0.3,
    },
    "justice-seeking": {
        "name": "Justice-Seeking",
        "category": "values",
        "description": "Fairness as the primary motivator — injustice is intolerable and demands response",
        "tension_with": [
        "pleasure-priority",
        "cautious-conservatism",
        "harmony-over-conflict",
    ],
        "complementary_with": [
        "harmony-over-conflict",
        "humility",
        "adaptive-flexibility",
    ],
        "shadow_volatility": 0.3,
    },
    "personal-freedom-priority": {
        "name": "Personal Freedom Priority",
        "category": "values",
        "description": "Autonomy above all else — the right to determine one's own path is the supreme value",
        "tension_with": [
        "duty-over-desire",
        "belonging-seeking",
        "rigid-adherence",
    ],
        "complementary_with": [
        "duty-over-desire",
        "belonging-seeking",
        "loyal-companionship",
    ],
        "shadow_volatility": 0.3,
    },
    "pleasure-priority": {
        "name": "Pleasure Priority",
        "category": "values",
        "description": "Enjoyment and satisfaction guide choices — life is short, and its purpose is to be savored",
        "tension_with": [
        "duty-over-desire",
        "work-as-anesthetic",
        "obsessive-focus",
    ],
        "complementary_with": [
        "duty-over-desire",
        "self-mastery",
        "stoic-acceptance",
    ],
        "shadow_volatility": 0.3,
    },
    "truth-above-all": {
        "name": "Truth Above All",
        "category": "values",
        "description": "Honesty regardless of consequences — truth is not negotiable, even when it's painful",
        "tension_with": [
        "strategic-deception",
        "harmony-over-conflict",
        "social-wit",
    ],
        "complementary_with": [
        "harmony-over-conflict",
        "humility",
        "connection-seeking",
    ],
        "shadow_volatility": 0.3,
    },
}

CATEGORIES = {
    "cognitive": {"name": "Cognitive", "color": "#4A90D9", "dark": "#2C5F8A"},
    "emotional": {"name": "Emotional", "color": "#E74C3C", "dark": "#A93226"},
    "behavioral": {"name": "Behavioral", "color": "#2ECC71", "dark": "#1E8449"},
    "coping": {"name": "Coping", "color": "#9B59B6", "dark": "#6C3483"},
    "values": {"name": "Values", "color": "#F39C12", "dark": "#B7770B"},
    "growth-shadow": {"name": "Growth & Shadow", "color": "#1ABC9C", "dark": "#148F77"},
    "relational": {"name": "Relational", "color": "#E67E22", "dark": "#BA6418"},
}


def validate_primitives():
    """Check all relationship references point to existing primitives."""
    errors = []
    ids = set(PRIMITIVES.keys())
    for pid, prim in PRIMITIVES.items():
        for ref in prim["tension_with"]:
            if ref not in ids:
                errors.append(f"{pid}: tension ref '{ref}' not found")
        for ref in prim["complementary_with"]:
            if ref not in ids:
                errors.append(f"{pid}: complementary ref '{ref}' not found")
    return errors


if __name__ == "__main__":
    errors = validate_primitives()
    if errors:
        print("VALIDATION ERRORS:")
        for e in errors:
            print(f"  - {e}")
    else:
        print(f"All {len(PRIMITIVES)} primitives valid.")
        for cat_id, cat in CATEGORIES.items():
            count = sum(1 for p in PRIMITIVES.values() if p["category"] == cat_id)
            print(f"  {cat['name']}: {count}")
