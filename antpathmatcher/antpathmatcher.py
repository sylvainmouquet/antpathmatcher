import re
from typing import Literal


from loguru import logger


class AntPathMatcher:
    """
    Python implementation of Ant-style path patterns.

    References:
    - https://github.com/Mach-II/Mach-II-Framework/wiki/ANT-Style-Pattern-Matcher#Wildcards
    - https://docs.spring.io/spring-framework/docs/5.1.6.RELEASE_to_5.2.0.M1/Spring%20Framework%205.1.6.RELEASE/org/springframework/util/AntPathMatcher.html

    Supports wildcards:
    - ? - matches exactly one character (except path separators)
    - * - matches zero or more characters (except path separators)
    - ** - matches zero or more directories in a path
    """

    def __init__(self, path_separator: str | Literal["/"] = "/"):
        """
        Initialize an AntPathMatcher with a configurable path separator.

        The AntPathMatcher provides pattern matching functionality based on Ant-style path patterns.
        By default, it uses '/' as the path separator, which is common for URL and file paths.
        However, this can be configured to use different separators for custom needs.

        Args:
            path_separator: The character to use as path separator. Defaults to "/".
                           This impacts how wildcards and path variables are matched.

        Examples:
            - AntPathMatcher() - Creates a matcher using '/' as the path separator
            - AntPathMatcher(path_separator=".") - Creates a matcher using '.' as the
              path separator, useful for matching package names or domain names
        """
        self.path_separator = path_separator
        # Escape the path separator for safe use in regular expressions
        self.path_separator_slug = re.escape(path_separator)

    def _prepare_pattern_regex(self, pattern: str) -> str:
        """
        Convert an Ant-style pattern to a regular expression pattern.

        This internal method transforms Ant-style pattern syntax into equivalent
        regex patterns that can be used with Python's re module. It handles
        special Ant pattern characters including:

        - ? → matches a single character except path separator
        - * → matches zero or more characters except path separator
        - ** → matches zero or more directories/path segments

        The method uses temporary placeholders during conversion to avoid
        interference between replacements.

        Args:
            pattern: The Ant-style pattern to convert

        Returns:
            str: A regular expression equivalent of the input pattern

        Example:
            Input: "/users/*/profile"
            Output: "\\/users\\/[^/]*?\\/profile"
        """
        pattern_regex = pattern.strip()

        # First replace regex special characters and Ant pattern characters with placeholders
        pattern_regex = pattern_regex.replace(f"**{self.path_separator}", "__DOUBLE_STAR_SLASH__")
        pattern_regex = pattern_regex.replace(
            f"**", "__DOUBLE_STAR_SLASH__"
        )
        pattern_regex = pattern_regex.replace("?", "__QUESTION_MARK__")
        pattern_regex = pattern_regex.replace("*", "__SINGLE_STAR__")

        # all {variables} are interpreted like single *
        pattern_regex = re.sub(r"{[^}]+}", "__SINGLE_STAR__", pattern_regex)

        logger.debug(f"first pattern replacement = {pattern_regex}")

        # Then convert placeholders to their regex equivalents
        pattern_regex = pattern_regex.replace("__DOUBLE_STAR_SLASH__", ".*")
        pattern_regex = pattern_regex.replace(
            "__QUESTION_MARK__", f"[^{self.path_separator_slug}]"
        )
        pattern_regex = pattern_regex.replace(
            "__SINGLE_STAR__", f"[^{self.path_separator_slug}]*?"
        )
        logger.debug(f"second pattern replacement = {pattern_regex}")
        return pattern_regex

    def match(self, pattern: str, path: str) -> bool:
        """
        Match a path against an Ant-style pattern.

        This method checks if the given path matches the specified Ant-style pattern.
        Ant-style patterns support these special characters

        Args:
            pattern: The Ant-style pattern to match against
            path: The path to be matched

        Returns:
            bool: True if the path matches the pattern, False otherwise
        """
        pattern_regex = self._prepare_pattern_regex(pattern)

        # match checks for a match only at the beginning of the string
        # fullmatch checks for entire string to be a match
        # (cf https://docs.python.org/3/library/re.html#search-vs-match )
        is_match = re.fullmatch(pattern_regex, path) is not None
        logger.debug(f"match result : {pattern=} and {path=} is {is_match}")
        return is_match

    def extract_uri_template_variables(self, pattern: str, path: str) -> dict[str, str]:
        """
        Extract variables from a URI path based on a template pattern.

        Example:
            pattern = "/users/{user_id}/posts/{post_id}"
            path = "/users/123/posts/456"
            returns: {"user_id": "123", "post_id": "456"}

        Args:
            pattern: URI template pattern with variables in curly braces
            path: Actual URI path to extract variables from

        Returns:
            Dictionary mapping variable names to their values
        """

        # Extract variable names from pattern
        variable_names = re.findall(r"{([^}]+)}", pattern)

        if not variable_names:
            return {}

        # Create a regex pattern that captures groups for each variable
        regex_pattern = pattern
        for var_name in variable_names:
            regex_pattern = regex_pattern.replace(f"{{{var_name}}}", "([^/]+)")

        # Match the path against the pattern
        match = re.match(regex_pattern, path)

        if not match:
            logger.debug(f"extract : No match found for {pattern=} and {path=}")
            return {}

        # Create a dictionary mapping variable names to their values
        result = {}
        for i, var_name in enumerate(variable_names):
            result[var_name] = match.group(i + 1)

        logger.debug(f"extract : result: {pattern=} and {path=} is {result}")
        return result
