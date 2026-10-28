"""
Helper script to push commits to GitHub without requiring system Git installation.
Uses the pure-Python dulwich library.

Usage:
    python push_to_github.py
    (prompts securely for your GitHub Personal Access Token)
Or:
    python push_to_github.py <GITHUB_TOKEN>
"""

import sys
import getpass
import dulwich.porcelain as p
from dulwich.repo import Repo

REPO_URL = "https://github.com/prajanprajan1463-cloud/Fake-job-and-internship-detection-system-.git"


def main():
    if len(sys.argv) > 1:
        token = sys.argv[1].strip()
    else:
        print("==================================================")
        print(" Push Project to GitHub Repository ")
        print(" Target: " + REPO_URL)
        print("==================================================")
        print("\nGitHub requires a Personal Access Token (PAT) for write access.")
        print("If you do not have one yet:")
        print("1. Go to https://github.com/settings/tokens")
        print("2. Generate a token (classic) with 'repo' scope selected.")
        print("3. Paste the token below:\n")
        try:
            token = getpass.getpass("GitHub Personal Access Token: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nAborted.")
            sys.exit(1)

    if not token:
        print("[!] Error: No token provided.")
        sys.exit(1)

    # Clean token in case user pasted 'Bearer ' or quotes
    token = token.replace('"', '').replace("'", "").strip()
    auth_url = f"https://{token}@github.com/prajanprajan1463-cloud/Fake-job-and-internship-detection-system-.git"

    print("[*] Authenticating and pushing 'main' branch to GitHub...")
    repo = Repo('.')
    try:
        p.push(repo, auth_url, 'refs/heads/main:refs/heads/main')
        print("\n[+] SUCCESS! All files and commits have been pushed to:")
        print("    https://github.com/prajanprajan1463-cloud/Fake-job-and-internship-detection-system-")
    except Exception as e:
        print(f"\n[!] Push failed: {e}")
        print("\nCommon troubleshooting:")
        print("- Verify your token has write access to repository 'prajanprajan1463-cloud/Fake-job-and-internship-detection-system-'.")
        print("- Ensure the token has the 'repo' scope enabled.")


if __name__ == '__main__':
    main()

