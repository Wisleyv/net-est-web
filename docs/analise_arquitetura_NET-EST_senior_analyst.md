# NET-EST Architecture Review - Senior Systems Analyst

## 1. Project Purpose and Main Goal

The NET-EST system analyzes intralingual translation, focusing on text simplification strategies. Its main objectives are:
- Align source and target texts at the discourse (paragraph) level
- Extract features and classify simplification strategies using tags (e.g., `[OM+]`, `[SL+]`, `[RF+]`)
- Enable human-in-the-loop validation and correction
- Capture feedback for future ML model training
- Provide transparent, interpretable results and exportable reports

## 2. Tag Annotation Flow

- Tags are applied to the target text based on analysis of aligned paragraph pairs and unaligned source paragraphs.
- User configuration determines which tags are active and their weights, influencing the evidence score for each tag.
- Features extracted include word reduction, readability change, lexical density, and complexity of key nouns/verbs (using spaCy and TF-IDF).
- Heuristic rule engine combines feature thresholds and tag weights to assign tags with confidence scores.
- Manual corrections are captured via UI interactions and stored for future system improvement.

## 3. Successes of the Current System

- Discourse-first alignment: Paragraph-level matching is robust for simplification analysis.
- Modular design: Each module is independently testable and replaceable.
- Human-in-the-loop: Designed for expert validation, not as a black box.
- Feature transparency: System can explain its decisions via feature evidence.
- Feedback loop: Corrections are stored for future ML training, ensuring system evolution.
- Configurable analysis: Users control which tags are active and their influence.

## 4. Potential Issues and Limitations

- Alignment accuracy: Paragraph-level alignment may fail if source and target texts are structurally very different (e.g., merged/split paragraphs).
- Feature extraction granularity: Sampling only 5 key nouns/verbs may miss important lexical changes, especially in longer paragraphs.
- Heuristic rule engine: May not capture complex simplification strategies or feature interactions.
- Tagging edge cases: System must ensure `[PRO+]` is never generated, as per requirements.
- Scalability: For very large texts, performance and UI responsiveness may degrade.
- Feedback persistence: If deployed on ephemeral storage, feedback may be lost unless an external DB is used.
- User experience: Cold starts and slow analysis may frustrate users if not clearly communicated.

## 5. Robust Approach to Address Issues

**A. Alignment Robustness**
- Implement flexible alignment algorithms that handle paragraph splits/merges (one-to-many, many-to-one matches).
- Use similarity clustering to group related paragraphs when direct alignment fails.

**B. Feature Extraction Improvements**
- Allow dynamic sampling: For longer paragraphs, increase the number of sampled key terms.
- Use additional linguistic features: syntactic complexity, discourse markers, semantic roles.
- Consider contextual embeddings for richer feature sets.

**C. Rule Engine and Tagging**
- Make the rule engine extensible: Allow new rules/tags to be added easily.
- Implement tag exclusion logic (never output `[PRO+]`).
- Provide feature importance visualization in the UI for each tag decision.

**D. Scalability and Performance**
- Add batch processing and progress indicators for large texts.
- Warn users about expected analysis time and allow cancellation.

**E. Feedback and Knowledge Base**
- Integrate with a persistent external database for feedback storage.
- Periodically export feedback data for backup and analysis.

**F. User Experience**
- Display clear loading states and messages for cold starts and long analyses.
- Allow users to edit tags and see immediate updates in the UI.
- Provide tooltips and contextual help for all tags and features.

**G. Future-Proofing**
- Design the system so the heuristic classifier can be replaced by an ML model trained on collected feedback.
- Maintain modular interfaces for easy swapping of components.

---

## Summary

The NET-EST architecture is well-conceived for its goal of analyzing and classifying simplification strategies in intralingual translation. Its modular, discourse-first, and human-centered design is a strong foundation. To ensure robustness:
- Enhance alignment and feature extraction flexibility
- Make the rule engine extensible and transparent
- Ensure feedback is persistently stored
- Optimize for scalability and user experience

This approach will maximize the system’s accuracy, interpretability, and long-term value for both research and practical annotation workflows.
