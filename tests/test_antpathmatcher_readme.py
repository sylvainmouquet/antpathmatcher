import pytest
import logging

from antpathmatcher import AntPathMatcher
import os

# For console output
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)


@pytest.mark.asyncio
async def test_antpathmatcher_basic():

    # Create a matcher with default path separator (/)
    matcher = AntPathMatcher()

    # Basic matching with single character wildcard
    assert matcher.match("com/t?st.jsp", "com/test.jsp") is True
    assert matcher.match("com/t?st.jsp", "com/tast.jsp") is True
    assert matcher.match("com/t?st.jsp", "com/txst.jsp") is True
    assert matcher.match(
        "com/t?st.jsp", "com/tst.jsp"
    )  is False # (? requires exactly one character)

    # Matching with * wildcard (matches within a path segment)
    assert matcher.match("com/*.jsp", "com/demo.jsp")  is True
    assert matcher.match("com/*.jsp", "com/test.jsp")  is True
    assert matcher.match(
        "com/*.jsp", "com/sub/test.jsp"
    )   is False # (doesn't cross path boundaries)

    # Matching with ** wildcard (matches across path segments)
    assert matcher.match("com/**/test.jsp", "com/test.jsp")  is True
    assert matcher.match("com/**/test.jsp", "com/sub/test.jsp")  is True
    assert matcher.match("com/**/test.jsp", "com/sub/dir/test.jsp")  is True

    # Complex patterns
    assert matcher.match(
        "org/demo/**/*.jsp", "org/demo/views/home.jsp"
    )   is True
    assert matcher.match(
        "org/demo/**/*.jsp", "org/demo/templates/views/home.jsp"
    )  is True


async def test_antpathmatcher_extraction():


    matcher = AntPathMatcher()

    # Basic variable extraction
    variables = matcher.extract_uri_template_variables("/hotels/{hotel}", "/hotels/1")
    print(variables)  # {'hotel': '1'}

    # Multiple variables
    variables = matcher.extract_uri_template_variables(
        "/users/{user_id}/posts/{post_id}", "/users/123/posts/456"
    )
    assert variables == {'user_id': '123', 'post_id': '456'}



@pytest.mark.asyncio
async def test_antpathmatcher_path_separator():

    # Create a matcher with custom path separator
    # Useful for matching things like Java package names
    matcher = AntPathMatcher(path_separator=".")

    # Now the patterns use dots as separators
    assert matcher.match("com.example.*.service", "com.example.user.service") is True
    assert matcher.match("com.example.???.service", "com.example.api.service") is True
    assert matcher.match("com.**.service", "com.example.module.api.service")  is True


@pytest.mark.asyncio
async def test_antpathmatcher_web_routing():


    # In a web framework context
    routes = {
        "/api/users/{user_id}": "get_user_handler",
        "/api/users/{user_id}/posts/{post_id}": "get_user_post_handler",
        "/api/products/**": "product_handler"
    }

    def route_request(path):
        matcher = AntPathMatcher()
        for route_pattern, handler in routes.items():
            if matcher.match(route_pattern, path):
                variables = matcher.extract_uri_template_variables(route_pattern, path)
                return handler, variables
        return "not_found_handler", {}

    # Examples
    handler, vars = route_request("/api/users/123")
    assert handler == "get_user_handler"
    assert vars == {"user_id": "123"}

    handler, vars = route_request("/api/users/456/posts/789")
    assert handler == "get_user_post_handler"
    assert vars == {"user_id": "456", "post_id": "789"}

    handler, vars = route_request("/api/products/electronics/phones")
    assert handler == "product_handler"
    assert vars == {}
