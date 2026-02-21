import enum


class QualityFlag(str, enum.Enum):
    OK = 'OK'
    CLOUDY = 'CLOUDY'
    NO_DATA = 'NO_DATA'


class RecommendationType(str, enum.Enum):
    GRAZE_NOW = 'GRAZE_NOW'
    AVOID_WATERLOG = 'AVOID_WATERLOG'
    MONITOR_STRESS = 'MONITOR_STRESS'
    LOW_DATA = 'LOW_DATA'


class Severity(str, enum.Enum):
    info = 'info'
    warning = 'warning'


class JobStatus(str, enum.Enum):
    running = 'running'
    success = 'success'
    failed = 'failed'


class JobType(str, enum.Enum):
    ingest_satellite = 'ingest_satellite'
    compute_ndvi = 'compute_ndvi'
    aggregate_ndvi = 'aggregate_ndvi'
    fetch_weather = 'fetch_weather'
    generate_recommendations = 'generate_recommendations'
    cleanup_artifacts = 'cleanup_artifacts'
