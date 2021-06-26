import urllib

from zerver.lib.test_classes import WebhookTestCase


class TravisHookTests(WebhookTestCase):
    STREAM_NAME = "travis"
    URL_TEMPLATE = "/api/v1/external/travis?stream={stream}&api_key={api_key}"
    WEBHOOK_DIR_NAME = "travis"
    TOPIC = "builds"
    EXPECTED_MESSAGE = """
Author: josh_mandel
Build status: Passed :thumbs_up:
Details: [changes](https://github.com/hl7-fhir/fhir-svn/compare/6dccb98bcfd9...6c457d366a31), [build log](https://travis-ci.org/hl7-fhir/fhir-svn/builds/92495257)
""".strip()

    def test_travis_message(self) -> None:
        """
        Build notifications are generated by Travis after build completes.

        The subject describes the repo and Stash "project". The
        content describes the commits pushed.
        """

        self.check_webhook(
            "build",
            self.TOPIC,
            self.EXPECTED_MESSAGE,
            content_type="application/x-www-form-urlencoded",
        )

    def test_ignore_travis_pull_request_by_default(self) -> None:
        self.subscribe(self.test_user, self.STREAM_NAME)
        result = self.client_post(
            self.url,
            self.get_body("pull_request"),
            content_type="application/x-www-form-urlencoded",
        )
        self.assert_json_success(result)
        msg = self.get_last_message()
        self.assertNotEqual(msg.topic_name(), self.TOPIC)

    def test_travis_pull_requests_are_not_ignored_when_applicable(self) -> None:
        self.url = f"{self.build_webhook_url()}&ignore_pull_requests=false"

        self.check_webhook(
            "pull_request",
            self.TOPIC,
            self.EXPECTED_MESSAGE,
            content_type="application/x-www-form-urlencoded",
        )

    def get_body(self, fixture_name: str) -> str:
        return urllib.parse.urlencode(
            {"payload": self.webhook_fixture_data("travis", fixture_name, file_type="json")}
        )
