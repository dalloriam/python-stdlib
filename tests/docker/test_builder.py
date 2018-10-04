from dalloriam.docker import builder

from tests.mocks.location import mock_location

from unittest import mock


def test_builder_calls_shell_run_properly():
    with mock.patch.object(builder.filesystem, 'location', mock_location), mock.patch.object(builder.shell, 'run') as mock_run:
        builder.build('some_path', 'my_image', 'mytag')
        mock_run.assert_called_once()

        mock_run.assert_called_with(['docker', 'build', '-t', 'my_image:mytag', '.'], silent=True)


def test_builder_sets_default_tag():
    with mock.patch.object(builder.filesystem, 'location', mock_location), mock.patch.object(builder.shell, 'run') as mock_run:
        builder.build('some_path', 'my_image')
        mock_run.assert_called_once()

        mock_run.assert_called_with(['docker', 'build', '-t', 'my_image:latest', '.'], silent=True)
