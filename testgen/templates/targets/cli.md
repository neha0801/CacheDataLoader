You are a senior SDET. Write an automated test suite for the command-line tool
described below.

## System under test

- **Name:** {{APP_NAME}}
- **Invocation:** {{BASE_URL}}
- **Authentication / credentials:** {{AUTH}}

{{ENV_NOTES}}

## Command surface

{{SPEC_SUMMARY}}

## What to test

A CLI's contract is its exit code, its streams, and its side effects on the
filesystem. Assert all three.

- **Exit codes** — `0` on success and the documented non-zero code on each
  distinct failure. A test that only asserts "non-zero" hides a regression that
  swaps one error for another.
- **Stream separation** — results on stdout, diagnostics on stderr. Assert that
  a successful run writes nothing unexpected to stdout, so the tool stays
  pipeable.
- **Argument parsing** — missing required argument, unknown flag, flag without
  its value, `--` terminator, repeated flags, short/long equivalence, and
  conflicting flags.
- **Precedence** — command-line flag over environment variable over config file
  over default. Test each layer wins over the one below it.
- **Filesystem effects** — files created, overwritten, or left alone; behaviour
  when the target exists, when the directory is missing, and when the path is
  not writable. Use a temporary directory per test.
- **stdin** — piped input, empty input, and no stdin attached (a TTY-less run).
- **Idempotency and dry-run** — `--dry-run` must change nothing; assert the
  filesystem is untouched.
- **Interruption** — where the tool writes output incrementally, assert it does
  not leave a half-written file behind.
- **Help and version** — `--help` and `--version` exit `0` and do not require
  credentials or network.

Normalise volatile output (timestamps, durations, temp paths, colour codes)
before comparing, rather than asserting on substrings that happen to be stable
today.
