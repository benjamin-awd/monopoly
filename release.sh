#!/usr/bin/env bash

if [ -z "$1" ]; then
	echo "Please provide a tag."
	echo "Usage: ./release.sh v[X.Y.Z]"
	exit
fi

echo "Preparing $1..."

# update the version
msg="# managed by release.sh"
grep -m 1 version pyproject.toml | awk -F' = ' '{print $2}' | tr -d '"'

# update the pyproject version
poetry version $1

# update the changelog
git cliff --unreleased --tag $(poetry version --short) --prepend CHANGELOG.md
git add -A -ip && git commit -m "chore(release): prepare for $1"

export GIT_CLIFF_TEMPLATE="\
	{% for group, commits in commits | group_by(attribute=\"group\") %}
	{{ group | upper_first }}\
	{% for commit in commits %}
		- {% if commit.breaking %}(breaking) {% endif %}{{ commit.message | upper_first }} ({{ commit.id | truncate(length=7, end=\"\") }})\
	{% endfor %}
	{% endfor %}"

# create a signed tag
git tag "v$1"
echo "Done!"
echo "Now push the commit (git push) and the tag (git push --tags)."
