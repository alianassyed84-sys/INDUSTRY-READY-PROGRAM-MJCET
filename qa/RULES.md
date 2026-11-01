1. EVIDENCE ONLY. Every claim cites a file path + line, a command + its real output, or a screenshot. If you did not read or run it, write NOT VERIFIED. Never assume a file, function, table, route, field or value exists: open it first.
2. Status for every item: PASS (needs evidence) / FAIL / PARTIAL / BLOCKED / NOT TESTED / UNKNOWN.
3. DO NOT change code, tests, config or data while testing. Read, run, report. Never delete or loosen a test. Never add fallback values or fake data.
4. Expected results come from SPEC.md or from hand calculation written down BEFORE running the code. Never copy expected values from the code's own output.
5. If you cannot run something, write BLOCKED and say why. Never simulate its output.
6. Never print secrets, tokens or .env values. Never write to production.
7. Log every result in qa/TEST_LOG.md. Failure template: Feature | File/endpoint | Steps | Expected | Actual | Error | Root cause (established or "unknown") | Severity | Suggested fix | Retest.
8. When the task ends, stop and wait for me.
