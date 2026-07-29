# Company Config

Fill this in once and every work order carries your branding. Colors are hex
without the #. Everything else in the package derives from these lines —
see `examples/resilient-retrofits/company.md` for a filled-in real example.

- company_name: Your Company Name
- license_line: License # 000000
- prepared_by: Your Name
- crew_contact: Your Name — (555) 555-0100
- logo: ../assets/logo-placeholder.png
- color_primary: 1F4E79
- color_accent: 6E8FAF
- vent_ratio: 300
- qa_label: QA
- checklist_dirs: ../checklists

# Notes
# - logo: path relative to THIS file. Leave blank to render a text wordmark
#   banner instead — the package works with no logo at all.
# - color_primary is the banner/heading color; color_accent drives table
#   borders and row tints (they're derived automatically, always harmonious).
# - vent_ratio: your attic net-free-area ventilation standard (1:300 here).
#   Check your local code — the lint flags any doc that drifts from this.
# - qa_label prefixes quality-checklist titles ("QA — Attic Insulation").
#   Companies under a program inspector can rename it (see the example).
# - checklist_dirs: comma-separated, relative to this file. Later directories
#   override earlier ones by checklist key — that's how program overlays work.
