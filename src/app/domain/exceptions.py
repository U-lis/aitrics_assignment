class DomainError(Exception):
    """Base exception for domain errors."""

    pass


class OptimisticLockError(DomainError):
    """Raised when optimistic locking fails (version mismatch)."""

    pass


class PatientNotFoundError(DomainError):
    """Raised when a patient is not found."""

    pass


class VitalNotFoundError(DomainError):
    """Raised when a vital record is not found."""

    pass


class InvalidTokenError(DomainError):
    """Raised when token validation fails."""

    pass


class DuplicatePatientIdError(DomainError):
    """Raised when patient_id already exists."""

    pass
