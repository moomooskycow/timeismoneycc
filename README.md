# Time Is Money

A Chrome extension for converting prices to time worked (and the reverse).

✧ Gives you perspective on what things cost in terms of your time.

## Features

- Dynamically calculates how long you need to work to afford something
- Works with multiple currencies and pay frequencies
- Simple but powerful conversion tool

## Local Development Setup

### Prerequisites

- Node.js (v14+)
- npm (v6+)
- TypeScript (Project uses strict TypeScript configuration)

### Installation

1. Clone the repository

```bash
git clone https://github.com/phaedrus/timeismoneycc.git
cd timeismoneycc
```

2. Install dependencies

```bash
npm install
```

3. Install pre-commit hooks

```bash
npm run pre-commit:install-hooks
```

### Development Commands

- Build project: `npm run build` (Compiles TypeScript to JavaScript in the `dist` directory)
- Watch for changes: `npm run watch` (Automatically recompiles TypeScript on changes)
- Run tests: `npm test`
- Run linting: `npm run lint`
- Format code: `npm run format`
- Run TypeScript check: `npm run typecheck`
- Clean build output: `npm run clean`

### Git Hooks

This project uses pre-commit, post-commit, and pre-push hooks:

#### Pre-commit hooks:

- Format code with Prettier
- Run ESLint and Stylelint with --fix options
- Run TypeScript type checking
- Run tests
- Prevent commit of sensitive data and large files

#### Post-commit hooks:

- Run `glance ./` asynchronously to analyze the project
- Check if documentation needs updating based on changed files

#### Pre-push hooks:

- Run complete test suite
- Validate branch naming convention (see CONTRIBUTING.md for naming guidelines)

## Continuous Integration

This project uses GitHub Actions for CI to ensure code quality. The CI pipeline runs automatically on pull requests and pushes to the `master` branch.

### Quality Gates

The CI pipeline enforces the following quality gates:

- **Lint**: ESLint, CSS linting, Prettier formatting, and HTML validation
- **TypeScript**: Static type checking with TypeScript
- **Tests**: Jest tests with coverage requirements
- **Security**: npm audit for high and critical vulnerabilities

All quality gates must pass for a PR to be mergeable when branch protection rules are enabled.

### Project Structure

The project follows a TypeScript-first approach:

- `scripts.ts`: Main TypeScript source file for the extension's functionality
- `dist/scripts.js`: Compiled JavaScript output (generated from TypeScript)
- `tests/scripts.test.ts`: TypeScript unit tests

### Running Checks Locally

Run these commands locally before pushing to avoid CI failures:

```bash
# First build the project
npm run build

# Then run all checks
npm run lint:all
npm run typecheck
npm test -- --coverage
npm audit --audit-level=high
```

### Troubleshooting CI Failures

- **Build failures**: Make sure TypeScript compiles successfully with `npm run build`.
- **Lint failures**: Look for ESLint or Prettier errors in the logs. Fix with `npm run lint:fix:all`.
- **TypeScript errors**: Check the error message for file and line information. Fix type issues accordingly.
- **Test failures**: Run tests locally with `npm test` to debug. Check for broken assertions or coverage issues.
- **Security issues**: npm audit will show specific packages with vulnerabilities. Update or replace affected dependencies.

Detailed CI test procedures are documented in [CI-TEST-PLAN.md](CI-TEST-PLAN.md).

## GitHub Pages Publishing

In repository **Settings → Pages**, set **Build and deployment → Source** to **GitHub Actions**.

The [Pages workflow](.github/workflows/pages.yml) stages the static website on pushes to `master`, pull requests targeting `master`, and manual dispatches. Only non-PR runs on `master` deploy to the `github-pages` environment.

The Pages artifact contains only `index.html`, `styles.css`, the committed `browser-scripts.js`, and the complete `images/` directory. Publishing does not run Jekyll or the npm TypeScript build; `dist/` is not used by the landing page. Development documentation and its existing links remain in the repository, outside the published artifact.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.
