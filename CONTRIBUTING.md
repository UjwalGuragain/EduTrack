# Contributing to EduTrack

Thanks for helping improve EduTrack.

## Workflow

1. Fork the repository.
2. Create a branch for your change.
3. Keep the work focused and scoped to one improvement at a time.
4. Add or update tests whenever behavior changes.
5. Run the relevant Django tests before opening a pull request.
6. Open a clear pull request that explains the bug fix or feature.

## Code expectations

- Follow the existing Django project structure.
- Keep templates, views, and permissions consistent with current patterns.
- Be explicit about authorization checks.
- Prefer small, readable commits over broad refactors.

## Security-sensitive changes

If you are changing access control, permission logic, or authentication behavior, include test coverage for both allowed and denied scenarios.
