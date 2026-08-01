-- Disk monitoring for PA module: checkbox + quota MiB from Admin form.
-- Public PA API has no disk endpoint; usage is measured on-host via du when possible.
PRAGMA foreign_keys = ON;

ALTER TABLE pa_module_settings ADD COLUMN monitor_disk INTEGER NOT NULL DEFAULT 0;
ALTER TABLE pa_module_settings ADD COLUMN disk_quota_mib INTEGER NOT NULL DEFAULT 512;
