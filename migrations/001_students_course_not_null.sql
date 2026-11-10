-- Migration 001: align students.course with the application model.
--
-- The live database already has a students.course column, but it was created
-- as nullable while the API requires a course for every student.
--
-- This migration is intentionally non-destructive:
--   * It does not drop or recreate the table.
--   * It does not delete rows.
--   * If any existing row has a NULL course, SET NOT NULL fails safely and the
--     transaction rolls back. Resolve those rows manually, then re-run.
--
-- Run with:
--   psql "$DATABASE_URL" -f migrations/001_students_course_not_null.sql

BEGIN;

ALTER TABLE students
    ALTER COLUMN course SET NOT NULL;

COMMIT;
