"""Deploy hook auth and happy path."""

from __future__ import annotations

from unittest.mock import patch

from tests import BlogTestCase


class DeployHookTests(BlogTestCase):
    def test_deploy_unauthorized(self) -> None:
        response = self.client.post("/internal/deploy")
        self.assertEqual(response.status_code, 401)

    def test_deploy_wrong_token(self) -> None:
        response = self.client.post(
            "/internal/deploy",
            headers={"Authorization": "Bearer wrong"},
        )
        self.assertEqual(response.status_code, 401)

    def test_deploy_disabled_without_secret(self) -> None:
        self.app.config["DEPLOY_SECRET"] = ""
        response = self.client.post(
            "/internal/deploy",
            headers={"Authorization": "Bearer test-deploy-token"},
        )
        self.assertEqual(response.status_code, 404)

    @patch("app.deploy.run_deploy")
    def test_deploy_ok(self, mock_run) -> None:
        mock_run.return_value = (True, [{"cmd": ["git"], "returncode": 0}])
        response = self.client.post(
            "/internal/deploy",
            headers={"Authorization": "Bearer test-deploy-token"},
        )
        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertTrue(payload["ok"])
        mock_run.assert_called_once()

    @patch("app.deploy.run_deploy")
    def test_deploy_failure(self, mock_run) -> None:
        mock_run.return_value = (
            False,
            [{"cmd": ["git"], "returncode": 1, "stderr": "fail"}],
        )
        response = self.client.post(
            "/internal/deploy",
            headers={"Authorization": "Bearer test-deploy-token"},
        )
        self.assertEqual(response.status_code, 500)
        self.assertFalse(response.get_json()["ok"])
