#!/bin/bash
set -e

handle_error() {
    # delete remote tag if it exists
    if git rev-parse $VERSION &>/dev/null; then
        git tag -d $VERSION
        git push origin :refs/tags/$VERSION
    fi

    # if last commit was the release commit, reset to the commit before that
    if [ "$(git log -1 --pretty=%B)" == "chore: release $VERSION" ]; then
        git reset --hard HEAD~1
        git push origin $BRANCH --force
    fi

    echo "🛑 An error occurred. Changes reverted"
    exit 1
}

# check if gh is installed
if ! command -v gh &>/dev/null; then
    echo "🛑 GitHub CLI (gh) is required to create a release"
    exit 1
fi

# ensure gh is logged in
if ! gh auth status &>/dev/null; then
    echo "🛑 You must be logged in to GitHub to create a release"
    exit 1
fi

BRANCH=$(git branch --show-current)
COMMIT=$(git rev-parse HEAD)

if [ "$BRANCH" != "main" ]; then
    echo "🛑 You must be on the main branch to release a new version"
    exit 1
fi

# check that $1 is in `major`, `minor`, or `patch`
if [ "$1" != "major" ] && [ "$1" != "minor" ] && [ "$1" != "patch" ]; then
    echo "🛑 Invalid argument: $1"
    echo "👉 Usage: release.sh [major|minor|patch] [--dry-run] [--ci]"
    exit 1
fi

# check if there are any uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "🛑 You have uncommitted changes. Please commit or stash them before releasing a new version"
    exit 1
fi

DRY_RUN=false
# set to true to disable interactive prompts
CI=false

for arg in "$@"; do
    if [ "$arg" == "--dry-run" ]; then
        DRY_RUN=true
    elif [ "$arg" == "--ci" ]; then
        CI=true
    fi
done

# Bump version
uv version --bump $1

VERSION=$(uv version --short)

# get changelog for this version
CHANGELOG=$(uv run cz changelog --dry-run --increment)

# remove first line of changelog (the version header)
CHANGELOG=$(echo "$CHANGELOG" | sed '1d')

echo "📝 Changelog for version $VERSION"
echo "$CHANGELOG"

if [ "$DRY_RUN" = true ]; then
    echo "🚨 Dry run complete. No changes made"

    exit 0
fi

# confirm release
if [ "$CI" = false ]; then
    read -p "🚀 Release version $VERSION? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "🛑 Release cancelled"
        exit 1
    fi
fi

echo "🚀 Releasing version $VERSION"

# handle errors to revert changes
trap handle_error ERR

# add all changes
git add .

# commit changes
git commit -m "chore: release $VERSION"

# tag the version
git tag $VERSION

# update CHANGELOG.md (needs to be done after tagging the version)
uv run cz changelog

# add CHANGELOG.md
git add CHANGELOG.md

# add changes to the previous commit
git commit --amend --no-edit

# amend changes the commmit hash, so we need to remove the old tag
git tag -d $VERSION

# tag the version again
git tag $VERSION

# push changes
git push origin $BRANCH

# push tags
git push origin $VERSION

# Create a new release on GitHub
gh release create "$VERSION" --title "Release $VERSION" --notes "$CHANGELOG"

echo "🎉 Released version $VERSION on GitHub"