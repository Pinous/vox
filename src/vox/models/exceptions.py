class VoxError(Exception):
    pass


class ValidationError(VoxError):
    pass


class DependencyError(VoxError):
    pass


class DownloadError(VoxError):
    pass


class AudioCleaningError(VoxError):
    pass


class TranscriptionError(VoxError):
    pass


class ConfigError(VoxError):
    pass
