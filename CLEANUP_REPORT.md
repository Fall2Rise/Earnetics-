# 🧹 Repository Hygiene Report: Earnetics Project

**Status:** Dry Run (No files deleted yet)
**Date:** 2026-02-03
**Objective:** Clean up junk while preserving system integrity.

---

## 🚨 CRITICAL SECURITY FINDINGS
**Action Required Immediately:**
The following files contain **PRIVATE KEYS** and are currently in the root directory. They should be moved to a secure location (e.g., `secrets/`) which is already ignored by `.gitignore`.

*   [ ] `fallat-crewai-3a42545ac039.json` (Google Service Account)
*   [ ] `google_service_account.json` (Google Service Account)

**Recommendation:** Move these to `secrets/` immediately.

---

## 1️⃣ SAFE TO DELETE
These files are identified as temporary scripts, logs, debug output, or abandoned artifacts. They serve no runtime purpose for the active system.

### Debug & Diagnostic Scripts
*   `_extract_activities.py`
*   `agent_activity_diagnostic.py`
*   `agent_activity_diagnostic_v2.py`
*   `analyze_keywords.py`
*   `check_env.py`
*   `check_env_content.py`
*   `check_system.py`
*   `debug_email.py`
*   `debug_import.py`
*   `debug_stripe.py`
*   `dump_daily.py`
*   `dump_pd.py`
*   `dump_pd_repr.py`
*   `fetch_article.py`
*   `fetch_trends.py`
*   `find_key.py`
*   `fix_env.py`
*   `inspect_script.py`
*   `inspect_topics.py`
*   `list_google_models.py`
*   `list_products.py`
*   `parse_daily.py`
*   `parse_topics.py`
*   `read_log.py`
*   `verify_config.py`
*   `verify_env.py`
*   `verify_moviepy.py`
*   `verify_providers.py`
*   `verify_stripe.py`

### Logs & Output Artifacts
*   `audit_results.txt`
*   `db_check_output.txt`
*   `diagnostic_results.md`
*   `diagnostic_results.txt`
*   `diagnostic_results_internal.txt`
*   `email_debug_log.md`
*   `email_debug_log_2.md`
*   `email_debug_log_2_utf8.md`
*   `email_debug_log_utf8.md`
*   `pd_repr.txt`
*   `pd_repr_utf8.txt`
*   `restore_log.md`
*   `secrets_report.txt`
*   `server_debug_log.md`
*   `stripe_products.txt`
*   `stripe_products_list.txt`
*   `system_check_final.txt`
*   `SYSTEM_DIAGNOSIS.md`
*   `tree.txt`
*   `venv_files.txt`
*   `verification_result.md`
*   `helpers_block.txt`

### Miscellaneous Junk
*   `Frontend/Uploads/` (Contains screenshots)
*   `backup/` (Contains `main_server_old.py` and `requirements_old.txt`)
*   `KALI LIVE/` (Boot image artifacts)
*   `.aider*` files (Chat history)

---

## 2️⃣ MOVE OR CONSOLIDATE
These directories contain code that is **imported** by the active backend but structurally separated. Deleting them will break the system.

*   `earnetics/` (Referenced by `backend/api/intelligence_router.py`)
*   `earnetics_crm/` (Likely used as a module)
*   `head_office/` (Referenced by `backend/main_server.py`)

**Recommendation:** Do not delete. In a future architectural pass, these should be consolidated into the `backend/` directory to create a unified monorepo structure.

---

## 3️⃣ KEEP (DO NOT TOUCH)
These are the core pillars of the application.

*   `backend/` (The active Python API)
*   `fallat_crewai_dashboard/` (The active React Frontend)
*   `autonomous/` (Worker agents)
*   `config/` (YAML configurations)
*   `deployment/` (Docker/Nginx configs)
*   `scripts/` (Operational tools like `run_all.ps1`)
*   `static/` & `templates/` (Web assets)
*   `tests/` (Test suite)

---

## 4️⃣ UNCERTAIN / REVIEW REQUIRED
*   `builder/tasks/` (Contains JSON task definitions. Keep until usage is verified.)
*   `assets/` (Contains `earnetics.ico` and `shop.css`. Keep as likely used by templates.)

---

## 🏁 Execution Plan
1.  **Move Secrets:** I will move the 2 JSON key files to `secrets/`.
2.  **Delete Junk:** I will delete all files listed in "Safe to Delete".
3.  **Preserve Rest:** All other files will remain untouched.

**Awaiting your approval to proceed.**
