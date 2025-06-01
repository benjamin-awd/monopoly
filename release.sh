#!/usr/bin/env bash

if [ -z "$1" ]; then
	echo "Please provide a tag."
	echo "Usage: ./release.sh v[X.Y.Z]"
	exit
fi

new_version=$1
echo "Preparing $new_version..."

# update the version
msg="# managed by release.sh"

# update the pyproject version
uv version $new_version

# build the latest version
uv build

# update the changelog
git cliff --unreleased --tag $(uv version --short) --prepend CHANGELOG.md
git add -A -ip && git commit -m "chore(release): prepare for $new_version"

export GIT_CLIFF_TEMPLATE="\
	{% for group, commits in commits | group_by(attribute=\"group\") %}
	{{ group | upper_first }}\
	{% for commit in commits %}
		- {% if commit.breaking %}(breaking) {% endif %}{{ commit.message | upper_first }} ({{ commit.id | truncate(length=7, end=\"\") }})\
	{% endfor %}
	{% endfor %}"

# create a signed tag
git tag "v$new_version"
echo "Done!"
echo "Now push the commit (git push) and the tag (git push --tags)."
