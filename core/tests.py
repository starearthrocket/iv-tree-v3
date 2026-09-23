from django.test import RequestFactory, TestCase, override_settings

from core.views import custom_500


class ErrorPageTests(TestCase):
    """Tests for custom production error pages."""

    @override_settings(DEBUG=False)
    def test_custom_404_page(self):
        """An unknown URL should return the branded 404 page."""

        response = self.client.get(
            '/this-page-does-not-exist/',
        )

        self.assertEqual(
            response.status_code,
            404,
        )
        self.assertTemplateUsed(
            response,
            'errors/404.html',
        )
        self.assertContains(
            response,
            'This path has gone a little wild.',
            status_code=404,
        )

    def test_custom_500_page(self):
        """The custom server-error view should return HTTP 500."""

        request = RequestFactory().get('/')
        response = custom_500(request)

        self.assertEqual(
            response.status_code,
            500,
        )
        self.assertContains(
            response,
            'Something went wrong.',
            status_code=500,
        )