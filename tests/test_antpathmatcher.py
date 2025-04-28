import pytest
import logging

from antpathmatcher import AntPathMatcher

# For console output
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)


@pytest.mark.asyncio
async def test_antpathmatcher_match_stackoverflow():
    """
    Some examples found in StackOverflow.
    https://stackoverflow.com/questions/2952196/ant-path-style-patterns

    com/t?st.jsp - matches com/test.jsp but also com/tast.jsp or com/txst.jsp
    com/*.jsp - matches all .jsp files in the com directory
    com/**/test.jsp - matches all test.jsp files underneath the com path
    org/springframework/**/*.jsp - matches all .jsp files underneath the org/springframework path
    org/**/servlet/bla.jsp - matches org/springframework/servlet/bla.jsp but also org/springframework/testing/servlet/bla.jsp and org/servlet/bla.jsp
    com/{filename:\\w+}.jsp will match com/test.jsp and assign the value test to the filename variable
    """

    antpathmatcher = AntPathMatcher()
    assert antpathmatcher.match(pattern="com/t?st.jsp", path="com/test.jsp") is True
    assert antpathmatcher.match(pattern="com/t?st.jsp", path="com/tast.jsp") is True
    assert antpathmatcher.match(pattern="com/t?st.jsp", path="com/txst.jsp") is True

    assert antpathmatcher.match(pattern="com/*.jsp", path="com/demo.jsp") is True

    assert (
        antpathmatcher.match(pattern="com/**/test.jsp", path="com/sample/test.jsp")
        is True
    )

    assert (
        antpathmatcher.match(
            pattern="org/springframework/**/*.jsp",
            path="org/springframework/demo/demo/test.jsp",
        )
        is True
    )

    assert (
        antpathmatcher.match(
            pattern="org/**/servlet/bla.jsp", path="org/springframework/servlet/bla.jsp"
        )
        is True
    )
    assert (
        antpathmatcher.match(
            pattern="org/**/servlet/bla.jsp",
            path="org/springframework/testing/servlet/bla.jsp",
        )
        is True
    )
    assert (
        antpathmatcher.match(
            pattern="org/**/servlet/bla.jsp", path="org/servlet/bla.jsp"
        )
        is True
    )

    # Not managed
    # assert antpathmatcher.match(pattern="com/{filename:\\w+}.jsp", path="com/test.jsp") is True


@pytest.mark.asyncio
async def test_antpathmatcher_match_mach_II():
    antpathmatcher = AntPathMatcher()

    pattern_and_paths = {
        "/views/products/**/*.cfm": {
            "valid_paths": {
                "/views/products/index.cfm",
                "/views/products/SE10/index.cfm",
                "/views/products/SE10/details.cfm",
                "/views/products/ST80/index.cfm",
                "/views/products/ST80/details.cfm",
            },
            "invalid_paths": {
                "/views/index.cfm",
                "/views/aboutUs/index.cfm",
                "/views/aboutUs/managementTeam.cfm",
            },
        },
        "/views/**/*.cfm": {
            "valid_paths": {
                "/views/index.cfm",
                "/views/aboutUs/index.cfm",
                "/views/aboutUs/managementTeam.cfm",
                "/views/products/index.cfm",
                "/views/products/SE10/index.cfm",
                "/views/products/SE10/details.cfm",
                "/views/products/ST80/index.cfm",
                "/views/products/ST80/details.cfm",
            },
            "invalid_paths": {"/views/index.htm", "/views/readme.txt"},
        },
        "/views/index??.cfm": {
            "valid_paths": {
                "/views/index01.cfm",
                "/views/index02.cfm",
                "/views/indexAA.cfm",
            },
            "invalid_paths": {
                "/views/index01.htm",
                "/views/index1.cfm",
                "/views/indexA.cfm",
                "/views/indexOther.cfm",
                "/views/anotherDir/index01.cfm",
            },
        },
    }

    for pattern in pattern_and_paths:
        for valid_paths in pattern_and_paths[pattern]["valid_paths"]:
            assert antpathmatcher.match(pattern=pattern, path=valid_paths) is True
        for valid_paths in pattern_and_paths[pattern]["invalid_paths"]:
            assert antpathmatcher.match(pattern=pattern, path=valid_paths) is False



@pytest.mark.asyncio
async def test_antpathmatcher_match():
    antpathmatcher = AntPathMatcher()
    assert antpathmatcher.match(pattern="com/t?st.jsp", path="com/test.jsp") is True
    assert antpathmatcher.match(pattern="com/t?st.jsp", path="com/tast.jsp") is True
    assert antpathmatcher.match(pattern="com/t?st.jsp", path="com/txst.jsp") is True

    assert antpathmatcher.match(pattern="com/t?st.jsp", path="com/tst.jsp") is False
    assert antpathmatcher.match(pattern="com/t?st.jsp", path="com/taast.jsp") is False
    assert antpathmatcher.match(pattern="com/t?st.jsp", path="com/t/st.jsp") is False


@pytest.mark.asyncio
async def test_antpathmatcher_match_custom_path_separator():
    antpathmatcher = AntPathMatcher(path_separator=".")
    assert antpathmatcher.match(pattern="com/t?st.jsp", path="com/test.jsp") is True

    assert antpathmatcher.match(pattern="com/t?st.jsp", path="com/test.jsp") is True
    assert antpathmatcher.match(pattern="com/t?st.jsp", path="com/tast.jsp") is True
    assert antpathmatcher.match(pattern="com/t?st.jsp", path="com/txst.jsp") is True

    assert antpathmatcher.match(pattern="com.t?st/jsp", path="com.tst/jsp") is False
    assert antpathmatcher.match(pattern="com.t?st/jsp", path="com.taast/jsp") is False
    assert antpathmatcher.match(pattern="com.t?st/jsp", path="com.t.st/jsp") is False


@pytest.mark.asyncio
async def test_antpathmatcher_extract_uri_template_variables():
    antpathmatcher = AntPathMatcher()
    assert antpathmatcher.extract_uri_template_variables(
        pattern="/hotels/{hotel}", path="/hotels/1"
    ) == {"hotel": "1"}
    assert antpathmatcher.extract_uri_template_variables(
        pattern="/users/{user_id}/posts/{post_id}", path="/users/123/posts/456"
    ) == {"user_id": "123", "post_id": "456"}
