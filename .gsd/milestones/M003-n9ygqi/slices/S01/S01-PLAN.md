# S01: fal Visual Card Client and Tests

**Goal:** Implement the fal.ai visual generation client with a circuit breaker, mock it in pytest, and ensure it correctly handles generation and errors.
**Demo:** Mocked fal client tests pass, validating circuit breaking and basic API interaction.

## Must-Haves

- Mocked tests for the fal client pass
- Circuit breaking handles API key absence, timeouts, and failures gracefully

## Proof Level

- This slice proves: tests

## Integration Closure

S01 provides the tested fal client that S02 will call.

## Verification

- fal API calls are logged; circuit breaker trips and errors are recorded for visibility.

## Tasks

- [x] **T01: Create robust fal client** `est:1h`
  Create the base fal client structure in `backend/tools/fal_client.py` incorporating a circuit breaker. Ensure it degrades gracefully on timeouts or empty API keys.
  - Files: `backend/tools/fal_client.py`
  - Verify: Run python syntax check and linter on the file.

- [x] **T02: Write mocked fal client tests** `est:1h`
  Write mocked pytest tests in `backend/tests/test_fal_client.py` to validate successful generation, timeout behavior, and empty API key fallback.
  - Files: `backend/tests/test_fal_client.py`
  - Verify: `uv run pytest backend/tests/test_fal_client.py`

## Files Likely Touched

- backend/tools/fal_client.py
- backend/tests/test_fal_client.py
