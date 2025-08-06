# Security Policy

## Supported Versions

We release patches for security vulnerabilities. Currently supported versions:

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of Aircraft Go-Around Tracker seriously. If you discover a
security vulnerability, please follow these steps:

### How to Report

1. **DO NOT** open a public GitHub issue for security vulnerabilities
2. Instead, please report vulnerabilities via one of these methods:
   - Open a [Security Advisory](https://github.com/challgren/aircraft-goaround/security/advisories/new) on GitHub
   - Email the maintainer directly (see profile for contact information)

### What to Include

Please include the following information in your report:

- Type of vulnerability (e.g., XSS, SQL injection, authentication bypass)
- Full paths of source file(s) related to the vulnerability
- Location of the affected source code (tag/branch/commit or direct URL)
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the vulnerability and potential attack scenarios

### What to Expect

- **Acknowledgment**: We will acknowledge receipt of your report within 48 hours
- **Assessment**: We will investigate and validate the vulnerability
- **Fix Timeline**: We aim to release patches for critical vulnerabilities within
  7 days and other vulnerabilities within 30 days
- **Disclosure**: We will coordinate disclosure with you to ensure users have
  adequate time to update

## Security Best Practices

When deploying Aircraft Go-Around Tracker:

### Network Security

- Always run behind a reverse proxy (nginx, Apache, etc.)
- Use HTTPS for all connections
- Implement rate limiting to prevent abuse
- Use firewall rules to restrict access to necessary ports only

### Docker Security

- Keep the base image updated regularly
- Run containers with minimal privileges
- Use read-only root filesystem where possible
- Limit container resources (CPU, memory)

### Data Security

- Ensure TAR1090 connections use internal networks when possible
- Regularly review and rotate any API keys or secrets
- Monitor logs for suspicious activity
- Backup detection data regularly

### Configuration Security

- Never expose the application directly to the internet
- Use strong, unique passwords for any authentication
- Keep all dependencies up to date
- Review environment variables for sensitive information

## Dependency Management

This project uses Dependabot to automatically monitor and update dependencies:

- Security updates are automatically created as pull requests
- Dependencies are checked weekly
- Critical security updates are prioritized

To manually check for vulnerabilities:

```bash
# Python dependencies
pip install safety
safety check -r requirements.txt

# Docker image scanning
docker scan ghcr.io/challgren/aircraft-goaround:latest
```

## Security Features

Aircraft Go-Around Tracker includes several security features:

- **ProxyFix middleware**: Properly handles X-Forwarded headers
- **Input validation**: All user inputs are validated
- **No database**: Reduces attack surface (no SQL injection possible)
- **Read-only operations**: Only reads from TAR1090, never writes
- **Containerized**: Isolated runtime environment
- **Health checks**: Built-in monitoring endpoints

## Contact

For security concerns, please use the methods described above.
For general questions, please [open an issue](https://github.com/challgren/aircraft-goaround/issues).

## Acknowledgments

We appreciate responsible disclosure and will acknowledge security researchers
who report vulnerabilities according to this policy.