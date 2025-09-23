### Guidelines for Effective AI-Assisted Development

**1. Principle: Stability and Regression Prevention First**

- **Atomic Changes:** Always make the smallest possible change that addresses the immediate issue. Large, sweeping refactors are high-risk.

- **Test Before and After:** Before making any change, run the relevant test suite to establish a baseline. After the change, run it again to confirm no regressions were introduced.

- **Isolate the Issue:** Reproduce the bug in the simplest way possible. Use debugging and logs to pinpoint the exact line or component causing the problem before writing a fix.

**2. Principle: Production Readiness as the North Star**

- **Ask: "Is this production-grade?"** Every change should be evaluated against this question. This includes:
  
  - **Error Handling:** Code should handle edge cases and failures gracefully, providing clear feedback to the user and logs for developers.
  
  - **Performance:** Be mindful of inefficient operations, especially in loops or frequent events (like UI renders).
  
  - **Security:** Never expose sensitive data, keys, or debug endpoints in production code.

- **User-Centric Design:** Prioritize features and fixes that directly impact the end-user's ability to complete their core tasks (e.g., validating annotations).

**3. Principle: Cleanliness and Organization**

- **Follow Existing Patterns:** Conform to the project's existing code style, naming conventions, and architectural patterns (e.g., repository abstraction, specific state management). Do not introduce new patterns without a compelling reason.

- **Leave No Trace:** Clean up after yourself. Remove debug logs, commented-out code, and unused functions before finalizing a change. Update related documentation.

- **Meaningful Naming:** Use clear, descriptive names for variables, functions, and commits (e.g., `fix: restore text highlighting regression` not `fixed stuff`).

**4. Principle: Documentation and Knowledge Transfer**

- **Document the "Why":** Beyond what the code does, use comments to explain *why* a non-obvious approach was taken, especially for workarounds or complex logic.

- **Update Docs Concurrently:** If you change a feature's behavior or add a new environment variable, update `ONBOARDING.md`, `CHANGELOG.md`, or `README.md` immediately as part of the same changeset.

- **Commit Message Clarity:** Write commit messages that would allow someone to understand the change without looking at the code.

**5. Principle: Token and Resource Efficiency**

- **Be Precise in Prompts:** Provide clear, specific context and instructions. The more precise the prompt, the less back-and-forth is required, saving tokens and time.

- **Leverage the Agent's Analysis:** When an agent provides a root cause analysis, trust it and direct the next steps based on that analysis rather than starting from scratch.

- **Consolidate Changes:** Batch small, related changes into a single prompt/action instead of multiple sequential requests.

**6. Best Practice: Communication and Validation**

- **Summarize and Verify:** After completing a task, provide a brief summary of what was changed, the result of tests, and explicitly state what should be verified next .

- **Flag Risks Early:** If a required fix might have unintended side effects or requires a significant refactor, communicate this risk immediately before proceeding.

- **Assume the Project will be Handed Off:** Write code and documentation for the next developer who will read it. clarity and simplicity are more valuable than cleverness.
