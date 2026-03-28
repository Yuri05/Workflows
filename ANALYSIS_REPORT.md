# GitHub Actions Version Analysis Report

**Date:** 2026-03-28
**Repository:** Open-Systems-Pharmacology/Workflows
**Branch:** main

## Summary

Analyzed **24 workflow files** and **11 action files** in the repository.

**Result:** Found **16 files** with outdated GitHub Actions that should be updated.

## Files with Outdated Actions

### Workflows (15 files)

1. **`.github/workflows/pkgdown-rClr.yml`**
   - actions/checkout@v5 → v6 (1 occurrence)
   - actions/download-artifact@v1 → v8 (1 occurrence)
   - actions/upload-artifact@v1 → v7 (1 occurrence)

2. **`.github/workflows/QualificationPlan_ModelVersionCheck.yml`**
   - actions/checkout@v5 → v6 (1 occurrence)
   - actions/setup-python@v4 → v6 (1 occurrence)

3. **`.github/workflows/test-coverage-rClr.yml`**
   - actions/upload-artifact@v3 → v7 (1 occurrence)

4. **`.github/workflows/Check_CSV.yml`**
   - actions/checkout@v5 → v6 (1 occurrence)

5. **`.github/workflows/ValidateActions.yml`**
   - actions/checkout@v5 → v6 (1 occurrence)
   - asdf-vm/actions@v3 → v4 (1 occurrence)

6. **`.github/workflows/R-CMD-check-build-rClr.yml`**
   - actions/upload-artifact@v3 → v7 (1 occurrence)

7. **`.github/workflows/Check_BOM.yml`**
   - actions/checkout@v5 → v6 (1 occurrence)

8. **`.github/workflows/CreateGitHubPagesForR.yml`**
   - actions/checkout@v5 → v6 (2 occurrences)
   - actions/download-artifact@v1 → v8 (1 occurrence)
   - actions/upload-artifact@v1 → v7 (1 occurrence)

9. **`.github/workflows/latest-artifact.yml`**
   - octokit/request-action@v2 → v3 (2 occurrences)

10. **`.github/workflows/GitHub_CodeQL.yml`**
    - actions/checkout@v5 → v6 (1 occurrence)

11. **`.github/workflows/test-csharp.yml`**
    - actions/checkout@v5 → v6 (1 occurrence)

12. **`.github/workflows/Check_URLs.yml`**
    - actions/checkout@v5 → v6 (1 occurrence)

13. **`.github/workflows/R-CMD-check-build.yaml`**
    - actions/upload-artifact@v4 → v7 (1 occurrence)

14. **`.github/workflows/bump_dev_version_tag_branch.yaml`**
    - tj-actions/changed-files@v45 → v47 (1 occurrence)

15. **`.github/workflows/test-coverage.yaml`**
    - actions/upload-artifact@v4 → v7 (1 occurrence)

### Actions (1 file)

1. **`.github/actions/report-evaluation/action.yaml`**
   - actions/upload-artifact@v4 → v7 (1 occurrence)

## Issues Created

✅ **All 16 GitHub issues have been successfully created!**

Issues #186-#201 were created in the Open-Systems-Pharmacology/Workflows repository:

- Issue #186: .github/workflows/pkgdown-rClr.yml
- Issue #187: .github/workflows/QualificationPlan_ModelVersionCheck.yml
- Issue #188: .github/workflows/test-coverage-rClr.yml
- Issue #189: .github/workflows/Check_CSV.yml
- Issue #190: .github/workflows/ValidateActions.yml
- Issue #191: .github/workflows/R-CMD-check-build-rClr.yml
- Issue #192: .github/workflows/Check_BOM.yml
- Issue #193: .github/workflows/CreateGitHubPagesForR.yml
- Issue #194: .github/workflows/latest-artifact.yml
- Issue #195: .github/workflows/GitHub_CodeQL.yml
- Issue #196: .github/workflows/test-csharp.yml
- Issue #197: .github/workflows/Check_URLs.yml
- Issue #198: .github/workflows/R-CMD-check-build.yaml
- Issue #199: .github/workflows/bump_dev_version_tag_branch.yaml
- Issue #200: .github/workflows/test-coverage.yaml
- Issue #201: .github/actions/report-evaluation/action.yaml

View all issues at: https://github.com/Open-Systems-Pharmacology/Workflows/issues

## Most Common Updates Needed

- **actions/checkout**: v5 → v6 (9 files)
- **actions/upload-artifact**: v1/v3/v4 → v7 (7 files)
- **actions/download-artifact**: v1 → v8 (2 files)
- **actions/setup-python**: v4 → v6 (1 file)
- **asdf-vm/actions**: v3 → v4 (1 file)
- **octokit/request-action**: v2 → v3 (1 file)
- **tj-actions/changed-files**: v45 → v47 (1 file)
