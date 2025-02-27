import os
from git import Repo, GitCommandError

# Set your GitHub token in the environment (adjust as needed)


# Define the path to your local repository
repo_path = '/content/drive/MyDrive/Colab Notebooks/commissie_scraper'

try:
    repo = Repo(repo_path)
except Exception as e:
    print(f"Error accessing repository at {repo_path}: {e}")
    exit(1)

# If in a detached HEAD state, force-checkout a branch that tracks origin/master.
if repo.head.is_detached:
    print("Detached HEAD detected. Checking out the 'master' branch...")
    try:
        # The '-B' flag creates/resets the branch 'master' and checks it out,
        # setting it to match origin/master.
        repo.git.checkout('-B', 'master', 'origin/master')
        print("Checked out branch 'master' from 'origin/master'.")
    except GitCommandError as e:
        print(f"Error checking out branch 'master': {e}")
        exit(1)

# Fetch remote changes
try:
    repo.remote(name='origin').fetch()
    print("Fetched remote changes.")
except GitCommandError as e:
    print(f"Error fetching remote changes: {e}")

# Pull remote changes with an explicit merge strategy (--no-rebase)
try:
    repo.git.pull('--no-rebase', 'origin', 'master')
    print("Pulled remote changes using merge (--no-rebase).")
except GitCommandError as e:
    print(f"Error pulling remote changes: {e}")

# Stage all local changes (new, modified, and deleted files)
repo.git.add(all=True)

# Commit local changes if there are any modifications
if repo.is_dirty(untracked_files=True):
    try:
        commit_message = "Sync: merging local changes with remote updates"
        repo.index.commit(commit_message)
        print("Committed local changes.")
    except GitCommandError as e:
        print(f"Error committing changes: {e}")
else:
    print("No local changes to commit.")

# Push the combined commits to the remote repository
try:
    repo.git.push('origin', 'master')
    print("Pushed local commits to remote.")
except GitCommandError as e:
    print(f"Error pushing changes: {e}")