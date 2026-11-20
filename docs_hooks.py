import re

REPO_URL = "https://github.com/TUDelftGeodesy/caroline/blob/main"

LINK_PATTERN = re.compile(r"(?P<prefix>!?\[[^\]]*\]\()" r"(?P<path>\.\./[^)\s]+)" r"(?P<suffix>\))")


def github_slugify(value, separator):
    """Unify labels with underscores between GitHub and mkdocs label management."""
    value = re.sub(r"[^\w\- ]", "", value.lower())
    value = value.replace("_", "")
    return re.sub(r"\s+", separator, value)


def on_page_markdown(markdown, page, config, files):
    """Allow docs to access files outside docs folder in mkdocs environment by replacing them with hard links."""

    def replace_link(match):
        path = match.group("path")

        # Resolve relative to the Markdown file's location.
        from pathlib import PurePosixPath

        source = PurePosixPath("docs") / page.file.src_path
        parts = []

        for part in (source.parent / path).parts:
            if part == "..":
                if parts:
                    parts.pop()
            elif part != ".":
                parts.append(part)

        resolved = "/".join(parts)

        # Only rewrite links that point outside docs/.
        if resolved.startswith("docs/"):
            return match.group(0)

        return match.group("prefix") + f"{REPO_URL}/{resolved}" + match.group("suffix")

    return LINK_PATTERN.sub(replace_link, markdown)
