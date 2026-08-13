"""
Unit tests for Automated S3 / GCS Match Replay Video Cloud Backup Module
"""

import pytest

from ai_drs.enterprise.cloud_backup import CloudBackupResult, CloudStorageBackupEngine


def test_cloud_backup_engine():
    res = CloudStorageBackupEngine.backup_match_assets("M_CLOUD_101", "report_match_101.pdf")

    assert isinstance(res, CloudBackupResult)
    assert res.match_id == "M_CLOUD_101"
    assert "s3://ai-drs-cloud-archive" in res.remote_uri
    assert res.is_backup_successful is True
