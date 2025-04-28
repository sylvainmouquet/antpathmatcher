# AntPathMatcher

Python Implementation of the Ant-style path patterns, inspired by Spring Framework's AntPathMatcher.

## References

[Spring framework - AntPathMatcher](https://docs.spring.io/spring-framework/docs/5.1.6.RELEASE_to_5.2.0.M1/Spring%20Framework%205.1.6.RELEASE/org/springframework/util/AntPathMatcher.html)

## Features

- Match URL paths and file paths using Ant-style patterns
- Support for wildcards:
  - `?` - matches exactly one character (except path separators)
  - `*` - matches zero or more characters (except path separators)
  - `**` - matches zero or more directories in a path
- Extract variables from URI templates (e.g., `/users/{id}` matches `/users/123` with `id=123`)
- Customizable path separators (default is `/` but can be changed)
- Fully type-hinted for modern Python development
- Compatible with Python 3.10+

## Installation

```bash
pip install antpathmatcher
```

Or with uv:

```bash
uv add antpathmatcher
```

## Quick Start

### Basic Pattern Matching

```python
from antpathmatcher import AntPathMatcher

# Create a matcher with default path separator (/)
matcher = AntPathMatcher()

# Basic matching with single character wildcard
matcher.match("com/t?st.jsp", "com/test.jsp")  # True
matcher.match("com/t?st.jsp", "com/tast.jsp")  # True
matcher.match("com/t?st.jsp", "com/txst.jsp")  # True
matcher.match("com/t?st.jsp", "com/tst.jsp")   # False (? requires exactly one character)

# Matching with * wildcard (matches within a path segment)
matcher.match("com/*.jsp", "com/demo.jsp")     # True
matcher.match("com/*.jsp", "com/test.jsp")     # True
matcher.match("com/*.jsp", "com/sub/test.jsp") # False (doesn't cross path boundaries)

# Matching with ** wildcard (matches across path segments)
matcher.match("com/**/test.jsp", "com/test.jsp")           # True
matcher.match("com/**/test.jsp", "com/sub/test.jsp")       # True
matcher.match("com/**/test.jsp", "com/sub/dir/test.jsp")   # True

# Complex patterns
matcher.match("org/demo/**/*.jsp", "org/demo/views/home.jsp")           # True
matcher.match("org/demo/**/*.jsp", "org/demo/templates/views/home.jsp") # True
```

### Extracting URI Template Variables

```python
from antpathmatcher import AntPathMatcher

matcher = AntPathMatcher()

# Basic variable extraction
variables = matcher.extract_uri_template_variables("/hotels/{hotel}", "/hotels/1")
print(variables)  # {'hotel': '1'}

# Multiple variables
variables = matcher.extract_uri_template_variables(
    "/users/{user_id}/posts/{post_id}", 
    "/users/123/posts/456"
)
print(variables)  # {'user_id': '123', 'post_id': '456'}
```

### Custom Path Separators

```python
from antpathmatcher import AntPathMatcher

# Create a matcher with custom path separator
# Useful for matching things like Java package names
matcher = AntPathMatcher(path_separator=".")

# Now the patterns use dots as separators
matcher.match("com.example.*.service", "com.example.user.service")  # True
matcher.match("com.example.???.service", "com.example.api.service") # True
matcher.match("com.**.service", "com.example.module.api.service")   # True
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.