import base64
import subprocess
import json
import sys


def run_gh(*args, stdin_data=None):
    cmd = ["gh", "api", f"repos/rfsee/M-ThreadsMonitor/{args[0]}"] + list(args[1:])
    result = subprocess.run(
        cmd, input=stdin_data, capture_output=True, text=True, timeout=30,
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return None
    return result.stdout.strip()


def main():
    workflow_content = """name: Daily Threads Monitor
on:
  schedule:
    - cron: "0 1 * * *"
  workflow_dispatch:
permissions:
  contents: write
jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: pip
      - name: Install deps
        run: |
          pip install -r requirements.txt
          pip install lxml
      - name: Run scraper
        run: python -m threads_monitor.main run
        continue-on-error: true
      - name: Build static HTML
        run: python -m threads_monitor.build_static
      - name: Deploy to Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./docs
          publish_branch: gh-pages
          force_orphan: true
"""

    encoded = base64.b64encode(workflow_content.encode()).decode()

    out = run_gh("git/refs/heads/main", "-q", ".object.sha")
    if not out:
        print("Failed to get main SHA")
        return
    main_sha = out.strip()

    out = run_gh(f"git/commits/{main_sha}", "-q", ".tree.sha")
    if not out:
        print("Failed to get tree SHA")
        return
    base_tree = out.strip()

    blob_result = run_gh(
        "git/blobs",
        "-f", f"content={encoded}",
        "-F", "encoding=base64",
        "-q", ".sha",
    )
    if not blob_result:
        print("Failed to create blob")
        return
    blob_sha = blob_result.strip()
    print(f"Blob: {blob_sha}")

    tree_payload = json.dumps({
        "base_tree": base_tree,
        "tree": [
            {"path": ".github/workflows/daily-update.yml", "mode": "100644",
             "type": "blob", "sha": blob_sha},
            {"path": "daily-update.yml", "mode": "100644",
             "type": "blob", "sha": "e69de29bb2d1d6434b8b29ae775ad8c2e48c5391",
             },
        ],
    })

    out = run_gh("git/trees", "--input", "-", stdin_data=tree_payload)
    if not out:
        print("Failed to create tree")
        print(f"Payload was: {tree_payload[:200]}...")
        return
    tree_result = json.loads(out)
    new_tree_sha = tree_result.get("sha")
    print(f"Tree: {new_tree_sha}")

    commit_payload = json.dumps({
        "message": "fix: move workflow to .github/workflows/ and delete root file",
        "tree": new_tree_sha,
        "parents": [main_sha],
    })
    out = run_gh("git/commits", "--input", "-", stdin_data=commit_payload)
    if not out:
        print("Failed to create commit")
        return
    commit = json.loads(out)
    commit_sha = commit.get("sha")
    print(f"Commit: {commit_sha}")

    out = run_gh(
        "git/refs/heads/main",
        "--method", "PATCH",
        "--input", "-",
        stdin_data=json.dumps({"sha": commit_sha, "force": True}),
    )
    if out:
        print("Success! Workflow file created at .github/workflows/daily-update.yml")
    else:
        print("Failed to update ref")


if __name__ == "__main__":
    main()
